# PS1 OSD Launcher

A minimalist game launcher with a PlayStation 1 BIOS-style interface, designed to run on **Raspberry Pi OS Lite** — no desktop, no X11, no RetroArch as a frontend.

## Overview

PS1 OSD Launcher boots directly into a controller-navigable menu styled after the original PS1 BIOS screen. It plays a Sony-style intro video, then presents a configurable list of apps (emulators, scripts, system commands) that launch on selection and return to the menu when closed.

Built with Python and pygame, it runs over KMSDRM (direct framebuffer) on the Pi and opens as a regular window on Linux desktops or WSL for development.

## Features

- Sony PS1 intro video playback before the menu (`assets/intro.mp4`)
- OSD menu visually faithful to the original PS1 BIOS
- 100% controller-driven navigation — no keyboard or mouse required
- Universal controller support via **SDL2 GameController API** + [SDL_GameControllerDB](https://github.com/mdqinc/SDL_GameControllerDB) (2200+ mappings)
- Apps configured via `apps.ini` — add any emulator, script, or shell command
- Auto-update via `git pull` on boot
- Launched automatically via **systemd** at startup

## How It Works

```
Boot
 └── systemd: git pull (auto-update)
      └── python3 launcher.py
            ├── mpv: plays intro.mp4 (if present)
            └── pygame: OSD menu
                  ├── reads apps.ini
                  ├── controller navigation
                  └── launches selected app
                        ├── releases display (DRM)
                        ├── subprocess: runs app
                        └── returns to menu when app exits
```

## Requirements

### Hardware
- Raspberry Pi 5 (tested with 4GB RAM)
- USB or Bluetooth controller (PS, Xbox, 8BitDo, or any generic)

### OS
- Raspberry Pi OS Lite (Bookworm)
- No desktop environment, no X11

### Dependencies
```
python3-pygame
python3-pil
python3-numpy
mpv
```

## Project Structure

```
ps1-osd-launcher/
├── launcher.py               # Entry point
├── apps.ini                  # App configuration (user-editable)
├── requirements.txt          # Python dependencies
├── install.sh                # Pi installation script
├── assets/
│   ├── ps1-bios.jpg          # Menu background
│   ├── intro.mp4             # Sony intro video — add manually (see below)
│   ├── gamecontrollerdb.txt  # SDL2 controller mappings
│   └── fonts/
│       └── PressStart2P.ttf  # Menu font
├── src/
│   ├── config.py             # apps.ini reader
│   ├── intro.py              # Intro video playback
│   ├── controller.py         # Normalized controller input (SDL2)
│   └── menu.py               # OSD menu renderer
└── systemd/
    └── ps1-osd-launcher.service
```

## Configuring Apps (`apps.ini`)

```ini
[apps]
RetroArch   = retroarch
Duckstation = duckstation-qt
PPSSPP      = ppsspp
Shutdown    = !sudo shutdown -h now
Reboot      = !sudo reboot
```

- **Key** = label shown in the menu
- **Value** = shell command to execute
- Prefix `!` for system commands (shutdown, reboot)
- Order in the file determines menu order
- Edit via SSH and restart the service to apply

## Installation on Raspberry Pi

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/ps1-osd-launcher.git ~/ps1-osd-launcher
cd ~/ps1-osd-launcher
```

### 2. Edit the install script

Open `install.sh` and update `INSTALL_DIR` to match your clone path:

```bash
INSTALL_DIR="/home/<your-username>/ps1-osd-launcher"
```

Also update the sudoers line with your Pi username.

### 3. Add the intro video (optional)

```bash
# From your local machine:
scp intro.mp4 <user>@<pi-ip>:~/ps1-osd-launcher/assets/
```

If `intro.mp4` is absent, the launcher skips it silently.

### 4. Run the installer

```bash
bash install.sh
```

The installer:
- Installs `python3-pygame`, `python3-pil`, `python3-numpy`, and `mpv`
- Copies the systemd service to `/etc/systemd/system/`
- Grants passwordless `shutdown`/`reboot` permission
- Enables and starts the service

### 5. Disable any previous launcher (if applicable)

```bash
sudo systemctl disable retroarch.service
sudo systemctl stop retroarch.service
```

## Updating

Push from your machine — the Pi pulls automatically on the next boot. To apply immediately:

```bash
# On the Pi:
cd ~/ps1-osd-launcher && git pull
sudo systemctl restart ps1-osd-launcher
```

## Development (Linux / WSL)

```bash
# Install dependencies
sudo apt install python3-pygame python3-pil python3-numpy mpv

# Run
python3 launcher.py
```

On WSL with WSLg, a normal pygame window opens. On the Pi, it uses KMSDRM directly. Controller detection is automatic — keyboard works as fallback (arrow keys + Enter + Escape).

## Controller Mapping

| Action        | PS           | Xbox       | Keyboard |
|---------------|--------------|------------|----------|
| Navigate      | D-pad ↑↓     | D-pad ↑↓   | ↑↓       |
| Confirm       | X (Cross)    | A          | Enter    |
| Back / Quit   | O (Circle)   | B          | Escape   |

Works with any controller in [SDL_GameControllerDB](https://github.com/mdqinc/SDL_GameControllerDB).

## Logs and Debugging

```bash
# Live logs
sudo journalctl -u ps1-osd-launcher -f

# Last 50 lines
sudo journalctl -u ps1-osd-launcher -n 50 --no-pager

# Restart manually
sudo systemctl restart ps1-osd-launcher
```

## License

MIT License — see [LICENSE](LICENSE) for details.
