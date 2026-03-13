
# Suggestions — `ovos-technical-manual`

> This file tracks proposed improvements for human developers. Each entry includes
> the problem/opportunity, proposed solution, and estimated impact.

### 1. Add type hints to public API

**Problem/Opportunity**: Functions and classes may lack full type annotations,
reducing IDE support and making the codebase harder to audit.

**Proposed Solution**: Annotate all public function signatures with PEP 484
type hints. Run `mypy` to verify.

**Estimated Impact**: Low effort, high long-term benefit for maintainability.

### 2. Expand unit test coverage

**Problem/Opportunity**: Test coverage may be incomplete, leading to undetected
regressions during refactors or dependency upgrades.

**Proposed Solution**: Review `test/` coverage report and add tests for
uncovered edge cases, especially around plugin loading and error paths.

**Estimated Impact**: Medium — reduces regression risk significantly.

### 4. Create `dev` branch and align with OVOS standards

**Problem/Opportunity**: This repository currently only has a `master` branch, while all other OpenVoiceOS repositories use `dev` as the main development branch. This can lead to confusion for contributors and breaks the "dev: Main development branch" mandate.

**Proposed Solution**: Create a `dev` branch from `master`, set it as the default branch, and update all GitHub Actions to trigger on `dev`.

**Estimated Impact**: Medium — improves consistency across the workspace.
