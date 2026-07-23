# settingsmeta.json

!!! abstract "In a nutshell"
    This optional file describes a form for configuring your skill — labeled boxes, checkboxes,
    and drop-downs on a settings screen — so a tool can render a settings UI without you writing
    one. **Heads-up: this is a legacy format and most OVOS skills don't ship it.** It came from
    the old Mycroft backend, which OVOS doesn't run; your skill's settings work fine without it
    (see [Skill Settings](skill-settings.md)). It only matters if you use a community tool that
    reads it. For term definitions see the [Glossary](glossary.md).

!!! warning "Legacy — specified but not used by OVOS itself"
    `settingsmeta.json` / `.yaml` is a **legacy format inherited from the Mycroft backend
    server**, which presented a web form to edit skill settings. **OVOS does not run that backend**,
    so nothing in OVOS core consumes this file, and it is **optional and usually absent** in modern
    skills. Your skill reads and writes its settings perfectly well without it — see
    [Skill Settings](skill-settings.md).

    It is still *specified* (and `ovos-workshop` can auto-generate a basic version from a skill's
    settings), and some **community tools still consume it to render a settings UI** — most notably
    [`ovos-skill-config-tool`](https://github.com/OscillateLabsLLC/ovos-skill-config-tool) by
    Oscillate Labs. Provide a `settingsmeta` file only if you specifically target such a tool; the
    rest of this page documents the format for that case.

## Define settings UI for a [Skill](skill-design-guidelines.md)

To define a Skill's settings UI you can provide a `settingsmeta.json` or `settingsmeta.yaml` file.
When present, it lives in the root directory of the Skill and follows the structure below.

A `settingsmeta` file does nothing on its own — it is only meaningful to a tool that reads it (a
community settings editor like the one above), which then presents the described fields to the user.

### Example settingsmeta file

To see it in action, here is a simple example, similar to what a legacy date-and-time skill might ship. First using the JSON syntax as a `settingsmeta.json` file:

```javascript
{
    "skillMetadata": {
        "sections": [
            {
                "name": "Display",
                "fields": [
                    {
                        "name": "show_time",
                        "type": "checkbox",
                        "label": "Show digital clock when idle",
                        "value": "true"
                    }
                ]
            }
        ]
    }
}

```

Now, here is the same settings, as it would be defined with YAML in a `settingsmeta.yaml` file:

```yaml
skillMetadata:
   sections:

      - name: Display
        fields:

          - name: show_time
            type: checkbox
            label: Show digital clock when idle
            value: "true"

```

Notice that the checkbox's value, `"true"`, is a quoted string rather than a bare YAML/JSON boolean. This is intentional — the format expects the literal string `"true"` or `"false"`, not a real boolean.

Both of these files would result in the same settings block.


It is up to your personal preference which syntax you choose.

### Structure of the settingsmeta file

Whilst the syntax differs, the structure of these two filetypes is the same. This starts at the top level of the file by defining a `skillMetadata` object. This object must contain one or more `sections` elements.

#### Sections

Each section represents a group of settings that logically sit together. This enables us to display the settings more clearly in the web interface for users.

In the simple example above we have just one section. A skill that needs more configuration might use several — for example, one section for account authentication and a separate section for playback preferences.

Each section must contain a `name` attribute that is used as the heading for that section, and an Array of `fields`.

#### Fields

Each section has one or more `fields`. Each field is a setting available to the user. Each field takes four properties:

*   `name` (String)

    The `name` of the `field` is used by the Skill to get and set the value of the `field`. It will not usually be displayed to the user, unless the `label` property has not been set.

*   `type` (Enum)

    The data type of this field. The supported types are:

    * `text`: any kind of text


    * `email`: text validated as an email address


    * `checkbox`: boolean, True or False


    * `number`: text validated as a number


    * `password`: text hidden from view by default


    * `select`: a drop-down menu of options


    * `label`: special field to display text for information purposes only. No name or value is required for a `label` field.


*   `label` (String)

    The text to be displayed above the setting field.

*   `value` (String)

    The initial value of the field.

Examples for each type of field are provided in JSON and YAML at the end of this page.


## SettingsMeta Examples

### Label Field

```yaml
skillMetadata:
   sections:

      - name: Label Field Example
        fields:

          - type: label
            label: This is descriptive text.

```

### Text Field

```yaml
skillMetadata:
   sections:

      - name: Text Field Example
        fields:

          - name: my_string
            type: text
            label: Enter any text
            value:

```

### Email

```yaml
skillMetadata:
   sections:

      - name: Email Field Example
        fields:

          - name: my_email_address
            type: email
            label: Enter your email address
            value:

```


### Checkbox

```yaml
skillMetadata:
   sections:

      - name: Checkbox Field Example
        fields:

          - name: my_boolean
            type: checkbox
            label: This is an example checkbox. It creates a Boolean value.
            value: "false"

```

### Number

```yaml
skillMetadata:
   sections:

      - name: Number Field Example
        fields:

          - name: my_number
            type: number
            label: Enter any number
            value: 7

```


### Password

```yaml
skillMetadata:
   sections:

      - name: Password Field Example
        fields:

          - name: my_password
            type: password
            label: Enter your password
            value:

```

### Select

```yaml
skillMetadata:
   sections:

      - name: Select Field Example
        fields:

          - name: my_selected_option
            type: select
            label: Select an option
            options: Option 1|option_one;Option 2|option_two;Option 3|option_three
            value: option_one

```

---

*Source code: [OpenVoiceOS/ovos-workshop](https://github.com/OpenVoiceOS/ovos-workshop).*
