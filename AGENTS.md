# AGENTS.md — AI Instructions for PS1 OSD Launcher

This file guides AI assistants (Claude Code, Copilot, etc.) working in this repository.

---

## What This Project Is

A minimalist launcher with a PlayStation 1 BIOS-style OSD, built in Python + pygame. It runs on **Raspberry Pi OS Lite** with no desktop environment, using KMSDRM for direct framebuffer rendering. On Linux desktops or WSL, it opens as a regular pygame window for development.

The launcher:
1. Plays a Sony-style intro video (`assets/intro.mp4`) via mpv
2. Shows a controller-navigable menu styled after the PS1 BIOS
3. Reads app entries from `apps.ini`
4. Launches the selected app as a subprocess, then returns to the menu
5. Starts automatically via systemd on boot

---

## Tech Stack

| Component        | Technology                              |
|------------------|-----------------------------------------|
| Language         | Python 3.11+                            |
| Rendering        | pygame 2.5+ (SDL2)                      |
| Display (Pi)     | `SDL_VIDEODRIVER=kmsdrm` (no X11)       |
| Video playback   | mpv via subprocess                      |
| Controller input | `pygame.joystick` + SDL_GameControllerDB |
| App config       | `configparser` (INI format)             |
| Boot integration | systemd service unit                    |
| Font             | Press Start 2P (`assets/fonts/`)        |

---

## Project Structure

```
ps1-osd-launcher/
├── launcher.py        # Entry point — platform detection, init, boot sequence
├── apps.ini           # User-configured app list
├── requirements.txt   # Python deps (pygame, Pillow)
├── install.sh         # Pi installation script
├── assets/
│   ├── ps1-bios.jpg          # Static menu background
│   ├── intro.mp4             # Intro video (not tracked in git)
│   ├── gamecontrollerdb.txt  # SDL2 mappings
│   └── fonts/
│       └── PressStart2P.ttf
├── src/
│   ├── config.py      # Reads apps.ini → list of (label, command)
│   ├── intro.py       # Plays intro.mp4 via mpv subprocess
│   ├── controller.py  # Normalizes joystick + keyboard events
│   └── menu.py        # OSD menu loop, rendering, app launch
└── systemd/
    └── ps1-osd-launcher.service
```

---

## Module Responsibilities

### `launcher.py`
- Detects platform via `os.path.exists("/dev/fb0")` (Pi vs dev)
- Sets SDL environment variables before `pygame.init()`
- Calls intro → menu in sequence
- Handles SIGTERM for clean shutdown

### `src/config.py`
- Reads `apps.ini` with `configparser`
- Returns a list of `(label: str, command: str)` tuples
- No external dependencies beyond stdlib

### `src/intro.py`
- Checks for `assets/intro.mp4` before attempting playback
- Pi: `mpv --vo=drm --fullscreen assets/intro.mp4`
- Dev: `mpv --fullscreen assets/intro.mp4`
- Uses `subprocess.run()` — blocks until video ends
- Silently skips if file is absent

### `src/controller.py`
- Initializes the first joystick found via `pygame.joystick`
- Maps: D-pad ↑↓ → navigate, X/A → confirm, O/B → back
- Keyboard fallback: arrows → navigate, Enter → confirm, Escape → back
- Returns normalized events — callers do not interact with pygame events directly

### `src/menu.py`
- Loads `ps1-bios.jpg` as background at 1920×1080
- Renders app labels from `config.py` with Press Start 2P font
- Draws a highlight rectangle over the active item
- On confirm: calls `subprocess.run(command, shell=True)`, waits, resumes menu
- No animations — static interface, faithful to the PS1 BIOS style

---

## Platform Detection

```python
import platform, os

IS_PI = platform.system() == "Linux" and os.path.exists("/dev/fb0")

if IS_PI:
    os.environ["SDL_VIDEODRIVER"] = "kmsdrm"
    os.environ["SDL_FBDEV"] = "/dev/fb0"
    os.environ["SDL_AUDIODRIVER"] = "alsa"
```

Do not set KMS variables in the development environment.

---

## `apps.ini` Format

```ini
[apps]
RetroArch  = retroarch
PPSSPP     = ppsspp
Shutdown   = !sudo shutdown -h now
Reboot     = !sudo reboot
```

- Section `[apps]` is required
- Key = menu label, Value = shell command
- Prefix `!` signals a system command (shutdown/reboot)
- File order = menu order

---

## Coding Conventions

- Pure Python — no frameworks beyond pygame and stdlib
- Each module in `src/` is independent and individually testable
- No verbose logging — `print()` only for critical errors
- Comments only where logic is non-obvious
- No premature abstractions — keep it simple

---

## Commit Conventions

Use conventional commits with imperative present tense:

```
feat: add splash screen before intro
fix: handle missing gamecontrollerdb.txt gracefully
refactor: extract app execution into a helper
chore: update SDL_GameControllerDB mappings
docs: update AGENTS.md with platform detection notes
```

- Keep commits focused — one logical change per commit
- Do not include `Co-Authored-By` lines

---

## Development Environment

- **Dev machine:** Linux or WSL2 with WSLg (native GUI support)
- **Target:** Raspberry Pi 5, Raspberry Pi OS Lite (Bookworm), no desktop
- **Transfer:** SSH/SCP or git push + pull on boot

On WSL, pygame opens a normal window. On the Pi, it renders via KMSDRM. Do not set Pi SDL env vars during local development.

---

## Out of Scope

- No mouse or touch support
- No ROM scraping or game metadata
- No animations in the menu
- No in-app configuration UI — edit `apps.ini` via SSH
- No multi-language support
- No multi-user or authentication
