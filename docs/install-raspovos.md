# RaspOVOS: A Beginner's Guide to Setting Up Your Raspberry Pi with OVOS

!!! abstract "In a nutshell"
    This is a step-by-step guide to turning a Raspberry Pi (a small, inexpensive computer) into a working OVOS voice assistant by flashing a ready-made "RaspOVOS" image onto an SD card or USB drive. It walks you through hardware choices, writing the image, first boot, connecting to Wi-Fi, and the handy commands you'll use afterward. Heads-up: these pre-built images are now **outdated** — for a fresh install the recommended path is the [`ovos-installer`](ovos-installer.md) instead. See the [Glossary](glossary.md) for unfamiliar terms.

!!! warning "Not currently recommended"
    The pre-built **RaspOVOS** images are **outdated** and **not recommended** for new
    installs right now. For a Raspberry Pi (or any Linux device), use the
    **[`ovos-installer`](ovos-installer.md)** instead — it runs on Raspberry Pi OS and
    is the supported way to get a current OVOS stack. This page is kept for existing
    RaspOVOS users and for reference.

This tutorial is designed for users new to Raspberry Pi and RaspOVOS. Follow these steps to set up and optimize your device for the best experience.

---

## Step 1: Prepare Your Hardware

### Raspberry Pi Model Recommendations

- **Recommended:** Raspberry Pi 4 or 5.


    - For offline [STT](stt-plugins.md) (speech-to-text), the **Raspberry Pi 5** offers significant performance improvements.


- **Minimum Requirement:** Raspberry Pi 3.


    - **Note:** The Raspberry Pi 3 will work but may be **extremely slow** compared to newer models.

### Storage Options

- **SD Card or USB Storage:**


    - You can use either a microSD card or a USB drive.


- **Recommended:** USB SSD Drive for maximum speed and performance.


    - Connect the USB drive to the **blue USB 3.0 port** for optimal performance.

### Power Supply Considerations
Raspberry Pi boards are notoriously **picky about power supplies**. Insufficient power can lead to performance issues, random reboots, or the appearance of the **undervoltage detected** warning (a lightning bolt symbol in the top-right corner of the screen).

- **Recommended Power Supplies:**


    - Raspberry Pi 4: 5V 3A USB-C power adapter.


    - Raspberry Pi 5: Official Raspberry Pi 5 USB-C power adapter or equivalent high-quality adapter with sufficient current capacity.


- **Common Issues:**


    - Using cheap or low-quality chargers or cables may result in voltage drops.


    - Long or thin USB cables can cause resistance, reducing the power delivered to the board.


- **How to Fix:**


    - Always use the official power adapter or a trusted brand with a stable 5V output.


    - If you see the **"undervoltage detected"** warning, consider replacing your power supply or cable.

---

## Step 2: Install RaspOVOS Image

