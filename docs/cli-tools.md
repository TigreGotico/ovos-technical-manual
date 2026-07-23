# Command-line Tools

!!! abstract "In a nutshell"
    Installing OVOS also installs a handful of **terminal commands** — small programs you run from
    a shell to configure the assistant, poke a running system ("say this", "listen now"), read the
    logs, or launch the individual services by hand. This page is a catalogue of the ones the core
    OVOS packages provide, what each does, and which package ships it. (These are the *core* CLIs;
    the [RaspOVOS image](install-raspovos.md) adds its own extra convenience commands on top.) See
    the [Glossary](glossary.md) for unfamiliar terms.

Each command below is a console-script entry point declared by a core OVOS package, so it lands on
your `PATH` when that package is installed. Run any of them with `--help` for the authoritative,
version-correct options.

---

## Configuration — `ovos-config`

Shipped by **[`ovos-config`](config.md)**. Inspect and edit the layered
[configuration](config.md) without hand-editing JSON.

| Command | What it does |
|---|---|
| `ovos-config show` | Print the merged configuration as a table. |
| `ovos-config get -k <key>` | Read the value(s) at a key or key path (e.g. `-k /tts/module`); a loose key name lists every match. |
| `ovos-config set -k <key> -v <value>` | Write a value into the user configuration; omit `-v` to be prompted (useful when the key is ambiguous). |
| `ovos-config autoconfigure -l <lang>` | Pick sensible default STT/TTS plugins for a language. `--lang`/`-l` is required; select `--online`/`-on`, `--offline`/`-off`, or `--hybrid`/`-hy` (offline TTS + online STT — the default when none is given), and optionally `--male`/`-m` or `--female`/`-f` for the TTS voice (TTS is left unconfigured if neither is passed). |
| `ovos-config telemetry --enable` / `--disable` | Opt in or out of anonymous intent telemetry. |

`ovos-config autoconfigure --help` is the recommended first stop after an install to set
language-appropriate defaults.

---

## Talking to a running OVOS — `ovos-bus-client`

