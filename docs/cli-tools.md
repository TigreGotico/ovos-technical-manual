# Command-line Tools

!!! abstract "In a nutshell"
    Installing OVOS also installs a handful of **terminal commands**: small programs you run from
    a shell to configure the assistant, poke a running system ("say this", "listen now"), read the
    logs, or launch the individual services by hand. This page is a catalog of the ones the core
    OVOS packages provide, what each does, and which package ships it. (These are the *core* CLIs.
    The [RaspOVOS image](install-raspovos.md) adds its own extra convenience commands on top.) See
    the [Glossary](glossary.md) for unfamiliar terms.

Each command below is a console-script entry point declared by a core OVOS package, so it lands on
your `PATH` when that package is installed. Most take `--help`, which is the authoritative,
version-correct list of options.

!!! warning "`--help` is not safe on older bus clients"
    `ovos-speak`, `ovos-say-to`, `ovos-listen` and `ovos-simple-cli` gained `--help` in
    `ovos-bus-client` 2.7.3. Before that they read the first argument as the utterance, so
    `ovos-speak --help` made the device **say "--help" out loud**, and `ovos-say-to --help` injected
    it as if you had spoken it
    ([ovos-bus-client#274](https://github.com/OpenVoiceOS/ovos-bus-client/pull/274)). On an older
    install, use the usage lines documented on this page instead.

---

## Configuration: `ovos-config`

Shipped by **[`ovos-config`](config.md)**. Inspect and edit the layered
[configuration](config.md) without hand-editing JSON.

| Command | What it does |
|---|---|
| `ovos-config show` | Print the merged configuration as a table. |
| `ovos-config get -k <key>` | Read the value(s) at a key or key path (e.g. `-k /tts/module`). A loose key name lists every match. |
| `ovos-config set -k <key> -v <value>` | Write a value into the user configuration. Omit `-v` to be prompted (useful when the key is ambiguous). |
| `ovos-config autoconfigure -l <lang>` | Pick sensible default STT/TTS plugins for a language. `--lang`/`-l` is required. Select `--online`/`-on`, `--offline`/`-off`, or `--hybrid`/`-hy` (offline TTS + online STT: the default when none is given). Optionally add `--male`/`-m` or `--female`/`-f` for the TTS voice. TTS is left unconfigured if neither is passed. |
| `ovos-config telemetry --enable` / `--disable` | Opt in or out of anonymous intent telemetry. |

`ovos-config autoconfigure --help` is the recommended first stop after an install to set
language-appropriate defaults. See the full generated
[`ovos-config --help` output](#command-help-output-generated) below.

---

## Talking to a running OVOS: `ovos-bus-client`

Shipped by **[`ovos-bus-client`](core-libraries.md#ovos-bus-client)**. These emit messages to a *running*
OVOS over the [messagebus](bus-service.md). They help with testing, scripting, and debugging.

| Command | What it does |
|---|---|
| `ovos-listen` | Trigger the microphone to start listening, as if the wake word had fired. |
| `ovos-speak "<phrase>"` | Make OVOS speak a phrase out loud. |
| `ovos-say-to "<phrase>"` | Inject an utterance into the pipeline as if the user had said it. |
| `ovos-simple-cli` | Open an interactive terminal chat with the assistant. |

---

## Reading the logs: `ovos-logs`

Shipped by **[`ovos-utils`](core-libraries.md#ovos-utils)**. A helper for slicing and filtering the OVOS
[log files](core-libraries.md#ovos-utils) without wrestling with `grep`/`tail`.

| Command | What it does |
|---|---|
| `ovos-logs slice` | Extract a time-bounded slice across the logs (`--start` / `--until`). |
| `ovos-logs list` | List messages filtered by level (`--error`, `--warning`, `--exception`, `--debug`) and time. |
| `ovos-logs show -l <log>` | Print one named log (e.g. `skills`, `bus`, `audio`). |
| `ovos-logs reduce` | Truncate the logs to a given `--size` or `--date` to reclaim space. |

See the full generated [`ovos-logs --help` output](#command-help-output-generated) below.

---

## Watching the bus: `ovos-busmon`

Shipped by **[`ovos-busmon`](https://github.com/OpenVoiceOS/ovos-busmon)**. A small web app that
connects to the [messagebus](bus-service.md) and streams every message live to a browser tab, in
one filterable, searchable timeline.

| Command | What it does |
|---|---|
| `ovos-busmon` | Start the web UI (default `http://127.0.0.1:8005`), connecting outward to a messagebus at `localhost:8181`. |

See [Watching the Bus: `ovos-busmon`](troubleshooting-bus.md)
for installation, configuration variables, security notes, and a walkthrough.

---

## Configuring skill settings from a browser: `ovos-skill-config-tool`

A community-built web UI, **[OVOS Skill Config Tool](https://github.com/OscillateLabsLLC/ovos-skill-config-tool)**,
for editing installed skills' settings without hand-editing `settings.json`.

| Command | What it does |
|---|---|
| `ovos-skill-config-tool` | Start the web UI (default `http://0.0.0.0:8000`). |

See [Skill Settings → Web-Based Settings UI](skill-settings.md#web-based-settings-ui-community)
for installation and credential configuration.

---

## Testing skills offline: `ovoscope`

Shipped by **[`ovoscope`](https://github.com/TigreGotico/ovoscope)**. Runs an in-process, mocked
assistant that loads real skills and the real intent-matching engines without audio hardware, so a
bug can be captured once and replayed instead of re-triggered on real hardware.

| Command | What it does |
|---|---|
| `ovoscope record` | Capture a fixture, optionally `--live` from a running OVOS instance. |
| `ovoscope run <fixture>` | Replay a fixture and exit non-zero on failure. |
| `ovoscope diff <a> <b>` | Compare two fixture files. |

See the [ovoscope guide](ovoscope-overview.md) for the full workflow, including `End2EndTest` for
writing an assertion once a fixture is captured.

---

!!! note "HiveMind CLI tools"
    HiveMind ships its own CLI tools (`hivemind-core`, `hivemind-client`), covered in
    [HiveMind Agents](hivemind-agents.md).

---

## Running the services by hand

Each core OVOS service is normally started by your service manager (systemd, the
[ovos-installer](ovos-installer.md), or Docker). Every one also has a console script, so you
can launch it directly. This is useful for debugging or minimal/headless setups. For running a
service from an editable checkout of its own repo while fixing a bug in it, see
[Development Environment](dev-environment.md).

| Command | Service | Package |
|---|---|---|
| `ovos-core` | The skills service ([ovos-core](core.md)) | `ovos-core` |
| `ovos-messagebus` | The [messagebus](bus-service.md) server | `ovos-messagebus` |
| `ovos-dinkum-listener` | The [speech/listener service](speech-service.md) | `ovos-dinkum-listener` |
| `ovos-audio` | The [audio service](audio-service.md): TTS and sound playback (and the legacy media audioservice) | `ovos-audio` |
| `ovos-gui-service` | The [GUI service](gui-service.md) | `ovos-gui` |
| `ovos-gui-debug-tui` | A terminal viewer for GUI state, for debugging | `ovos-gui` |
| `ovos-intent-service` | The [intent service](intent-service.md), run standalone | `ovos-core` |
| `ovos-skill-installer` | The [skill installer](skill-installer.md), run standalone | `ovos-core` |
| `ovos-ocp-standalone` | The [OCP media player](ocp-audio-plugin.md#standalone-mode), run standalone | `ovos-plugin-common-play` |

---

## Related Pages

- [ovos-config](config.md): the configuration system the `ovos-config` CLI edits.
- [ovos-bus-client Overview](core-libraries.md#ovos-bus-client): the library behind the `ovos-*` bus commands.
- [Logging](core-libraries.md#ovos-utils): log locations and levels that `ovos-logs` reads.
- [ovos-docs-viewer](docs-viewer.md): the in-terminal documentation browser.
- [RaspOVOS helper commands](raspovos-commands-reference.md#helpful-commands): extra CLIs added by the RaspOVOS image.

---

## Command Help Output (Generated)

<!-- BEGIN GENERATED: cli-help-output -->
<!-- This section is auto-generated by tools/gen_reference.py from the upstream source of truth. Do not hand-edit; re-run the script instead. -->
??? example "`ovos-config --help`"

    ```text
    [33mUsage:[0m [1movos-config[0m [[31mOPTIONS[0m] [31mCOMMAND[0m [[31mARGS[0m]...                                 
                                                                                    
                                                                                    
     Small helper tool to quickly show, get or set config values                    
     [2m`ovos-config [COMMAND] [0m[2;31m--help[0m[2m` for further information about the specific [0m     
     [2mcommand ARGUMENTS [0m                                                             
                                                                                    
    [2m╭─[0m[2m Options [0m[2m───────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [31m--help[0m  Show this message and exit.                                          [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Show configuration tables (Joined/User/System/Remote) [0m[2m─────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36mshow[0m[1;37m  [0m[37m  [0m[37mBy ommiting a specific configuration a joined configuration table is[0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mshown. (which is the one ultimately gets loaded by ovos)            [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mBased on this consideration you can further trim the table by       [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37msection.                                                            [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mIf the sections are unknown you may want to list them.              [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mExamples:                                                           [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37movos-config show                                    # shows all the [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mconfiguration values in a table format                              [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37movos-config show [0m[91m-s[0m[37m [0m[91m-l[0m[37m                              # shows the     [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37msections of the system configuration                                [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37movos-config show [0m[91m-u[0m[37m [0m[31m--section[0m[37m base                  # shows only the[0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mbase (ie. top level) values of the user configuration               [0m [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Get specific key(s) [0m[2m───────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36mget[0m[1;37m  [0m[37m  [0m[37mSearch for config keys in the (joined) configuration                 [0m [2m│[0m
    [2m│[0m [1;37m     [0m[37m  [0m[37mMeant to either loosely search for keys resp. parts thereof or       [0m [2m│[0m
    [2m│[0m [1;37m     [0m[37m  [0m[37mspecific dictionary paths (form: `/path/to/key`)                     [0m [2m│[0m
    [2m│[0m [1;37m     [0m[37m  [0m[37mThe loose search will output a list of found keys - if there are     [0m [2m│[0m
    [2m│[0m [1;37m     [0m[37m  [0m[37mmultiple - that match the query (full or in part)                    [0m [2m│[0m
    [2m│[0m [1;37m     [0m[37m  [0m[37mThe strict search performs a query to a specific path and will only  [0m [2m│[0m
    [2m│[0m [1;37m     [0m[37m  [0m[37moutput the value. (usefull for shell scripting)                      [0m [2m│[0m
    [2m│[0m [1;37m     [0m[37m  [0m[37mExamples:                                                            [0m [2m│[0m
    [2m│[0m [1;37m     [0m[37m  [0m[37movos-config get [0m[91m-k[0m[37m lang                              # get all lang  [0m [2m│[0m
    [2m│[0m [1;37m     [0m[37m  [0m[37mkey values across the configuration                                  [0m [2m│[0m
    [2m│[0m [1;37m     [0m[37m  [0m[37movos-config get [0m[91m-k[0m[37m /tts/module                       # get the key at[0m [2m│[0m
    [2m│[0m [1;37m     [0m[37m  [0m[37mthe position specified                                               [0m [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Setting user values [0m[2m───────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36mset[0m[1;37m   [0m[37m   [0m[37mSets a config key in the user configuration                        [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37mLoosely searches a config key and if multiple are found asks which [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37mkey and value should be written.                                   [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37mThe user may pass a value to bypass prompting.                     [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37mExamples:                                                          [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37movos-config set [0m[91m-k[0m[37m gui                              # lists all    [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37mconfig keys containing "gui" (either as endpoint or in path),      [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37m                                                    # let the user [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37mchoose the specific key and asks for the value                     [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37movos-config set [0m[91m-k[0m[37m blacklisted_skills [0m[91m-v[0m[37m myskill    # Adds         [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37m"myskill" as an blacklisted skill                                  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37m                                                    # Since this is[0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37ma pretty specific key and a value is passed, the user won't be     [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m   [0m[37mprompted                                                           [0m [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Commands [0m[2m──────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36mautoconfigure[0m[1;36m [0m Automatically configures the language, STT, and TTS settings  [2m│[0m
    [2m│[0m [1;36m              [0m based on user input.                                          [2m│[0m
    [2m│[0m [1;36mtelemetry    [0m[1;36m [0m Enable intent telemetry upload for the opendata initiative.   [2m│[0m
    [2m│[0m [1;36m              [0m OpenData can be seen live at https://opendata.tigregotico.pt  [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    ```

??? example "`ovos-logs --help`"

    ```text
    [33mUsage:[0m [1movos-logs[0m [[31mOPTIONS[0m] [31mCOMMAND[0m [[31mARGS[0m]...                                   
                                                                                    
      Small helper tool to quickly navigate the logs, create slices and quickview   
     errors                                                                         
     [1;2;36;40movos-logs [COMMAND] --help[0m[2m for further information about the specific command [0m 
     [2mARGUMENTS[0m[2m [0m                                                                     
                                                                                    
    [2m╭─[0m[2m Options [0m[2m───────────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [31m--help[0m  Show this message and exit.                                          [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Slice logs by time [0m[2m────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36mslice[0m[1;37m  [0m[37m  [0m[37mOptionally define start ([0m[1;36;40m-s[0m[37m) and the time until ([0m[1;36;40m-u[0m[37m) the slice     [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[37mshould be limited to.                                              [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[37mDifferent logs can be included using the [0m[1;36;40m-l[0m[37m option. If not         [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[37mspecified, all logs will be included.                              [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[37mOptionally the directory where the logs are stored ([0m[1;36;40m-p[0m[37m) and the    [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[37mfile where the slices should be dumped ([0m[1;36;40m-f[0m[37m) can be specified.      [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[37m                                                                   [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[35m▌ [0m[35mExamples:[0m[35m                                                      [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[35m▌ [0m[35movos-logs slice                                            # [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[35m▌ [0m[35mSlice all logs from service start up until now[0m[35m                 [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[35m▌ [0m[35movos-logs slice -s 01-12-2023 -u '01-12-2023 17:00:20'     # [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[35m▌ [0m[35mSlice all logs from the start of december the first until [0m[35m     [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[35m▌ [0m[35m17:00:20[0m[35m                                                       [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[35m▌ [0m[35movos-logs slice -l bus -l skills -f ~/myslice.log          # [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[35m▌ [0m[35mSlice skills.log and bus.log from service start up until now [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m  [0m[35m▌ [0m[35mand dump it to the file ~/myslice.log[0m[35m                          [0m[37m  [0m [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m List logs by severity [0m[2m─────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36mlist[0m[1;37m  [0m[37m  [0m[37mLog level has to be specified.                                      [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mOptionally define start ([0m[1;36;40m-s[0m[37m) and the time until ([0m[1;36;40m-u[0m[37m) the slice      [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mshould be limited to.                                               [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mDifferent logs can be included using the [0m[1;36;40m-l[0m[37m option. If not          [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mspecified, all logs will be included.                               [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mOptionally the directory where the logs are stored ([0m[1;36;40m-p[0m[37m) and the file[0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mwhere the slices should be dumped ([0m[1;36;40m-f[0m[37m) can be specified.            [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37m                                                                    [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35mExamples:[0m[35m                                                       [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35movos-logs list -x                                           # [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35mList all exceptions from service start up until now[0m[35m             [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35movos-logs list -e -w -s 01-12-2023 -u '01-12-2023 17:00:20' # [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35mList all errors and warnings from the start of december the [0m[35m    [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35mfirst until 17:00:20[0m[35m                                            [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35movos-logs list -x -l bus -l skills -f                       # [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35mList all exceptions from skills.log and bus.log and dump it to [0m[35m [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35mthe file ~/list_xxx_xxx.log[0m[35m                                     [0m[37m  [0m [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Downsize logs [0m[2m─────────────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36mreduce[0m[1;37m [0m[37m [0m[37mReduce logs to a given size (in bytes) or remove entries before a   [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[37mgiven date.                                                         [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[37mDifferent logs can be included using the [0m[1;36;40m-l[0m[37m option. If not          [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[37mspecified, all logs will be included.                               [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[37mOptionally the directory where the logs are stored ([0m[1;36;40m-p[0m[37m) can be      [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[37mspecified.                                                          [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[37m                                                                    [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[35m▌ [0m[35mExamples:[0m[35m                                                       [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[35m▌ [0m[35movos-logs reduce                                            # [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[35m▌ [0m[35mReduce all logs to 0 bytes[0m[35m                                      [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[35m▌ [0m[35movos-logs reduce -s 1000000                                 # [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[35m▌ [0m[35mReduce all logs to ~1MB (latest logs)[0m[35m                           [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[35m▌ [0m[35movos-logs reduce -d "1-12-2023 17:00"                       # [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[35m▌ [0m[35mReduce all logs to entries after the specified date/time[0m[35m        [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[35m▌ [0m[35movos-logs reduce -s 1000000 -l skills -l bus                # [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m       [0m[37m [0m[35m▌ [0m[35mReduce skills.log and bus.log to ~1MB (latest logs)[0m[35m             [0m[37m  [0m [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    [2m╭─[0m[2m Show logs (using less) [0m[2m────────────────────────────────────────────────────[0m[2m─╮[0m
    [2m│[0m [1;36mshow[0m[1;37m  [0m[37m  [0m[37mA service log has to be specified ([0m[1;36;40m-l[0m[37m).                             [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mOptionally the directory where the logs are stored ([0m[1;36;40m-p[0m[37m) can be      [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37mspecified.                                                          [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[37m                                                                    [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35mExamples:[0m[35m                                                       [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35movos-logs show -l skills                                    # [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35mDisplay skills.log[0m[35m                                              [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35movos-logs show -l debug -p ~/custom_path/                   # [0m[35m  [0m[37m  [0m [2m│[0m
    [2m│[0m [1;37m      [0m[37m  [0m[35m▌ [0m[35mDisplay debug.log from a custom path[0m[35m                            [0m[37m  [0m [2m│[0m
    [2m╰──────────────────────────────────────────────────────────────────────────────╯[0m
    ```
<!-- END GENERATED -->

---

*Source code: [OpenVoiceOS/ovos-config](https://github.com/OpenVoiceOS/ovos-config), [OpenVoiceOS/ovos-bus-client](https://github.com/OpenVoiceOS/ovos-bus-client), and [OpenVoiceOS/ovos-utils](https://github.com/OpenVoiceOS/ovos-utils).*

---
**Read next:** [Core Libraries](core-libraries.md)
**Related:** [ovos-docs-viewer](docs-viewer.md) · [i2c Sound & Audio Setup](i2c-sound.md) · [Troubleshooting & Debugging](troubleshooting.md) · [Contributing](contributing.md)
