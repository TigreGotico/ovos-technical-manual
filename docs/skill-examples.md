# What Can I Say? — Default Skills Overview

!!! abstract "In a nutshell"
    A "skill" is an add-on that teaches your assistant to do one thing — tell the weather, set an
    alarm, play the radio, answer trivia. This page is a browsable catalog of ready-made skills you
    can add to OVOS, grouped by what they're for, each with real example phrases and how to install
    it. Some come pre-loaded depending on how you set OVOS up; others you add yourself. See
    [Your First Skill](first-skill.md) if you want to build your own, or the
    [Glossary](glossary.md) for terms.

A non-exhaustive list of skills available for OpenVoiceOS. Whether a given skill is already on your
assistant depends on how you installed it — see the legend below.

!!! tip "How to get a skill"
    Many of these ship with the [`ovos-installer`](ovos-installer.md)'s skill selection. To add
    one yourself, install its package (the repo link and `pip install` command are in the
    collapsed "Install" block under each skill below) and restart `ovos-core` — it scans for
    installed skills automatically. If a skill isn't published to PyPI, install straight from
    git, e.g. `pip install git+https://github.com/OpenVoiceOS/ovos-skill-weather`. To build your
    own, follow [Your First Skill](first-skill.md).

!!! info "Availability legend"
    - 🟢 **Installer default** — installed automatically when the `ovos-installer`'s `skills`
      feature is on (the default).
    - 🟡 **Installer optional** — installed only if you also enable the installer's
      `extra-skills` feature.
    - ⚪ **Manual install only** — not offered by the installer at all; add it yourself with
      `pip install`.

---

## Alerts (Timers, Reminders & Alarms)

🟢 **Installer default**

A skill to manage alarms, timers, reminders, events and todos and optionally sync them with a
CalDAV service. Handy if you want a hands-free alarm clock, kitchen timer, or todo list that
survives a reboot and can sync with an external calendar.

**Usage examples:**

