
# gh-automations

!!! abstract "In a nutshell"
    `gh-automations` is a shared toolbox of ready-made automation recipes that every OVOS code project can borrow, instead of each one writing its own. These recipes handle the repetitive chores around publishing software — running tests, checking licences, bumping version numbers, and pushing releases out. Because the recipe lives in one place, fixing or improving it once updates every project that uses it. This is a developer/maintainer reference; see the [Workflow Reference](gh-automations-workflows.md) for the full list, or the [Glossary](glossary.md).

`gh-automations` (hosted at [OpenVoiceOS/gh-automations](https://github.com/OpenVoiceOS/gh-automations)) is the shared GitHub Actions automation library for OpenVoiceOS repositories.

## What it does, in plain terms

Instead of every OVOS repo copy-pasting its own CI/CD YAML, this repo holds a set of **reusable workflows**. Your repo's workflow file is just a few lines that *call* one of these — GitHub runs the shared definition with your inputs. Update the shared workflow once, and every repo that references it gets the change.

The workflows cover two jobs:

- **Release automation** — bump the version on PR merge to `dev`, publish an alpha to PyPI, open a release PR to `master`, then on merge declare the version stable and tag it. See [Release Flow](gh-automations-release.md).
- **PR checks** — build/install/test, plugin detection, license/CVE scanning, coverage, linting, version preview, and more. Most of these post their result as a section in a single shared **OVOS PR Checks** comment on the PR.

### How to wire one into your repo

Add a workflow file under `.github/workflows/` in your repo that calls the reusable one. The `uses:` ref is **always `@dev`** (never a pinned tag or SHA):

```yaml
# .github/workflows/build_tests.yml
name: Run Build Tests
on:
  pull_request:
    branches: [dev]
  workflow_dispatch:

jobs:
  build_tests:
    uses: OpenVoiceOS/gh-automations/.github/workflows/build-tests.yml@dev
    secrets: inherit
    with:
      install_extras: 'test'
      test_path: 'test/'
```

`secrets: inherit` passes your repo's secrets (e.g. `GITHUB_TOKEN`, and `PYPI_TOKEN`/`MATRIX_TOKEN` for the publish workflows) through to the called workflow. See [Workflow Reference](gh-automations-workflows.md) for every input.

### Scripts checkout

Several reusable workflows check this repo out again at runtime to reach `scripts/` (the PR-comment helper, version utilities, etc.), pinned to `ref: dev`. You do not write this yourself — it lives inside the reusable workflow:

```yaml

- uses: actions/checkout@v6
  with:
    repository: OpenVoiceOS/gh-automations
    ref: dev
    path: _gh_automations/

```

---

## Reusable Workflows

Every reusable workflow lives in `.github/workflows/` and is called as:

```yaml
uses: OpenVoiceOS/gh-automations/.github/workflows/<name>.yml@dev

```

The filename below is the actual file in this repo (the `<name>.yml`). The name of the wrapper workflow in your own repo is up to you.

### Release

| Workflow | Purpose |
|---|---|
| `publish-alpha.yml` | On PR merge to `dev`: bump version, optionally update changelog / tag pre-release / publish alpha to PyPI / notify Matrix, and open a release PR to `master`. PyPI publish and Matrix notify are jobs **inside** this workflow, gated by `publish_pypi` / `notify_matrix`. |
| `publish-stable.yml` | On push to `master`: remove the alpha suffix, tag the stable release, optionally publish to PyPI, notify Matrix, and sync `master` → `dev`. |
| `release-preview.yml` | Predict the next version from PR labels/title; post a `🏷️ Release Preview` section. |

### Build & test

| Workflow | Purpose |
|---|---|
| `build-tests.yml` | Build/install/test matrix across Python versions. Posts `🔨 Build Tests`. |
| `coverage.yml` | Run pytest with coverage; post `📊 Coverage`; optionally deploy the HTML report to Pages (`deploy_pages: true`). |
| `ovoscope.yml` | Run [ovoscope](ovoscope-overview.md) end-to-end skill tests; post `🔌 Skill Tests (ovoscope)`. |
| `intent-case-tests.yml` | Run the file-based ovoscope intent-routing accuracy matrix (sharded by language); post `🎯 Intent-Case Accuracy`. |
| `tts-intelligibility.yml` | Synthesise speech, transcribe it back with reference STT, score WER/CER; post `🗣️ TTS Intelligibility`. |
| `opm-check.yml` | OPM (OVOS Plugin Manager) plugin detection, interface validation, import timing; post `🔌 Plugin Detection`. |

### Quality & policy

| Workflow | Purpose |
|---|---|
| `license-check.yml` | Scan dependencies for copyleft/incompatible licenses (universal-donor policy); post `⚖️ License Check`. |
| `pip-audit.yml` | Scan installed dependencies for CVEs; optional SARIF upload; post `🔒 Security (pip-audit)`. |
| `lint.yml` | Run ruff and/or pre-commit; post lint results. |
| `type-check.yml` | Run mypy; post `🔎 Type Check` (informational unless `fail_on_errors: true`). |
| `docs-check.yml` | Verify required docs files exist; optional markdownlint; post `📚 Docs`. |
| `repo-health.yml` | Check required files / version block, greet first-time contributors; post `📋 Repo Health`. |

### Skills

| Workflow | Purpose |
|---|---|
| `skill-check.yml` | Locale structure, language coverage, `skill.json` validity; post `🎙️ Skill`. |
| `locale-check.yml` | Verify locale folders are correctly included in the package build. |
| `spec-lint.yml` | Run `ovos-spec-lint` against a skill's locale folder (OVOS-INTENT-1 / OVOS-INTENT-2). |

### Notifications & dependency tracking

| Workflow | Purpose |
|---|---|
| `downstream-check.yml` | Report which packages in the alpha constraints depend on a given package. |
| `notify-matrix.yml` | Send a message to the OVOS Matrix channel (called by the publish workflows). |

### Deprecated (kept for backward compatibility — remove after 2027-01-01)

| Workflow | Replacement |
|---|---|
| `python-support.yml` | `build-tests.yml` (multi-version build/install/test). |
| `coverage-pages.yml` | `coverage.yml` with `deploy_pages: true`. |

Full input/output/job reference: [Workflow Reference](gh-automations-workflows.md)

---

## Python Scripts

Located in `scripts/`. Checked out by the reusable workflows at run time — not installed as a package.

| Script | Key function | Purpose |
|---|---|---|
| `_version_utils.py` | `read_version` / `format_version` / `write_version_block` | Parse, format, and rewrite the `version.py` block; shared by all version scripts |
| `update_version.py` | `update_version(part, version_file)` | Bump `VERSION_MAJOR/MINOR/BUILD/ALPHA` in `version.py` |
| `remove_alpha.py` | `update_alpha(version_file)` | Set `VERSION_ALPHA = 0` (declare stable) |
| `get_version.py` | `get_version(version_file)` | Read and print current version string |
| `check_downstream.py` | `get_downstream(package_name)` | Report reverse dependencies using `pipdeptree` |
| `update_pr_comment.py` | `find_ovos_comment` / `insert_or_replace_section` | Find-or-create and update sections of the shared OVOS PR Checks comment |
| `check_skill.py` | `run_checks(repo_root, ...)` | Skill locale / `skill.json` analysis |
| `check_release.py` | `run_checks(version_file, ...)` | Predict next version from PR labels/title |
| `check_opm.py` | `check_opm(plugin_type, entry_point, ...)` | OPM plugin detection, interface validation, import timing |

All version scripts share the `version.py` block format:

```python

# START_VERSION_BLOCK
VERSION_MAJOR = 1
VERSION_MINOR = 2
VERSION_BUILD = 3
VERSION_ALPHA = 4   # 0 = stable

# END_VERSION_BLOCK

```

---

## Documentation

- [Release Flow](gh-automations-release.md) — Full lifecycle: alpha → stable → release channels
- [Workflow Reference](gh-automations-workflows.md) — Every input, output, job, and bot guard for each reusable workflow

---

## Related repos

| Repo | Role |
|---|---|
| [ovos-releases](https://github.com/OpenVoiceOS/ovos-releases) | Holds `constraints-alpha/testing/stable.txt`; updated after stable releases. The channel-compatibility check and `downstream-check.yml` read these files. |
| [raspOVOS](https://github.com/OpenVoiceOS/raspOVOS) | Uses a `constraints-*.txt` URL as the `CONSTRAINTS` env var during image builds. |
