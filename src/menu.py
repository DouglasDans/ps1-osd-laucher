import glob
import os
import random
import subprocess
import sys

import pygame

from src import controller
from src.controller import Action

IS_PI = os.path.exists("/dev/fb0")

FONT_PATH = "assets/fonts/PressStart2P.ttf"
BG_PATH = "assets/ps1-bios.jpg"
MAIN_MENU_IMG_PATH = "assets/main-menu.png"
SPLASH_DIR = "assets/items-splash"

WIDTH, HEIGHT = 1920, 1080

FONT_SIZE = 42
FONT_SIZE_SELECTED = 58
ITEM_X = 200
ITEM_START_Y = 420
ITEM_SPACING = 160

COLOR_TEXT = (255, 255, 255)
COLOR_SHADOW = (0, 0, 0)
SHADOW_OFFSET = (5, 5)

SPLASH_BASE_W = 500
SPLASH_BASE_H = 120


def _load_splashes(apps: list) -> list[pygame.Surface]:
    paths = sorted(glob.glob(f"{SPLASH_DIR}/*.png"))
    random.shuffle(paths)
    result = []
    for i in range(len(apps)):
        path = paths[i % len(paths)]
        img = pygame.image.load(path).convert_alpha()
        result.append(pygame.transform.scale(img, (SPLASH_BASE_W, SPLASH_BASE_H)))
    return result


def run(screen: pygame.Surface, apps: list[tuple[str, str]]) -> None:
    font = pygame.font.Font(FONT_PATH, FONT_SIZE)
    font_selected = pygame.font.Font(FONT_PATH, FONT_SIZE_SELECTED)

    bg_raw = pygame.image.load(BG_PATH).convert()
    bg = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))

    _label = font.render("MAIN MENU", True, (255, 255, 255))
    pad_x, pad_y = 20, 14
    box_w = _label.get_width() + pad_x * 2
    box_h = _label.get_height() + pad_y * 4
    main_menu_img = pygame.transform.scale(
        pygame.image.load(MAIN_MENU_IMG_PATH).convert(),
        (box_w, box_h),
    )

    splashes = _load_splashes(apps)

    selected = 0
    clock = pygame.time.Clock()
    last_launch_time = 0
    LAUNCH_COOLDOWN = 500

    while True:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if now - last_launch_time < LAUNCH_COOLDOWN:
                continue

            action = controller.get_action(event)

            if action in (Action.QUIT, Action.BACK):
                return

            if action == Action.UP:
                selected = (selected - 1) % len(apps)

            if action == Action.DOWN:
                selected = (selected + 1) % len(apps)

            if action == Action.CONFIRM:
                screen = _launch(apps[selected][1])
                last_launch_time = pygame.time.get_ticks()
                bg_raw = pygame.image.load(BG_PATH).convert()
                bg = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))

        _draw(screen, bg, font, font_selected, main_menu_img, apps, splashes, selected)
        pygame.display.flip()
        clock.tick(30)


def _launch(cmd: str) -> pygame.Surface:
    quit_after = cmd.startswith("!")
    if quit_after:
        cmd = cmd[1:]

    pygame.display.quit()

    clean_env = {k: v for k, v in os.environ.items() if not k.startswith("SDL_")}
    subprocess.run(cmd, shell=True, env=clean_env)

    if quit_after:
        sys.exit(0)

    pygame.display.init()
    flags = pygame.FULLSCREEN if IS_PI else 0
    screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
    pygame.mouse.set_visible(False)
    pygame.event.clear()
    return screen


def _draw(
    screen: pygame.Surface,
    bg: pygame.Surface,
    font: pygame.font.Font,
    font_selected: pygame.font.Font,
    main_menu_img: pygame.Surface,
    apps: list[tuple[str, str]],
    splashes: list[pygame.Surface],
    selected: int,
) -> None:
    screen.blit(bg, (0, 0))
    screen.blit(main_menu_img, (WIDTH - main_menu_img.get_width() - 60, 60))

    for i, (name, _) in enumerate(apps):
        is_selected = (i == selected)
        splash_surf = splashes[i]
        splash_w = splash_surf.get_width()
        splash_h = splash_surf.get_height()

        y_center = ITEM_START_Y + i * ITEM_SPACING
        splash_y = y_center - splash_h // 2

        screen.blit(splash_surf, (ITEM_X, splash_y))

        f = font_selected if is_selected else font
        text = name.upper()
        text_w, text_h = f.size(text)
        splash_cx = ITEM_X + splash_w // 2
        text_x = splash_cx - text_w // 2
        text_y = splash_y + (splash_h - text_h) // 2

        screen.blit(f.render(text, True, COLOR_SHADOW), (text_x + SHADOW_OFFSET[0], text_y + SHADOW_OFFSET[1]))
        screen.blit(f.render(text, True, COLOR_TEXT), (text_x, text_y))