Shipped by **[`ovos-bus-client`](core-libraries.md#ovos-bus-client)**. These send messages to a *running*
OVOS over the [MessageBus](bus-service.md) — handy for testing, scripting, and debugging.

| Command | What it does |
|---|---|
| `ovos-listen` | Trigger the microphone to start listening, as if the wake word had fired. |
| `ovos-speak "<phrase>"` | Make OVOS speak a phrase out loud. |
| `ovos-say-to "<phrase>"` | Inject an utterance into the pipeline as if the user had said it. |
| `ovos-simple-cli` | Open an interactive terminal chat with the assistant. |

---

## Reading the logs — `ovos-logs`

Shipped by **[`ovos-utils`](core-libraries.md#ovos-utils)**. A helper for slicing and filtering the OVOS
[log files](core-libraries.md#ovos-utils) without wrestling with `grep`/`tail`.

| Command | What it does |
|---|---|
| `ovos-logs slice` | Extract a time-bounded slice across the logs (`--start` / `--until`). |
| `ovos-logs list` | List messages filtered by level — `--error`, `--warning`, `--exception`, `--debug` — and time. |
| `ovos-logs show -l <log>` | Print one named log (e.g. `skills`, `bus`, `audio`). |
| `ovos-logs reduce` | Truncate the logs to a given `--size` or `--date` to reclaim space. |

---

## Running the services by hand

Each core OVOS service is normally started by your service manager (systemd, the
[ovos-installer](ovos-installer.md), or Docker), but every one also has a console script so you
can launch it directly — useful for debugging or minimal/headless setups.

| Command | Service | Package |
|---|---|---|
| `ovos-core` | The skills service ([ovos-core](core.md)) | `ovos-core` |
| `ovos-messagebus` | The [MessageBus](bus-service.md) server | `ovos-messagebus` |
| `ovos-dinkum-listener` | The [speech/listener service](speech-service.md) | `ovos-dinkum-listener` |
| `ovos-audio` | The [audio service](audio-service.md) — TTS & sound playback (and the legacy media audioservice) | `ovos-audio` |
| `ovos-gui-service` | The [GUI service](gui-service.md) | `ovos-gui` |
| `ovos-gui-debug-tui` | A terminal viewer for GUI state, for debugging | `ovos-gui` |
| `ovos-intent-service` | The [intent service](intent-service.md), run standalone | `ovos-core` |
| `ovos-skill-installer` | The [skill installer](skill-installer.md), run standalone | `ovos-core` |
| `ovos-ocp-standalone` | The [OCP media player](ocp-audio-plugin.md#standalone-mode), run standalone | `ovos-plugin-common-play` |

---

## Related Pages

- [ovos-config](config.md) — the configuration system the `ovos-config` CLI edits.
- [ovos-bus-client Overview](core-libraries.md#ovos-bus-client) — the library behind the `ovos-*` bus commands.
- [Logging](core-libraries.md#ovos-utils) — log locations and levels that `ovos-logs` reads.
- [ovos-docs-viewer](docs-viewer.md) — the in-terminal documentation browser.
- [RaspOVOS helper commands](install-raspovos.md#helpful-commands) — extra CLIs added by the RaspOVOS image.

---

## Command `--help` Output (Generated)

<!-- BEGIN GENERATED: cli-help-output -->
<!-- This section is auto-generated by tools/gen_reference.py from the upstream source of truth. Do not hand-edit; re-run the script instead. -->
??? example "`ovos-config --help`"

    ```text
    Usage: ovos-config [OPTIONS] COMMAND [ARGS]...                                 
                                                                                    
                                                                                    
     Small helper tool to quickly show, get or set config values                    
     `ovos-config [COMMAND] --help` for further information about the specific      
     command ARGUMENTS                                                              
                                                                                    
    ╭─ Options ────────────────────────────────────────────────────────────────────╮
    │ --help  Show this message and exit.                                          │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ╭─ Show configuration tables (Joined/User/System/Remote) ──────────────────────╮
    │ show    By ommiting a specific configuration a joined configuration table is │
    │         shown. (which is the one ultimately gets loaded by ovos)             │
    │         Based on this consideration you can further trim the table by        │
    │         section.                                                             │
    │         If the sections are unknown you may want to list them.               │
    │         Examples:                                                            │
    │         ovos-config show                                    # shows all the  │
    │         configuration values in a table format                               │
    │         ovos-config show -s -l                              # shows the      │
    │         sections of the system configuration                                 │
    │         ovos-config show -u --section base                  # shows only the │
    │         base (ie. top level) values of the user configuration                │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ╭─ Get specific key(s) ────────────────────────────────────────────────────────╮
    │ get    Search for config keys in the (joined) configuration                  │
    │        Meant to either loosely search for keys resp. parts thereof or        │
    │        specific dictionary paths (form: `/path/to/key`)                      │
    │        The loose search will output a list of found keys - if there are      │
    │        multiple - that match the query (full or in part)                     │
    │        The strict search performs a query to a specific path and will only   │
    │        output the value. (usefull for shell scripting)                       │
    │        Examples:                                                             │
    │        ovos-config get -k lang                              # get all lang   │
    │        key values across the configuration                                   │
    │        ovos-config get -k /tts/module                       # get the key at │
    │        the position specified                                                │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ╭─ Setting user values ────────────────────────────────────────────────────────╮
    │ set      Sets a config key in the user configuration                         │
    │          Loosely searches a config key and if multiple are found asks which  │
    │          key and value should be written.                                    │
    │          The user may pass a value to bypass prompting.                      │
    │          Examples:                                                           │
    │          ovos-config set -k gui                              # lists all     │
    │          config keys containing "gui" (either as endpoint or in path),       │
    │                                                              # let the user  │
    │          choose the specific key and asks for the value                      │
    │          ovos-config set -k blacklisted_skills -v myskill    # Adds          │
    │          "myskill" as an blacklisted skill                                   │
    │                                                              # Since this is │
    │          a pretty specific key and a value is passed, the user won't be      │
    │          prompted                                                            │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ╭─ Commands ───────────────────────────────────────────────────────────────────╮
    │ autoconfigure  Automatically configures the language, STT, and TTS settings  │
    │                based on user input.                                          │
    │ telemetry      Enable intent telemetry upload for the opendata initiative.   │
    │                OpenData can be seen live at https://opendata.tigregotico.pt  │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ```

??? example "`ovos-logs --help`"

    ```text
    Usage: ovos-logs [OPTIONS] COMMAND [ARGS]...                                   
                                                                                    
      Small helper tool to quickly navigate the logs, create slices and quickview   
     errors                                                                         
     ovos-logs [COMMAND] --help for further information about the specific command  
     ARGUMENTS                                                                      
                                                                                    
    ╭─ Options ────────────────────────────────────────────────────────────────────╮
    │ --help  Show this message and exit.                                          │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ╭─ Slice logs by time ─────────────────────────────────────────────────────────╮
    │ slice    Optionally define start (-s) and the time until (-u) the slice      │
    │          should be limited to.                                               │
    │          Different logs can be included using the -l option. If not          │
    │          specified, all logs will be included.                               │
    │          Optionally the directory where the logs are stored (-p) and the     │
    │          file where the slices should be dumped (-f) can be specified.       │
    │                                                                              │
    │          ▌ Examples:                                                         │
    │          ▌ ovos-logs slice                                            #      │
    │          ▌ Slice all logs from service start up until now                    │
    │          ▌ ovos-logs slice -s 01-12-2023 -u '01-12-2023 17:00:20'     #      │
    │          ▌ Slice all logs from the start of december the first until         │
    │          ▌ 17:00:20                                                          │
    │          ▌ ovos-logs slice -l bus -l skills -f ~/myslice.log          #      │
    │          ▌ Slice skills.log and bus.log from service start up until now      │
    │          ▌ and dump it to the file ~/myslice.log                             │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ╭─ List logs by severity ──────────────────────────────────────────────────────╮
    │ list    Log level has to be specified.                                       │
    │         Optionally define start (-s) and the time until (-u) the slice       │
    │         should be limited to.                                                │
    │         Different logs can be included using the -l option. If not           │
    │         specified, all logs will be included.                                │
    │         Optionally the directory where the logs are stored (-p) and the file │
    │         where the slices should be dumped (-f) can be specified.             │
    │                                                                              │
    │         ▌ Examples:                                                          │
    │         ▌ ovos-logs list -x                                           #      │
    │         ▌ List all exceptions from service start up until now                │
    │         ▌ ovos-logs list -e -w -s 01-12-2023 -u '01-12-2023 17:00:20' #      │
    │         ▌ List all errors and warnings from the start of december the        │
    │         ▌ first until 17:00:20                                               │
    │         ▌ ovos-logs list -x -l bus -l skills -f                       #      │
    │         ▌ List all exceptions from skills.log and bus.log and dump it to     │
    │         ▌ the file ~/list_xxx_xxx.log                                        │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ╭─ Downsize logs ──────────────────────────────────────────────────────────────╮
    │ reduce  Reduce logs to a given size (in bytes) or remove entries before a    │
    │         given date.                                                          │
    │         Different logs can be included using the -l option. If not           │
    │         specified, all logs will be included.                                │
    │         Optionally the directory where the logs are stored (-p) can be       │
    │         specified.                                                           │
    │                                                                              │
    │         ▌ Examples:                                                          │
    │         ▌ ovos-logs reduce                                            #      │
    │         ▌ Reduce all logs to 0 bytes                                         │
    │         ▌ ovos-logs reduce -s 1000000                                 #      │
    │         ▌ Reduce all logs to ~1MB (latest logs)                              │
    │         ▌ ovos-logs reduce -d "1-12-2023 17:00"                       #      │
    │         ▌ Reduce all logs to entries after the specified date/time           │
    │         ▌ ovos-logs reduce -s 1000000 -l skills -l bus                #      │
    │         ▌ Reduce skills.log and bus.log to ~1MB (latest logs)                │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ╭─ Show logs (using less) ─────────────────────────────────────────────────────╮
    │ show    A service log has to be specified (-l).                              │
    │         Optionally the directory where the logs are stored (-p) can be       │
    │         specified.                                                           │
    │                                                                              │
    │         ▌ Examples:                                                          │
    │         ▌ ovos-logs show -l skills                                    #      │
    │         ▌ Display skills.log                                                 │
    │         ▌ ovos-logs show -l debug -p ~/custom_path/                   #      │
    │         ▌ Display debug.log from a custom path                               │
    ╰──────────────────────────────────────────────────────────────────────────────╯
    ```
<!-- END GENERATED -->

---

*Source code: [OpenVoiceOS/ovos-config](https://github.com/OpenVoiceOS/ovos-config), [OpenVoiceOS/ovos-bus-client](https://github.com/OpenVoiceOS/ovos-bus-client), and [OpenVoiceOS/ovos-utils](https://github.com/OpenVoiceOS/ovos-utils).*
