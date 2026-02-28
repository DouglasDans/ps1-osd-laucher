import os
import sys

import pygame

from src import controller
from src.config import load_apps
from src.intro import play_intro
from src.menu import run as run_menu

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPS_INI = os.path.join(BASE_DIR, "apps.ini")
INTRO_VIDEO = os.path.join(BASE_DIR, "assets", "intro.mp4")

WIDTH, HEIGHT = 1920, 1080

IS_PI = os.path.exists("/dev/fb0")


GAMECONTROLLERDB = os.path.join(BASE_DIR, "assets", "gamecontrollerdb.txt")


def setup_environment() -> None:
    if os.path.exists(GAMECONTROLLERDB):
        os.environ["SDL_GAMECONTROLLERCONFIG_FILE"] = GAMECONTROLLERDB

    if IS_PI:
        os.environ["SDL_VIDEODRIVER"] = "kmsdrm"
        os.environ["SDL_FBDEV"] = "/dev/fb0"
        os.environ["SDL_AUDIODRIVER"] = "alsa"


def main() -> None:
    setup_environment()

    try:
        apps = load_apps(APPS_INI)
    except (FileNotFoundError, KeyError) as e:
        print(f"Erro ao carregar apps.ini: {e}", file=sys.stderr)
        sys.exit(1)

    play_intro(INTRO_VIDEO)

    pygame.init()
    flags = pygame.FULLSCREEN if IS_PI else 0
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.display.set_caption("PS1 Launcher")
    pygame.mouse.set_visible(False)

    controller.init()
    run_menu(screen, apps)

    pygame.quit()


if __name__ == "__main__":
    main()
