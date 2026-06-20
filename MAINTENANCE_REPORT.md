# Maintenance Report — `ovos-technical-manual`

## [2026-06-20] — Source-verification audit of the full manual

Every navigation page was validated against the real source code of the repo it
documents (read-only against each repo's `origin/dev`) and against the formal
specifications in `OpenVoiceOS/architecture`.

### Changes
- Corrected a large set of inaccurate claims left by earlier automated passes —
  invented class/method names, wrong config keys and defaults, wrong OPM
  entry-point groups (e.g. `opm.skill` is singular; `opm.transformer.text`;
  `opm.VAD`), and a fabricated "self.gui deprecated in 9.0.0 / template-only GUI"
  narrative (`self.gui` is live on ovos-workshop v8).
- Re-classified genuine but **unreleased** work as **Upcoming**, linked to the open
  PR (e.g. messagebus webrockets/Rust backends #51; the GUI rework — OVOS-GUI-1
  spec + ovos-gui#112 + ovos-workshop#420; AsyncMessageBusClient #200; phoonnx
  engines). Such content is no longer presented as shipped.
- Added formal-specification references to the protocol pages (bus, listener,
  pipeline, stop, intent, session, GUI).
- Fixed the GitHub Pages deploy: pinned `pygments==2.18.0` (newer pygments crashes
  `pymdown-extensions==10.11.2`). The strict MkDocs build is green.
- Removed prior fabrications from the convention files (`FAQ.md`, `QUICK_FACTS.md`,
  `AUDIT.md`).

### Verification
- `mkdocs build --strict` passes with no warnings or broken internal links.
- Each fix traces to a source location; source bugs found are listed in `AUDIT.md`.
- The full page→source validation map is kept at
  `~/wiki/pages/projects/ovos-technical-manual.md`.
