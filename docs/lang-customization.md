# Customizing Language Resources

OpenVoiceOS allows users and developers to override or extend language resources (dialogs, intents, and vocabulary) without modifying the original skill or core code. This is particularly useful for localizing responses, fixing intent matching for your specific accent, or adding support for a new language.

---

## Skill Resource Overrides

OVOS skills load their resources (found in the `locale/` or `vocab/dialog/` directories) using a prioritized search path. You can place your custom files in the following XDG-compliant directory to override anything shipped with a skill:

**Path:** `~/.local/share/mycroft/resources/{skill_id}/{lang}/`

### How to Override
1.  **Identify the Skill ID**: Find the ID of the skill you want to customize (e.g., `ovos-skill-weather.openvoiceos`).
2.  **Create the Directory**: Create the folder structure matching the skill ID and your language code.
3.  **Copy and Edit**: Copy the `.dialog` or `.intent` file from the skill's source and place it in your local override directory.
4.  **Restart**: Restart `ovos-core` to pick up the changes.

!!! tip "Partial Overrides"
    You don't need to copy every file. Only place the specific files you want to change in the override directory. The system will fall back to the original skill files for anything missing locally.

---

## System-wide Resource Overrides

For core system resources (like the "boot finished" sound or common error dialogs), OVOS checks the following paths in order:

1.  **User Folder**: `~/.mycroft/res/`
2.  **System Folder**: `/opt/mycroft/res/`
3.  **Package Defaults**: Bundled resources inside `ovos-utils` or `ovos-workshop`.

You can place custom `.wav` sounds or `.dialog` files here to change the system's "personality" or branding.

---

## Customizing Language Names and Parsers

The technical parsers for numbers, dates, and language names can also be extended.

### Language Name Mapping
The `ovos-lang-parser` library uses JSON files to map BCP-47 codes to spoken names. While these are usually contributed upstream, you can fix local issues by modifying the `langs.json` in your local environment's package path (though this is less persistent than skill overrides).

### Number and Date Parsing
These libraries are highly dependent on language-specific rule files. If you find that "22nd" isn't parsing correctly in your language, you can contribute improved rules to the respective `ovos-number-parser` or `ovos-date-parser` repositories.
