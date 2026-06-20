# Suggestions — `ovos-technical-manual`

> Proposed improvements for human developers. Each entry: the problem/opportunity,
> a proposed solution, and estimated impact.

### 1. Add a link-checking step to CI

**Problem/Opportunity**: Internal links and anchors break silently during renames
and reorganizations; the deploy workflow does not run a strict build.

**Proposed Solution**: Run `mkdocs build --strict` in CI (it fails on broken
internal links and missing nav targets) before `gh-deploy`.

**Estimated Impact**: Medium — catches broken navigation before it reaches the site.

### 2. Publish the formal specs to a stable URL

**Problem/Opportunity**: Pages now reference `OpenVoiceOS/architecture` specs
(OVOS-MSG-1, GUI-1, …) via GitHub blob URLs because the specs are not yet published
to a canonical docs site.

**Proposed Solution**: Publish the `architecture` specs (e.g. their own MkDocs site
or a section here) and update the spec reference links to the canonical URLs.

**Estimated Impact**: Medium — gives the spec references stable, versioned anchors.

### 3. Create a `dev` branch and align with OVOS standards

**Problem/Opportunity**: This repository only has `master`, while other OpenVoiceOS
repositories develop on `dev`. The site deploys on push to `master`, so docs land
live with no staging step.

**Proposed Solution**: Create `dev` from `master`, set it as the default branch, and
deploy a preview from `dev` (PR → `dev` → `master`).

**Estimated Impact**: Medium — adds a review/staging step and matches the org flow.
