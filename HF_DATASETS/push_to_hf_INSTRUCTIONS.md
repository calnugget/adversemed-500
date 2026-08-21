# Publishing AdverseMed-500 to Hugging Face Datasets

This document is for Dyuthi (repo owner). It walks through the **first-ever
publish** of `calnugget/adversemed-500` on the Hugging Face Hub, plus how to
push updates later.

> **Security warning**: Your HF write token grants full write access to
> every dataset/model you own. **Never commit a token**, never paste it in
> an issue or PR, and never share a screenshot showing it. If a token ever
> leaks, revoke it at https://huggingface.co/settings/tokens.

## One-time setup

1. **Create a Hugging Face account**
   - Sign up at https://huggingface.co/join using
     `28dyuthiv@students.harker.org`.
   - Set your username to `calnugget` (matches GitHub) if available;
     otherwise pick one and update the URLs in this doc + main README.
   - Enable 2FA.

2. **Create a write-scoped user access token**
   - Go to https://huggingface.co/settings/tokens
   - Click "Create new token"
   - Name: `adversemed-500-push`
   - Role: `Write`
   - Copy the token (starts with `hf_`); you will not see it again.

3. **Install the CLI locally**

   ```bash
   python3.11 -m venv ~/.venvs/hf-tools
   source ~/.venvs/hf-tools/bin/activate
   pip install --upgrade "huggingface_hub[cli]"
   ```

4. **Log in (token stays in ~/.cache/huggingface, not in the repo)**

   ```bash
   huggingface-cli login
   # Paste the token when prompted.
   # Choose 'Y' to add it to your git credential helper if you'll push via git.
   ```

## First push (create the dataset repo + upload)

From the AdverseMed-500 repo root on your laptop:

```bash
# 1. Create the dataset repo on the Hub (empty, private for the initial
#    dry-run; we'll flip to public in step 4).
huggingface-cli repo create adversemed-500 --type dataset --private

# 2. Upload the dataset card + the benchmark JSONL as a single commit.
huggingface-cli upload calnugget/adversemed-500 \
    HF_DATASETS/README.md \
    README.md \
    --repo-type dataset \
    --commit-message "Add dataset card"

huggingface-cli upload calnugget/adversemed-500 \
    benchmark/adversemed_500.jsonl \
    adversemed_500.jsonl \
    --repo-type dataset \
    --commit-message "Add AdverseMed-500 benchmark JSONL (500 items, SHA-256 26cae9e1...c586a9)"

# 3. Optional: also upload the per-question verified YAMLs so downstream
#    users can inspect references without cloning the GitHub repo.
huggingface-cli upload calnugget/adversemed-500 \
    benchmark/verified_yaml/ verified_yaml/ \
    --repo-type dataset \
    --commit-message "Add per-question verified YAML sidecars"

# 4. Sanity-check the dataset viewer at
#    https://huggingface.co/datasets/calnugget/adversemed-500 — verify
#    the 500-item preview loads, categories parse, and license shows
#    "cc-by-4.0". If it looks good, flip to public:
huggingface-cli repo visibility calnugget/adversemed-500 --type dataset public
```

## Programmatic alternative (Python)

If you'd rather script it:

```python
from huggingface_hub import HfApi, create_repo

api = HfApi()

create_repo(
    "calnugget/adversemed-500",
    repo_type="dataset",
    private=True,
    exist_ok=True,
)

api.upload_file(
    path_or_fileobj="HF_DATASETS/README.md",
    path_in_repo="README.md",
    repo_id="calnugget/adversemed-500",
    repo_type="dataset",
    commit_message="Add dataset card",
)

api.upload_file(
    path_or_fileobj="benchmark/adversemed_500.jsonl",
    path_in_repo="adversemed_500.jsonl",
    repo_id="calnugget/adversemed-500",
    repo_type="dataset",
    commit_message="Add AdverseMed-500 benchmark JSONL",
)
```

## Verifying the publish

```python
from datasets import load_dataset

ds = load_dataset("calnugget/adversemed-500", split="test")
assert len(ds) == 500
assert ds[0]["ground_truth"] == "abstain"
print("OK -", ds[0]["question"][:80])
```

Also verify SHA-256 matches the manifest:

```bash
sha256sum <(datasets-cli download calnugget/adversemed-500)
# Expected: 26cae9e190bc96a96814241ef4e0c779f2ff7de51dd811dcdb425a8af1c586a9
```

## Updating the dataset later

If you fix a card typo:

```bash
huggingface-cli upload calnugget/adversemed-500 HF_DATASETS/README.md README.md \
    --repo-type dataset \
    --commit-message "Fix typo in dataset card"
```

If you release a v2 with new items (post-paper, unlikely before publication):

- Cut a new git tag on GitHub first (e.g. `benchmark-v1.1.0`).
- Bump the version in the dataset-card YAML frontmatter and in
  `benchmark/manifest.json`.
- Upload the new JSONL under a versioned filename
  (`adversemed_v1.1.0.jsonl`) rather than overwriting `adversemed_500.jsonl`,
  so downstream users pinning to v1.0.0 continue to reproduce results.

## Removing a dataset

Don't. Once a dataset has been referenced by other papers, removing it
breaks their reproducibility. If you need to correct an item, use a new
version and clearly document the change in the README + a HF Hub commit
message. Only remove if legally required (e.g., PHI leak) — AdverseMed-500
is synthetic so this should never happen.

## Troubleshooting

- **"401 Unauthorized"**: token doesn't have write scope or expired. Re-run
  `huggingface-cli login` with a fresh Write token.
- **"Repository not found"**: you passed the wrong `--repo-type` (needs
  `dataset`, not the default `model`).
- **Dataset viewer fails to parse**: usually a YAML-frontmatter error in
  `HF_DATASETS/README.md`. Validate at
  https://huggingface.co/spaces/huggingface/datasets-viewer.
