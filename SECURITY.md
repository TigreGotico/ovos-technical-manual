# Security Policy

This repository holds the OpenVoiceOS Technical Manual — documentation only, no
runnable service and no user data. If you found a **documentation bug that gives
unsafe advice** (for example a config example that would expose the message bus
to the network), please open a regular issue or pull request against this repo.

## Reporting a vulnerability in OVOS itself

For an actual security vulnerability in an OpenVoiceOS component (`ovos-core`,
`ovos-messagebus`, `ovos-PHAL`, a specific skill, etc.), **do not open a public
issue**. Use GitHub's private vulnerability reporting on the affected repository
instead:

1. Go to the repository on GitHub (for example
   `https://github.com/OpenVoiceOS/ovos-core`).
2. Open the **Security** tab.
3. Choose **Report a vulnerability** to open a private advisory visible only to
   maintainers.

If a repository does not have private reporting enabled, contact the maintainers
through the community channels linked from the
[Open Voice OS website](https://openvoiceos.org) instead of filing a public issue.

See [Privacy & Security](docs/privacy-security.md) for the network- and
trust-model overview of a default OVOS install.
