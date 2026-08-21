# Publishing `adversemed-gen` to PyPI

This document is for Dyuthi (repo owner). It walks through the **first-ever
publish** of `adversemed-gen` to PyPI, plus how automated publishes work
after the initial upload.

> **Security warning**: PyPI API tokens grant upload rights. **Never commit
> a token to the repo**, never paste it in an issue/PR, and never share a
> screenshot that shows the token. Store it in the OS keychain or in the
> GitHub `PYPI_API_TOKEN` secret — nowhere else. If you accidentally paste
> one anywhere, revoke it immediately at
> https://pypi.org/manage/account/token/.

## One-time setup

1. **Create a PyPI account**
   - Sign up at https://pypi.org/account/register/ using
     `28dyuthiv@students.harker.org`.
   - Enable 2FA (required for uploads since 2024). Store recovery codes in
     your password manager.

2. **Reserve the project name via a manual first upload**
   PyPI creates the project record on first upload. Do this from your
   laptop, one time:

   ```bash
   # a) Install build tooling in a scratch venv (do NOT reuse a project venv)
   python3.11 -m venv ~/.venvs/pypi-tools
   source ~/.venvs/pypi-tools/bin/activate
   pip install --upgrade build twine

   # b) From the repo root
   cd /path/to/adversemed-500
   git clean -fdx dist/ build/ *.egg-info    # clean any stale artifacts
   python -m build                            # -> dist/adversemed_gen-0.1.0.tar.gz + .whl
   twine check dist/*                         # sanity-check metadata

   # c) Upload (twine will prompt for username/password; use __token__ +
   #    your API token as the "password")
   twine upload dist/*
   ```

   You'll be asked:
   - **Username**: `__token__` (literally that string)
   - **Password**: your PyPI API token (starts with `pypi-`).

   The token can be a "unscoped" account-level token for the first upload,
   because the `adversemed-gen` project doesn't exist yet.

3. **Create a project-scoped token**
   Once the first upload succeeds and `pypi.org/project/adversemed-gen/`
   exists, replace the account-level token with a **project-scoped** one:

   - Go to https://pypi.org/manage/account/token/
   - Click "Add API token"
   - Token name: `adversemed-gen-github-actions`
   - Scope: **Project: adversemed-gen** (not "Entire account")
   - Copy the token (starts with `pypi-`), you will NOT see it again.

4. **Store the token as a GitHub Actions secret**
   - Go to https://github.com/calnugget/adversemed-500/settings/secrets/actions
   - Click "New repository secret"
   - Name: `PYPI_API_TOKEN`
   - Value: paste the token
   - Save.

5. **(Optional) Set up the `pypi` environment for stricter approvals**
   In the same GitHub settings page, go to "Environments" -> "New
   environment" -> name it `pypi`. You can require yourself as a manual
   approver here if you want a click-to-approve step before every publish.

## Publishing subsequent releases (automated)

Once setup is done, every new release is one command:

```bash
# 1. Bump the version in pyproject.toml AND generator/__init__.py
#    (both list "0.1.0"; keep them in sync).
# 2. Commit the version bump.
git add pyproject.toml generator/__init__.py
git commit -m "Bump adversemed-gen to 0.1.1"

# 3. Tag with the pypi-v prefix and push.
git tag pypi-v0.1.1
git push origin main --tags
```

The `.github/workflows/publish-pypi.yml` workflow will fire on the
`pypi-v*` tag, build the sdist + wheel, and upload them to PyPI using
the stored token.

## Manual publish (fallback, if Actions is broken)

If you ever need to publish without GitHub Actions:

```bash
source ~/.venvs/pypi-tools/bin/activate
cd /path/to/adversemed-500
git clean -fdx dist/ build/ *.egg-info
python -m build
twine check dist/*
twine upload dist/*   # will prompt for the token
```

## Verifying the publish worked

- Check https://pypi.org/project/adversemed-gen/ shows the new version.
- Test-install in a scratch venv:
  ```bash
  python3.11 -m venv /tmp/test-install
  /tmp/test-install/bin/pip install adversemed-gen==0.1.1
  /tmp/test-install/bin/adversemed-gen --help
  ```

## Yanking a broken release

If a release turns out to be broken:

```bash
# On pypi.org: navigate to the release, click "Options" -> "Yank release".
# Yanking hides it from `pip install adversemed-gen` (users get the previous
# version) but keeps it installable if pinned to that exact version.
# Do NOT delete releases unless legally required — deletion breaks caches.
```

## Version scheme

- `0.1.x` — alpha; API may change without notice.
- `0.y.0` — beta; API changes announced in CHANGELOG.
- `1.0.0` — first stable release; semver applies from here.

Keep `pyproject.toml` `version` and `generator/__init__.py` `__version__` in
sync — mismatches will trip up downstream tooling.