1. **Download and Install Raspberry Pi Imager**


    - Visit [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and download the appropriate version for your OS.


    - Install and launch the imager.


2. **Flash the Image to Storage**


    - Insert your SD card or USB drive into your computer.


    - In the Raspberry Pi Imager:


        - **Choose OS:** Select "Use custom" and locate the RaspOVOS image file.


        - **Choose Storage:** Select your SD card or USB drive.


![image](https://github.com/user-attachments/assets/92458289-a3c3-4c7b-afc8-126881445f9f)

![image](https://github.com/user-attachments/assets/36a83d0a-ebc2-4095-94ba-604ad78b5452)

![image](https://github.com/user-attachments/assets/47c92497-d1a2-4f2d-90be-189806736c0d)

3. **Advanced Configuration Options**


    - Click **Next** and select **Edit Settings** to customize settings, including:


        - **Password:** Change the default password.


        - **Hostname:** Set a custom hostname for your device.


        - **Wi-Fi Credentials:** Enter your Wi-Fi network name and password.


        - **Keyboard Layout:** Configure the correct layout for your region.

   **Important:** **Do NOT change the default username** (`ovos`), as it is required for the system to function properly.

![image](https://github.com/user-attachments/assets/9509ea57-ae46-4c0b-b9e9-97935579d207)

![image](https://github.com/user-attachments/assets/252af1a0-54dc-4450-aa4a-eb0f0a4d139f)

4. **Write the Image**


    - Click **Save** and then **Yes** to flash the image onto your storage device.


    - Once complete, safely remove the SD card or USB drive from your computer.

---

## Step 3: Initial Setup and First Boot

### Connect and Power On

- Insert the SD card or connect the USB drive to your Raspberry Pi.


- Plug in the power supply and connect an HDMI monitor to observe the boot process.

### First Boot Process

1. **Initialization:**


    - The system will expand the filesystem, generate SSH keys, and perform other setups.


2. **Reboots:**


    - The device will reboot **up to three times** during this process.


3. **Autologin:**


    - The `ovos` user will automatically log in to the terminal after boot.


4. **Check System Status:**


    - Use the `ologs` command to monitor logs and confirm that the system has fully initialized.

---

## Step 4: Setting Up Wi-Fi

### Option 1: Configure Wi-Fi Using Raspberry Pi Imager
The most straightforward method is to set up Wi-Fi during the imaging process.

1. Open Raspberry Pi Imager and select Edit Settings Option.


2. Enter your **SSID (Wi-Fi network name)** and **password** in the Wi-Fi configuration fields.


3. Write the image to your SD card or USB drive, and your Wi-Fi will be pre-configured.

### Option 2: Use Audio-Based Wi-Fi Setup (ggwave)

1. Open [ggwave Wi-Fi setup](https://openvoiceos.github.io/ovos-audio-transformer-plugin-ggwave/) on a device with speakers.


2. Enter your **SSID** and **password** and transmit the data as sound.


3. Place the transmitting device near the Raspberry Pi microphone.


4. If successful, you'll hear an acknowledgment tone.


    - If decoding fails or credentials are incorrect, you'll hear an error tone.

🚧 **Note:** ggwave is a **work-in-progress** feature and does not have any dialogs or provide on-screen feedback. 🚧

![image](https://github.com/user-attachments/assets/ce2857b1-b93f-4092-99f3-43f555e04920)

---

## Step 5: Running OVOS

### OVOS First Launch

- On the first run, OVOS may take longer to initialize.


- When ready, OVOS will say: **"I am ready"** (requires an Internet connection).

---

## Step 6: Using OVOS Commands

### Helpful Commands

When you log in, RaspOVOS prints a welcome banner listing its built-in helper commands. These
are **RaspOVOS-specific shell helpers** (aliases and small scripts baked into the image) — they
are part of the RaspOVOS image, not a standard `pip install` of OVOS. Run `ovos-help` at any time
to reprint the full list.

**Web interfaces:**

- `ovos-yaml-editor` — web editor for OVOS configuration (port 9210).
- `ovos-skill-config-tool` — web editor for individual skill settings (port 8000).

**Talking to OVOS:**

- `ovos-config` — manage your local OVOS configuration files.
- `ovos-listen` — activate the microphone to listen for a command.
- `ovos-speak <phrase>` — have OVOS speak a phrase to the user.
- `ovos-say-to <phrase>` — send an utterance to OVOS as if you had spoken it.
- `ovos-simple-cli` — chat with your device from the terminal.
- `ovos-docs-viewer` — open the documentation viewer (also `ovos-manual`, `ovos-skills-info`).

**Managing packages:**

- `ovos-install` — install OVOS packages with the correct version constraints.
- `ovos-update` — update all OVOS and skill packages.
- `ovos-force-reinstall` — force a full reinstall of all OVOS packages (last-resort repair).
- `ovos-freeze` — export installed OVOS packages to `requirements.txt`.
- `ovos-outdated` — list outdated OVOS/skill packages.
- `ovos-reset-brain` — reset the "OVOS brain" to a blank state by uninstalling all skills.

**Inspecting plugins:**

- `ls-skills` — list the `skill_id` of every installed skill.
- `ls-stt` / `ls-tts` / `ls-ww` / `ls-tx` — list installed [STT](stt-plugins.md) / [TTS](tts-plugins.md) / wake-word / [translation](translation-plugins.md) plugins.

**Logs and status:**

- `ologs` — view all logs in real time.
- `ovos-logs [COMMAND] --help` — a small tool to help navigate the logs.
- `ovos-status` — list OVOS-related systemd services.
- `ovos-restart` — restart all OVOS-related systemd services.
- `ovos-server-status` — check the live status of the public OVOS servers.

**Misc:**

- `ovos-commands` — usage examples for the installed skills.
- `ovos-support` — compile logs into a support package to share when asking for help.
- `ovos-help` — reprint this command list.

!!! note "Audio HAT setup on RaspOVOS uses `ovos-i2csound`"
    On RaspOVOS, an i2c sound HAT (such as a Respeaker or the Mark 2's SJ201) is detected and
    configured at boot by the **`ovos-i2csound`** service shipped in the image, which writes the
    detected board to `/etc/OpenVoiceOS/i2c_platform`. This is specific to the RaspOVOS image —
    the [ovos-installer](ovos-installer.md) does **not** use it (see
    [Mark 2 Hardware](mark2.md) for the installer's kernel-driver approach).

### Check Logs in Real-Time

- Use the `ologs` command to monitor logs live on your screen.


- If you're unsure whether the system has finished booting, check logs using this command.

---

Enjoy your journey with RaspOVOS! With your Raspberry Pi set up, you can start exploring all the features of OpenVoiceOS.

---

*Source code: [OpenVoiceOS/raspOVOS](https://github.com/OpenVoiceOS/raspOVOS).*
