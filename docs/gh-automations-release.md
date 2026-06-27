
# OVOS Release Flow

!!! abstract "In a nutshell"
    Software is published in versions, and OVOS offers each new version on three "channels" you can think of like ripeness: alpha is freshly cut and experimental, testing is partly proven, and stable is ready for everyday use. This page explains how a code change travels from a developer's keyboard to a published release. It is mainly for contributors and maintainers. See [Release Channels](release-channels.md) and the [Glossary](glossary.md).

All OVOS packages follow a rolling release model with three channels: **alpha**, **testing**, and **stable**. This document describes the full lifecycle from code change to published package, and separately covers the versioning strategy for gh-automations itself.

---

---

## Branches (per-repo)

Every OVOS package repo uses the following branch structure:

| Branch | Purpose |
|--------|---------|
| `dev` | Active development. Receives PRs. Publishes alpha releases automatically on merge. |
| `release-X.Y.ZaN` | Short-lived. Auto-created on each PR merge to `dev`. Used to propose a stable release. Deleted after PR to `master` is opened. |
| `master` | Stable. Receives only reviewed release PRs opened by automation. |

---

## Versioning (per-repo)

Versions follow `MAJOR.MINOR.BUILD[aN]` where the alpha suffix (`a1`, `a2`, …) is dropped on stable release.

The `version.py` file in each package is the authoritative source. The block between the marker comments is the only part that automation reads and rewrites:

```python

# START_VERSION_BLOCK
VERSION_MAJOR = 1
VERSION_MINOR = 2
VERSION_BUILD = 3
VERSION_ALPHA = 4   # 0 = stable release

# END_VERSION_BLOCK

__version__ = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}" + (f"a{VERSION_ALPHA}" if VERSION_ALPHA else "")

```

`read_version()` in `scripts/_version_utils.py` parses this block; `update_version()` in `scripts/update_version.py` rewrites it via `write_version_block()`. `update_alpha()` in `scripts/remove_alpha.py` sets `VERSION_ALPHA = 0` (declare stable). `get_version()` in `scripts/get_version.py` reads and formats the string.

### Version bump rules

`publish-alpha.yml`'s `bump_version` job reads the **PR labels** of the merged PR (it does not parse the PR title). The label-to-bump mapping is:

| PR label | Version bump |
|---|---|
| `breaking` | **Major**: `1.2.3a4` → `2.0.0a1` |
| `feature` or `enhancement` | **Minor**: `1.2.3a4` → `1.3.0a1` |
| `fix` or `bug` | **Build**: `1.2.3a4` → `1.2.4a1` |
| _(none of the above)_ | **Alpha only**: `1.2.3a4` → `1.2.3a5` |

Priority is major > minor > build > alpha. If the current version is already stable (alpha = 0), an unlabelled bump first increments `BUILD`: `1.2.3` → `1.2.4a1`.

