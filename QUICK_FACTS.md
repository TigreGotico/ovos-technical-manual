# Quick Facts — `ovos-technical-manual`

OpenVoiceOS component: ovos-technical-manual (developer documentation)

| Feature | Details |
|---------|---------|
| Type | MkDocs documentation site (not a PyPI package) |
| License | Apache-2.0 |
| Repository | [https://github.com/OpenVoiceOS/ovos-technical-manual](https://github.com/OpenVoiceOS/ovos-technical-manual) |
| Build Tool | `mkdocs` + `mkdocs-material` |
| Deploy | GitHub Pages from `master` (`.github/workflows/build.yml`) |
| Toolchain pin | `pygments==2.18.0` (newer crashes `pymdown-extensions==10.11.2`) |
| Source of truth | each documented repo's `origin/dev` + the formal specs in `OpenVoiceOS/architecture` |
