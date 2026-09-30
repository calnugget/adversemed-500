"""Enable `python -m generator` (installed as `python -m adversemed_gen` via console-script).

This module simply dispatches to `generator.cli.main` so both the installed
CLI entry point and `python -m ...` invocations share the same code path.
"""
from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
