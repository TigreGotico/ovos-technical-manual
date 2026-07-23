# Make It Yours

!!! abstract "In a nutshell"
    You just installed OVOS and it works — now you want it to sound like *your* assistant: a
    different name to wake it up, a different voice answering you, or a different language
    altogether. All three are small edits to the same file, `~/.config/mycroft/mycroft.conf`.
    This page is a quick-reference for all three; each section links to the full page with
    more detail and more options.

!!! tip "Want to do this by voice instead of editing files?"
    Everything below needs opening a text file and a restart. If you'd rather change your wake
    word, voice, or volume by *talking* to your assistant, see
    [What can I say?](skill-examples.md) and [It's Not Working — Quick Fixes](everyday-help.md)
    for what's already possible hands-free (e.g. volume) versus what still needs a config edit
    (wake word, voice, language).

All the settings below live in your personal config file at
**`~/.config/mycroft/mycroft.conf`** (create it if it doesn't exist yet — see
[Configuration Management](config.md) for how the layering works). It's JSON with comments
allowed (JSONC). Open it with any text editor, for example:

```bash
nano ~/.config/mycroft/mycroft.conf
```

Before restarting, double-check the file still parses — a stray missing comma or bracket will
stop it from loading. Because `mycroft.conf` allows `//` comments, plain `json.tool` will
reject it even when it's fine — use the same comment-aware loader OVOS itself uses:

```bash
python3 -c "from ovos_utils.json_helper import load_commented_json; load_commented_json('$HOME/.config/mycroft/mycroft.conf'); print('OK')"
```

This prints `OK` if the file is valid, or a `JSONDecodeError` with a line/column pointing at the
mistake if it isn't. You can also confirm a specific value actually took effect after restarting
with `ovos-config show --section <name>` (see [Configuration Management](config.md#cli-reference)
for the full CLI). Once the file parses cleanly, apply the change:

--8<-- "snippets/restart-ovos.md"

## Change your wake word

```json
{
  "listener": { "wake_word": "hey_computer" },
  "hotwords": {
    "hey_computer": { "module": "ovos-ww-plugin-vosk", "listen": true }
  }
}
```

Full walkthrough, plugin choices, and tuning: [Wake Word Plugins](wake-word-plugins.md#change-your-wake-word).

## Change your voice

```json
{
  "tts": {
    "module": "ovos-tts-plugin-piper",
    "ovos-tts-plugin-piper": { "voice": "en_US-amy-low" }
  }
}
```

Browse voice samples and see every available plugin: [TTS Plugins](tts-plugins.md#change-your-voice).

## Change your language

```json
{
  "lang": "de-de"
}
```

This one line is enough on its own — STT, TTS, and every language-aware plugin follow the
global `lang` automatically. Want the *recommended* plugins/voices for that language instead
of your current ones? Run `ovos-config autoconfigure -l de-de --offline` afterwards. Full
picture, supported-language table, and gaps to watch for: [Language Support](lang-support.md).

## Related pages

- [Configuration Management](config.md) — how the config layers stack, and the full CLI
- [Wake Word Plugins](wake-word-plugins.md) — every available wake-word engine
- [TTS Plugins](tts-plugins.md) — every available voice engine
- [Language Support](lang-support.md) — translation coverage and per-language plugin gaps
