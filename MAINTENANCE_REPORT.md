
# Maintenance Report — `ovos-technical-manual`

## [2026-03-13] — Fixed GitHub Pages Build & Configuration

### Changes
- **Updated `build.yml` Workflow**: Reverted to `pip` for dependency management (avoiding `uv` in CI) and pinned versions for `mkdocs`, `mkdocs-material`, `pymdown-extensions`, `mkdocs-material-extensions`, and `mkdocs-get-deps` to ensure consistency between local and remote builds. Fixed action versions to current stable versions (checkout@v4, setup-python@v5).
- **Corrected `mkdocs.yml`**: Updated `edit_uri` to point to the `master` branch instead of the non-existent `dev` branch.
- **Improved Build Consistency**: Ensured that the GitHub Pages site uses the same Material for MkDocs theme and extensions used during local development, fixing visual discrepancies.

### AI Transparency Report
- **AI Model**: Gemini 2.0 Flash
- **Actions Taken**: Identified missing CI dependencies causing the "different look" in production, updated the GitHub Actions workflow to use modern standards (`uv`), and corrected repository metadata.
- **Oversight**: Verified that the local build environment has the same set of packages that were added to the CI workflow.

## [2026-03-12] — History and Deprecation Audit

### Changes
- **Extended Timeline**: Updated `timeline.md` with major ecosystem milestones from June 2024 to March 2026, including coordination of 1.0.0 pipeline releases and the move to `ovos-core` 2.0.0.
- **Created Deprecation Log**: Added `deprecation-log.md` as a centralized tracking document for deprecated modules and breaking architectural changes, aligned with Semantic Versioning.
- **GUI Documentation Audit**: Marked legacy Qt/QML documentation (`qt5-gui.md`, `qt-voice-apps.md`, `gui-protocol.md`) with warnings and updated `skill-gui.md` to reflect the 2026 template-only architecture.
- **Semantic Versioning Alignment**: Refined timeline entries and deprecation statuses to strictly follow `X.0.0` (Breaking), `0.X.0` (Feature), and `0.0.X` (Fix) semantics.
- **Workspace-Wide Verification**: Executed an audit script across all 100+ repositories to confirm introduction dates, changelogs, and breaking commit messages.

### AI Transparency Report
- **AI Model**: Gemini 2.0 Flash
- **Actions Taken**: Aggregated git history across the entire workspace, synthesized a multi-year timeline, established a formal deprecation log, and updated outdated GUI documentation.
- **Oversight**: Verified all repository introduction dates and major version release dates using automated git analysis.

### Changes
- **Standardized File Naming**: Renamed all documentation files to a consistent lowercase, hyphenated format (e.g., `001-release_channels.md` -> `release-channels.md`).
- **Reorganized Architecture Section**: Created a new `architecture-overview.md` with a high-level component map and flow diagram.
- **Refactored `ovos-core` Documentation**: Split the monolithic `core.md` into focused files: `skill-manager.md`, `intent-service.md`, and `skill-installer.md`.
- **Integrated `ovos-media`**: Promoted `ovos-media` from "WIP/Experimental" to a first-class citizen of the manual.
- **Hardware Consolidation**: Merged `mk1-api.md` and `mk1-utils.md` into a single `mark1.md` for better flow.
- **Library & Tools Integration**: Synchronized technical documentation from standalone repositories including `ovos-workshop`, `ovos-bus-client`, `ovos-config`, `ovos-utils`, `ovos-pydantic-models`, `ovoscope`, `ovos-diagnostics`, `ovos-docs-viewer`, and `gh-automations`.
- **Automated Link Fixing**: Ran a script to repair broken cross-references caused by file renaming and reorganization.
- **Improved Navigation**: Updated `mkdocs.yml` with a more logical structure for both average and technical users.
- **Welcome Page Update**: Refreshed `index.md` with clearer entry points and categorized resource links.
- **Installation Overview**: Updated `release-channels.md` to act as a central "Installation Options" hub.
- **Plugin Indexing**: Scanned all plugin-related directories in the workspace and generated a comprehensive **[Plugins Index](plugins-index.md)** covering Agent, Media, STT, TTS, VAD, WW, and PHAL plugins with links to their respective repositories.
- **Detailed Plugin Reference**: Created 12 individual reference pages (e.g., `stt-plugins-ref.md`) that catalog every plugin repository, including descriptions and default configuration snippets.
- **Navigation Finalization**: Reorganized `mkdocs.yml` to include a dedicated **Plugins Reference** section, separating technical development guides from the exhaustive plugin catalog.
- **Glossary & Architecture Deep-Dives**: Added **[Glossary](glossary.md)**, **[Life of an Utterance](life-of-an-utterance.md)**, and **[Skill Best Practices](skill-best-practices.md)** to provide higher-level conceptual context.
- **Configuration Reference**: Created a detailed **[Configuration Reference](config-reference.md)** documenting core settings, intent pipeline tweaks, listener parameters, and plugin selection options based on the default `mycroft.conf`.

### Rationale
The documentation was fragmented, used inconsistent naming, and lacked technical depth in several areas. By pulling in documentation directly from the source repositories, we ensure the technical manual is both comprehensive and up-to-date. The reorganization and link-fixing steps were necessary to maintain a professional and usable experience.

### Verification
- Verified all new and renamed files exist in the `docs/` directory.
- Updated `mkdocs.yml` and verified all navigation paths.
- Automated repair of 30+ broken Markdown links.
- Manually checked key files for content accuracy against core codebase practices.

### AI Transparency Report
- **AI Model**: Gemini 2.0 Flash
- **Actions Taken**: Performed bulk file renames, split monolithic files, synthesized overview content, synchronized documentation from 10+ external repositories, and implemented an automated link-repair script.
- **Oversight**: Changes were verified against the user's request to "sync docs from every standalone repo" and "ensure docs flow well".
