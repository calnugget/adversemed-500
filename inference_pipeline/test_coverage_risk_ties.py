"""Regression tests for the coverage-risk tie convention.

Background. `coverage_risk_curve` originally did `sorted(zip(confidences, correct),
key=lambda x: -x[0])`. Python's sort is stable, so equal-confidence rows kept their
input order and the resulting AURC / Risk@90 depended on the order of the JSONL.
Self-consistency confidence takes only 3--4 distinct values over 500 items, so almost
every pair was a tie: six row shuffles moved Claude Haiku 4.5's self-consistency AURC
across 0.1310--0.1708 against a published 0.1468, and DeepSeek-Chat's across
0.1715--0.2220 against 0.2016.

These tests pin the fix: the curve is now built by grouping on confidence and
distributing each group's errors uniformly across its positions, so AURC and Risk@90
are functions of the multiset of (confidence, correct) pairs alone.

Run standalone (no pytest needed):
    python3 -m _pipeline.test_coverage_risk_ties
or under pytest:
    python3 -m pytest _pipeline/test_coverage_risk_ties.py
"""
from __future__ import annotations

import random
from pathlib import Path

try:  # repository layout
    from _pipeline.analyze import (
        aurc,
        coverage_risk_curve,
        load_inference_jsonl,
        risk_at_coverage,
        _valid_confidence_rows,
    )
except ModuleNotFoundError:  # released-archive layout, where the package is `inference_pipeline`
    import sys

    _here = Path(__file__).resolve().parent
    sys.path.insert(0, str(_here.parent))
    _analyze = __import__(f"{_here.name}.analyze", fromlist=["*"])
    aurc = _analyze.aurc
    coverage_risk_curve = _analyze.coverage_risk_curve
    load_inference_jsonl = _analyze.load_inference_jsonl
    risk_at_coverage = _analyze.risk_at_coverage
    _valid_confidence_rows = _analyze._valid_confidence_rows

_REPO = Path(__file__).resolve().parent.parent
_RUN_DIR = _REPO / "inference_outputs" / "adversemed_500_final"


def _metrics(pairs, tie_handling="average"):
    covs, risks = coverage_risk_curve(
        [c for c, _ in pairs], [y for _, y in pairs], tie_handling
    )
    return aurc(covs, risks), risk_at_coverage(covs, risks, 0.90)


def test_shuffle_invariance_synthetic():
    """A heavily tied synthetic run: AURC and Risk@90 must not move under shuffling."""
    rng = random.Random(20260706)
    pairs = [(rng.choice([0.4, 0.6, 0.8, 1.0]), rng.random() < 0.8) for _ in range(500)]
    ref = _metrics(pairs)
    for seed in range(25):
        shuffled = pairs[:]
        random.Random(seed).shuffle(shuffled)
        got = _metrics(shuffled)
        assert abs(got[0] - ref[0]) < 1e-12, f"AURC moved under shuffle {seed}: {got[0]} vs {ref[0]}"
        assert abs(got[1] - ref[1]) < 1e-12, f"Risk@90 moved under shuffle {seed}: {got[1]} vs {ref[1]}"


def test_shuffle_invariance_real_runs():
    """Same guarantee on every real (model x method) run that has usable confidences.

    Skipped rather than failed if the inference logs are not present locally; they
    live in the Zenodo archive, not the git repository.
    """
    if not _RUN_DIR.is_dir():
        print(f"  [skip] {_RUN_DIR} not present")
        return
    checked = 0
    for path in sorted(_RUN_DIR.glob("*.jsonl")):
        rows = _valid_confidence_rows(load_inference_jsonl(path))
        if len(rows) < 2:
            continue
        pairs = [(float(r["confidence"]), bool(r.get("correct"))) for r in rows]
        ref = _metrics(pairs)
        for seed in range(6):
            shuffled = pairs[:]
            random.Random(seed).shuffle(shuffled)
            got = _metrics(shuffled)
            assert abs(got[0] - ref[0]) < 1e-12, f"{path.name}: AURC moved under shuffle {seed}"
            assert abs(got[1] - ref[1]) < 1e-12, f"{path.name}: Risk@90 moved under shuffle {seed}"
        checked += 1
    assert checked >= 17, f"coverage guard: only {checked} runs checked, expected >= 17"
    print(f"  [ok] {checked} real runs shuffle-invariant")


def test_average_convention_is_the_mean_over_tie_orderings():
    """The averaging convention equals the expectation over random tie orderings.

    Risk at every position is linear in the cumulative error count, and AURC is linear
    in the risks, so the curve built from per-group averages has exactly the AURC that
    averaging over all within-group permutations would give. Checked against a
    Monte-Carlo mean of the old order-dependent computation.
    """
    rng = random.Random(7)
    pairs = [(rng.choice([0.5, 0.75, 1.0]), rng.random() < 0.7) for _ in range(300)]
    exact, _ = _metrics(pairs)

    # Monte-Carlo the old behaviour: stable sort over a shuffled input.
    total = 0.0
    trials = 400
    for seed in range(trials):
        shuffled = pairs[:]
        random.Random(seed).shuffle(shuffled)
        ordered = sorted(shuffled, key=lambda x: -x[0])  # stable: ties keep row order
        n = len(ordered)
        cum = 0
        covs, risks = [], []
        for i, (_, y) in enumerate(ordered, start=1):
            if not y:
                cum += 1
            covs.append(i / n)
            risks.append(cum / i)
        total += aurc(covs, risks)
    mc = total / trials
    assert abs(mc - exact) < 2e-3, f"average convention {exact} far from MC mean {mc}"


def test_envelope_brackets_the_reported_value():
    rng = random.Random(11)
    pairs = [(rng.choice([0.4, 0.6, 0.8, 1.0]), rng.random() < 0.8) for _ in range(500)]
    avg, avg_r90 = _metrics(pairs, "average")
    lo, lo_r90 = _metrics(pairs, "optimistic")
    hi, hi_r90 = _metrics(pairs, "pessimistic")
    assert lo <= avg <= hi, f"AURC envelope violated: {lo} <= {avg} <= {hi}"
    assert lo_r90 <= avg_r90 <= hi_r90, f"Risk@90 envelope violated: {lo_r90} <= {avg_r90} <= {hi_r90}"


def test_no_ties_matches_the_naive_computation():
    """With all-distinct confidences the new code must reproduce the old numbers exactly."""
    rng = random.Random(3)
    pairs = [(i / 400.0, rng.random() < 0.6) for i in range(1, 401)]
    covs, risks = coverage_risk_curve([c for c, _ in pairs], [y for _, y in pairs])

    ordered = sorted(pairs, key=lambda x: -x[0])
    n = len(ordered)
    cum = 0
    naive_risks = []
    for i, (_, y) in enumerate(ordered, start=1):
        if not y:
            cum += 1
        naive_risks.append(cum / i)
    assert len(risks) == len(naive_risks)
    for a, b in zip(risks, naive_risks):
        assert abs(a - b) < 1e-12


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            print(f"{name} ...")
            fn()
            print(f"{name} PASSED")
    print("\nall coverage-risk tie tests passed")