- What are my reminders?
- Cancel all reminders.
- When is my next alarm?
- Schedule a tennis event for 2 PM on friday spanning 2 hours.
- What did I miss?
- remind me to take out the trash every Thursday and Sunday at 7 PM.
- Start a bread timer for 30 minutes.
- Did I miss anything?
- Set an alarm for 8 AM.
- Set a daily alarm for 8 AM.

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-alerts](https://github.com/OpenVoiceOS/ovos-skill-alerts) · `pip install ovos-skill-alerts`

-------

## Date & Time

🟢 **Installer default**

Get the current time, date, or information about specific calendar days.

**Usage examples:**

- What time is it?
- Tell me the day of the week
- What day is Memorial Day 2020?
- What's the date?
- Show me the time
- How many days until July 4th
- What time is it in Paris?

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-date-time](https://github.com/OpenVoiceOS/ovos-skill-date-time) · `pip install ovos-skill-date-time`

-------

## Naptime (Snooze the Assistant)

🟢 **Installer default**

Put the assistant to sleep when you don't want to be disturbed. While asleep, the wake word stops
triggering listening — say "Wake up" (or the configured stand-up word) to bring it back.

**Usage examples:**

- Nap time
- Wake up
- Go to sleep

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-naptime](https://github.com/OpenVoiceOS/ovos-skill-naptime) · `pip install ovos-skill-naptime`

-------

## Weather

🟢 **Installer default**

Get weather conditions, forecasts, expected precipitation and more! You can also ask for other
cities around the world. Current conditions and weather forecasts come from OpenMeteo.

**Usage examples:**

- What's the temperature in Paris tomorrow in Celsius?
- When will it rain next?
- What's the high temperature tomorrow
- Is it going to snow in Baltimore?
- what is the weather like?
- How windy is it?
- What is the weather this weekend?
- What is the weather in Houston?
- Will it be cold on Tuesday
- What's the temperature?

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-weather](https://github.com/OpenVoiceOS/ovos-skill-weather) · `pip install ovos-skill-weather`

-------

## Smart Home

Controlling actual smart-home devices (lights, plugs, thermostats, scenes) isn't built into OVOS
itself — it's a separate skill that talks to [Home Assistant](https://www.home-assistant.io/).
See [OVOS & Home Assistant](home-assistant.md) for the full setup story in both directions
(OVOS controlling HA devices, and HA using OVOS's own speech engines).

⚪ **Manual install only** (or enable the installer's `homeassistant` feature, which installs and
configures it for you)

The `skill-homeassistant` skill (maintained by OscillateLabs) lets OVOS control your Home
Assistant devices by voice once you've pointed it at your HA instance's URL and a long-lived
access token.

**Usage examples** (exact phrasing depends on how your devices/areas are named in Home Assistant):

- Turn on the living room lights.
- Turn off the kitchen lights.
- Set the thermostat to 20 degrees.
- Activate the movie night scene.

??? note "Install"
    [:material-github: OscillateLabsLLC/skill-homeassistant](https://github.com/OscillateLabsLLC/skill-homeassistant) · `pip install skill-homeassistant` — or tick `homeassistant` in the [ovos-installer](ovos-installer.md#feature-selection) feature list, which prompts for the URL and token for you.

-------

## Music & Radio

### PyRadios

🟡 **Installer optional** (`extra-skills` feature)

A client for the Radio Browser API — a large, community-maintained directory of internet radio
stations.

**Usage examples:**

- play tsf jazz on pyradios
- play tsf jazz radio

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-pyradios](https://github.com/OpenVoiceOS/ovos-skill-pyradios) · `pip install ovos-skill-pyradios`

### SomaFM

🟡 **Installer optional** (`extra-skills` feature)

Listen to a variety of commercial-free internet radio stations from SomaFM.

**Usage examples:**

- play soma fm radio
- play metal detector
- play secret agent

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-somafm](https://github.com/OpenVoiceOS/ovos-skill-somafm) · `pip install ovos-skill-somafm`

### News

🟡 **Installer optional** (`extra-skills` feature)

News streams from around the globe.

**Usage examples:**

- play npr news
- play news in spanish
- play euronews
- play the news
- play portuguese news
- play catalan news

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-news](https://github.com/OpenVoiceOS/ovos-skill-news) · `pip install ovos-skill-news`

### Local Media

🟡 **Installer optional** (`extra-skills` feature)

Local media file browser for OpenVoiceOS — browse and play audio/video files from a USB drive or
local folder.

**Usage examples:**

- open my file browser
- show my file browser
- show my usb drive
- start usb browser app
- show my usb
- show file browser app
- show file browser
- open usb
- start usb browser
- open my usb

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-local-media](https://github.com/OpenVoiceOS/ovos-skill-local-media) · `pip install ovos-skill-local-media`

!!! note "Playing your own music or a streaming service"
    Out of the box, OVOS plays internet radio (PyRadios, SomaFM) and local files — it does not
    include Spotify or another streaming-service player by default. See
    [Cool Things You Can Do](showcase.md) and [Media Plugins](media-plugins.md) for what's
    available to add.

-------

## Fun & Trivia

### Dad Jokes

🟡 **Installer optional** (`extra-skills` feature)

Brighten your day with dad humor. Laughter is not guaranteed, but eye rolls are likely.

**Usage examples:**

- Can you tell jokes?
- Make me laugh.
- Do you know any Chuck Norris jokes?
- Tell me a joke about dentists.
- Say a joke.
- Tell me a joke.
- Do you know any jokes?

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-icanhazdadjokes](https://github.com/OpenVoiceOS/ovos-skill-icanhazdadjokes) · `pip install ovos-skill-icanhazdadjokes`

### Parrot

🟢 **Installer default**

Turn OpenVoiceOS into an echoing parrot! Make OVOS repeat whatever you want.

**Usage examples:**

- Tell me what I just said.
- say Goodnight, Gracie
- speak I can say anything you'd like!
- start parrot
- repeat Once upon a midnight dreary, while I pondered, weak and weary, Over many a quaint and curious volume of forgotten lore
- Repeat what you just said
- What did I just say?
- Can you repeat that?
- stop parrot
- Repeat that

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-parrot](https://github.com/OpenVoiceOS/ovos-skill-parrot) · `pip install ovos-skill-parrot`

### Confucius Quotes

⚪ **Manual install only**

Quotes from Confucius.

**Usage examples:**

- Quote from Confucius
- When did Confucius die
- When was Confucius born
- Who is Confucius

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-confucius-quotes](https://github.com/OpenVoiceOS/ovos-skill-confucius-quotes) · `pip install ovos-skill-confucius-quotes`

### Today in History

⚪ **Manual install only**

Provides historical events for today or any other calendar day using information pulled from
Wikipedia.

**Usage examples:**

- who died today in history?
- who was born today in history?
- What historical events happened on June 16th?
- Tell me about events in history on December 12th
- What happened today in history?

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-days-in-history](https://github.com/OpenVoiceOS/ovos-skill-days-in-history) · `pip install ovos-skill-days-in-history`

### Number Facts

⚪ **Manual install only**

Facts about numbers.

**Usage examples:**

- random number trivia
- trivia about next week
- trivia about tomorrow
- fact about number 666
- fact about yesterday
- curiosity about year 1992
- math fact about number 7

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-number-facts](https://github.com/OpenVoiceOS/ovos-skill-number-facts) · `pip install ovos-skill-number-facts`

### Movie Master

⚪ **Manual install only**

Find information about movies, actors, and production details. Easily find information about a
movie with your voice.

**Usage examples:**

- What are popular movies playing now?
- Tell me about the movie _______
- What genres does the flick _______ belong to?
- Who plays in the movie _______?
- How long is the movie _______?
- Look for information on the movie _______.
- Do you have info on the film _______?
- What is the movie _______ about?
- What are the highest rated movies out?
- When was the movie _______ made?

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-moviemaster](https://github.com/OpenVoiceOS/ovos-skill-moviemaster) · `pip install ovos-skill-moviemaster`

### ISS Location

⚪ **Manual install only**

Track the location of the International Space Station.

**Usage examples:**

- When is the ISS passing over
- Where is the ISS
- Tell me about the ISS
- how many persons on board of the space station
- Who is on board of the space station?

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-iss-location](https://github.com/OpenVoiceOS/ovos-skill-iss-location) · `pip install ovos-skill-iss-location`

### DuckDuckGo

🟢 **Installer default**

Use DuckDuckGo to answer questions.

**Usage examples:**

- ask the duck about the big bang
- when was stephen hawking born
- who is elon musk

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-ddg](https://github.com/OpenVoiceOS/ovos-skill-ddg) · `pip install ovos-skill-ddg`

### Wikipedia

🟢 **Installer default**

Query Wikipedia for answers to all your questions. Get just a summary, or ask for more to get
in-depth information.

**Usage examples:**

- Search for chocolate
- More information
- Tell me about beans
- Tell me More
- Tell me about the Pembroke Welsh Corgi
- Check Wikipedia for beans
- Tell me about Elon Musk

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-wikipedia](https://github.com/OpenVoiceOS/ovos-skill-wikipedia) · `pip install ovos-skill-wikipedia`

### WikiHow

🟢 **Installer default**

How to do nearly everything.

**Usage examples:**

- how do i get my dog to stop barking
- how to boil an egg

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-wikihow](https://github.com/OpenVoiceOS/ovos-skill-wikihow) · `pip install ovos-skill-wikihow`

### Wolfie (Wolfram Alpha)

🟢 **Installer default**

Use Wolfram Alpha for general knowledge questions.

**Usage examples:**

- How tall is Mount Everest?
- What's 18 times 4?
- How many inches in a meter?
- What is Madonna's real name?
- When was The Rocky Horror Picture Show released?
- ask the wolf what is the speed of light

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-wolfie](https://github.com/OpenVoiceOS/ovos-skill-wolfie) · `pip install ovos-skill-wolfie`

### Wordnet

⚪ **Manual install only**

Use Wordnet to answer dictionary-like questions.

**Usage examples:**

- what is the definition of ...
- what is the antonym of ...

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-wordnet](https://github.com/OpenVoiceOS/ovos-skill-wordnet) · `pip install ovos-skill-wordnet`

### Spelling

🟢 **Installer default**

Provides the spelling of words and phrases upon request.

**Usage examples:**

- How do you spell bureaucracy?
- How do you spell aardvark?
- Spell omnipotence
- Spell succotash

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-spelling](https://github.com/OpenVoiceOS/ovos-skill-spelling) · `pip install ovos-skill-spelling`

### Personal

🟢 **Installer default**

Learn history and personality of the assistant. Ask about the 'birth' and parentage of the voice
assistant and get a taste of the community who is fostering this open source artificial
intelligence.

**Usage examples:**

- Where were you born?
- What are you?
- When were you created?
- Who made you?

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-personal](https://github.com/OpenVoiceOS/ovos-skill-personal) · `pip install ovos-skill-personal`

### Hello World

🟢 **Installer default**

Introductory [skill](skill-design-guidelines.md) so that skill authors can see how an OVOS skill
is put together.

**Usage examples:**

- Hello world
- Thank you
- How are you?

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-hello-world](https://github.com/OpenVoiceOS/ovos-skill-hello-world) · `pip install ovos-skill-hello-world`

-------

## Utilities (System & Voice Control)

### Volume

🟢 **Installer default**

Control the volume of OVOS with verbal commands.

**Usage examples:**

- unmute volume
- volume low
- mute audio
- volume to high level
- reset volume
- volume to high
- volume level low
- toggle audio
- low volume
- set volume to maximum

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-volume](https://github.com/OpenVoiceOS/ovos-skill-volume) · `pip install ovos-skill-volume`

### IP Address

🟢 **Installer default**

Network connection information.

**Usage examples:**

- What's your IP address?
- What's your network address?
- Tell me your network address
- What network are you connected to?
- Tell me your IP address

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-ip](https://github.com/OpenVoiceOS/ovos-skill-ip) · `pip install ovos-skill-ip`

### Speedtest

🟢 **Installer default**

Runs an internet bandwidth test using speedtest.net.

**Usage examples:**

- run a speedtest

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-speedtest](https://github.com/OpenVoiceOS/ovos-skill-speedtest) · `pip install ovos-skill-speedtest`

### Boot Finished

🟢 **Installer default**

Provides notifications when OpenVoiceOS has fully started and all core services are ready. It
listens for the `mycroft.ready` bus event (emitted once every core service reports ready) and
speaks a short confirmation — useful on headless devices where you can't otherwise tell startup
finished.

**Usage examples:**

- Disable ready notifications.
- Is the system ready?
- Enable ready notifications.

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-boot-finished](https://github.com/OpenVoiceOS/ovos-skill-boot-finished) · `pip install ovos-skill-boot-finished`

### Dictation

🟢 **Installer default**

Continuously transcribes user speech to a text file while enabled.

**Usage examples:**

- start dictation
- end dictation

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-dictation](https://github.com/OpenVoiceOS/ovos-skill-dictation) · `pip install ovos-skill-dictation`

### Audio Recording

🟢 **Installer default**

Record and manage audio clips directly from your assistant.

**Usage examples:**

- new recording named {name}
- start recording
- start a recording called {name}
- start a new audio recording called {name}
- begin recording

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-audio-recording](https://github.com/OpenVoiceOS/ovos-skill-audio-recording) · `pip install ovos-skill-audio-recording`

### Commands

⚪ **Manual install only**

Allows you to execute shell scripts and system commands via voice. Useful for headless boxes
where you want a voice shortcut to a maintenance script instead of SSHing in.

**Usage examples:**

- run script ___
- launch command ___

??? note "Install"
    [:material-github: OpenVoiceOS/ovos-skill-cmd](https://github.com/OpenVoiceOS/ovos-skill-cmd) · `pip install ovos-skill-cmd`
