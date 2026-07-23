# License

!!! abstract "In a nutshell"
    OVOS follows a **universal donor** licensing policy: the code should be usable by anyone,
    anywhere, with no strings attached. In practice that means permissive licenses (mostly
    Apache 2.0 or BSD) for all core components, with a short, explicitly documented list of
    exceptions where a dependency forces a stricter license on one specific plugin.

Under the universal donor policy, OVOS code should be usable anywhere by anyone, with no
conditions attached. OVOS is predominately Apache 2.0 or BSD licensed; there are only a few
exceptions, and each is listed below.

Individual plugins or skills may carry their own license when they wrap a dependency that
requires it — for example a TTS plugin that wraps an AGPL-licensed engine cannot itself be
relicensed under a more permissive term. Core components are kept fully free; any code whose
license cannot be controlled lives in an optional plugin instead, flagged as such.

This also means avoiding LGPL code, for the reasons explained in
[this discussion of the GPL classpath exception](https://softwareengineering.stackexchange.com/questions/119436/what-does-gpl-with-classpath-exception-mean-in-practice/326325#326325).

## Policy properties

The license policy has the following properties:

- It gives the user of the software complete and unrestrained access, such that they may
  inspect, modify, and redistribute their changes:
    - **Inspection** — anyone may inspect the software for security vulnerabilities.
    - **Modification** — anyone may modify the software to fix issues or add features.
    - **Redistribution** — anyone may redistribute the software on their own terms.
- It is compatible with GPL licenses — projects licensed as GPL can be distributed with OVOS.
- It allows incorporating GPL-incompatible free software, such as CDDL-licensed code.

The policy does not restrict what software may run *on* OVOS. Thanks to the plugin
architecture, even traditionally tightly-coupled components such as drivers can be
distributed separately, so plugin maintainers are free to choose whatever license fits their
own project.

---

## Notable licensing exceptions

The repositories below do not follow the universal donor policy; check their licenses are
compatible with your use case before depending on them.

| Repository | License | Reason |
|---|---|---|
| [ovos-intent-plugin-padatious](https://github.com/OpenVoiceOS/ovos-intent-plugin-padatious) | Apache-2.0 | [padatious](https://github.com/MycroftAI/padatious) depends on [libfann](https://github.com/libfann/fann) ([LGPL-2.1](https://github.com/libfann/fann/blob/master/LICENSE.md)); its own license status is uncertain as a result |
| [ovos-tts-plugin-mimic3](https://github.com/OpenVoiceOS/ovos-tts-plugin-mimic3) | AGPL | depends on [mimic3](https://github.com/MycroftAI/mimic3) ([AGPL-3.0](https://github.com/MycroftAI/mimic3/blob/master/LICENSE)). This plugin is **archived**; see [Deprecated & Archived Repositories](deprecated-repos.md) for the current replacement |
| [ovos-tts-plugin-espeakNG](https://github.com/OpenVoiceOS/ovos-tts-plugin-espeakNG) | GPL | depends on [espeak-ng](https://github.com/espeak-ng/espeak-ng) ([GPL-3.0](https://github.com/espeak-ng/espeak-ng/blob/master/COPYING)) |
| [ovos-g2p-plugin-espeak](https://github.com/OVOSHatchery/ovos-g2p-plugin-espeak) | GPL | depends on [espeak-phonemizer](https://github.com/rhasspy/espeak-phonemizer) ([GPL-3.0](https://github.com/rhasspy/espeak-phonemizer/blob/master/LICENSE)) |
| [ovos-tts-plugin-SAM](https://github.com/OpenVoiceOS/ovos-tts-plugin-SAM) | see repo (no license file) | the package self-declares Apache-2.0 in its `pyproject.toml`, but the repository ships no `LICENSE` file, and the underlying S.A.M. engine is reverse-engineered abandonware with no clear upstream license |

## Further reading

- [Why OpenVoiceOS Uses Permissive Licenses](https://blog.openvoiceos.org/posts/2023-02-28-permissive-licenses) — OVOS blog
- [Deprecated & Archived Repositories](deprecated-repos.md) — current replacements for archived plugins