> Labels are typically applied automatically from conventional-commit PR titles by a *separate* labeller workflow in your repo (e.g. one using `bcoe/conventional-release-labels`). That labeller is **not** part of gh-automations — `publish-alpha.yml` only consumes whatever labels are present at merge time. The [`release-preview.yml`](gh-automations-workflows.md#release-previewyml) workflow, by contrast, falls back to parsing the PR title prefix when no label is set.

---

## Alpha Release (on PR merge to `dev`)

Your repo's workflow calls `publish-alpha.yml@dev`. **All steps — version bump, changelog, pre-release tag, release PR, PyPI publish, and Matrix notify — are jobs inside `publish-alpha.yml` itself**, each gated by an input. Your wrapper file is just the trigger plus the `uses:` call.

```
PR merged → dev
    │
    ▼
your-repo workflow  (e.g. release.yml)
    │   trigger: pull_request types:[closed] branches:[dev]
    │   also:    workflow_dispatch
    │
    └─► publish_alpha job
        if: merged == true || workflow_dispatch
            uses: publish-alpha.yml@dev   (gh-automations)
            secrets: inherit               (PYPI_TOKEN, MATRIX_TOKEN, GITHUB_TOKEN)
                │
                ├─ [bump_version job]   (the gate — all others need: bump_version)
                │   Checkout repo + gh-automations scripts (@dev)
                │   if: PR merged (skipping allcontributors/pre-commit-ci bots
                │       when skip_bot_prs) OR workflow_dispatch
                │   Determine bump part from PR labels
                │   update_version.py <part> --version-file ...
                │   git-auto-commit-action@v7 → push to `branch` (default dev)
                │
                ├─ [update_changelog job]   if: update_changelog
                │   github-changelog-generator → commit & push
                │
                ├─ [tag_prerelease job]   if: publish_prerelease
                │   ncipollo/release-action → GitHub pre-release tag (e.g. 1.2.3a4)
                │
                ├─ [propose_release job]   if: propose_release  (default true)
                │   git checkout -B release-X.Y.ZaN  (force-create, idempotent)
                │   git push; gh pr create → PR to `base_branch` (default master)
                │
                ├─ [publish_pypi job]   if: publish_pypi
                │   python -m build
                │   pypa/gh-action-pypi-publish@release/v1 → PyPI  (uses PYPI_TOKEN)
                │
                └─ [notify job]   if: notify_matrix && PR merged
                    calls notify-matrix.yml@dev → OVOS Matrix channel (uses MATRIX_TOKEN)

```

> Note: `publish_pypi` and `notify_matrix` both default to **`false`**, so a bare call only bumps the version and opens the release PR. Set them explicitly (and provide `PYPI_TOKEN`/`MATRIX_TOKEN` via `secrets: inherit`) to publish and notify.

---

## Stable Release (on PR merge to `master`)

The `release-X.Y.ZaN` PR opened by the alpha flow requires **human review** before merging. This is the only manual gate in the pipeline.

Like the alpha flow, **every step lives inside `publish-stable.yml`**. Your wrapper is the `push: master` trigger plus the `uses:` call.

```
PR merged → master
    │
    ▼
your-repo workflow  (e.g. publish_stable.yml)
    │   trigger: push: branches:[master]
    │   also:    workflow_dispatch
    │
    └─► publish_stable job
        if: github.actor != 'github-actions[bot]'   ← bot loop guard
            uses: publish-stable.yml@dev   (gh-automations)
            secrets: inherit                (PYPI_TOKEN, MATRIX_TOKEN, GITHUB_TOKEN)
                │
                ├─ [bump_version job]   if: github.actor != 'github-actions[bot]'
                │   Detects target branch (uses default branch if master is absent)
                │   remove_alpha.py → VERSION_ALPHA = 0
                │   git-auto-commit-action@v7 → push to the stable branch
                │
                ├─ [tag_release job]   if: publish_release  (default true)
                │   ncipollo/release-action → GitHub release tag
                │
                ├─ [publish_pypi job]   if: publish_pypi
                │   python -m build
                │   pypa/gh-action-pypi-publish@release/v1 → PyPI (uses PYPI_TOKEN)
                │
                ├─ [sync_dev job]   if: sync_dev
                │   ad-m/github-push-action → push master → dev
                │
                └─ [notify job]   if: notify_matrix
                    calls notify-matrix.yml@dev → OVOS Matrix channel

```

### Why the bot guard is critical

`git-auto-commit-action` pushes the version commit (removing alpha) directly to the stable branch. Without the `if: github.actor != 'github-actions[bot]'` guard, that push would re-trigger the `push: master` event → another run → another tag attempt → failure (tag already exists) or an infinite loop.

The guard exists at both layers for belt-and-suspenders protection:

- Inside `publish-stable.yml`, on the `bump_version` job (`if: github.actor != 'github-actions[bot]'`).
- In your repo's wrapper job that calls `publish-stable.yml` (same condition).

---

## Release Channels (ovos-releases)

After a stable release is published to PyPI, the constraints files in [ovos-releases](https://github.com/OpenVoiceOS/ovos-releases) are updated:

| File | Channel |
|------|---------|
| `constraints-alpha.txt` | Alpha — newest, includes pre-releases |
| `constraints-testing.txt` | Testing |
| `constraints-stable.txt` | Stable |

These files use `>=` bounds (e.g. `ovos-utils>=0.3.0`) so users get the latest compatible version within their chosen channel. `downstream-check.yml` reads `constraints-alpha.txt` (default branch `main`) to compute reverse dependencies; the channel-compatibility check in `release-preview.yml` reads all three.

---

## Manual Reruns

Both `publish-alpha.yml` and `publish-stable.yml` support `workflow_dispatch`, so the wrapper workflows in your repo can be triggered manually from the GitHub Actions UI. This is useful when:

- A workflow failed due to a transient error (e.g. PyPI outage).
- A version bump was needed but the PR was merged without the right labels (dispatch forces an alpha bump).
- Testing the release pipeline on a new repo.

For this to work your wrapper's job condition must allow dispatch — `bump_version` runs on either a merged PR or a manual dispatch:

```yaml
if: github.event.pull_request.merged == true || github.event_name == 'workflow_dispatch'

```

## Upcoming

- **NGI codename release schedule** — a codename release schedule is planned. It is not yet released; the flow above reflects current behaviour.
