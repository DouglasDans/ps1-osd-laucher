import glob
import os
import random
import subprocess
import sys

import pygame

from src import controller
from src.controller import Action
from src.ps1_font import PS1Font

IS_PI = os.path.exists("/dev/fb0")

PS1_FONT_SHEET = "assets/ps1_font_sheet.png"
PS1_FONT_JSON = "assets/ps1_font.json"
BG_PATH = "assets/ps1-bios.jpg"
MAIN_MENU_IMG_PATH = "assets/main-menu.png"
SPLASH_DIR = "assets/items-splash"

WIDTH, HEIGHT = 1920, 1080

# Uppercase glyphs are ~70px tall in the sprite sheet.
# Scale to match the original font sizes (42px / 58px).
FONT_SCALE = 0.70
FONT_SCALE_SELECTED = 0.87
ITEM_X = 210
ITEM_START_Y = 340
ITEM_SPACING = 160

COLOR_TEXT = (255, 255, 255)
COLOR_SHADOW = (0, 0, 0)
SHADOW_OFFSET = (5, 5)

SPLASH_BASE_W = 500
SPLASH_BASE_H = 140


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
    font = PS1Font(PS1_FONT_SHEET, PS1_FONT_JSON)

    bg_raw = pygame.image.load(BG_PATH).convert()
    bg = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))

    _raw_menu_img = pygame.image.load(MAIN_MENU_IMG_PATH).convert()
    orig_w, orig_h = _raw_menu_img.get_size()
    box_h = 120
    box_w = int(orig_w * box_h / orig_h * 3 / 4)  # corrige stretch 16:9 → 4:3
    main_menu_img = pygame.transform.scale(_raw_menu_img, (box_w, box_h))

    splashes = _load_splashes(apps)

    selected = 0
    clock = pygame.time.Clock()
    transitioning = False
    transition_start = 0
    TRANSITION_DURATION = 1000

    while True:
        now = pygame.time.get_ticks()

        if transitioning:
            t = min((now - transition_start) / TRANSITION_DURATION, 1.0)
            if t >= 1.0:
                screen = _launch(apps[selected][1])
                transitioning = False
                bg_raw = pygame.image.load(BG_PATH).convert()
                bg = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))
                t = 0.0
            selected_color = (int(255 * (1 - t)), int(255 * (1 - t)), int(255 * (1 - t)))
        else:
            selected_color = COLOR_TEXT
            for event in pygame.event.get():
                action = controller.get_action(event)

                if action in (Action.QUIT, Action.BACK):
                    return

                if action == Action.UP:
                    selected = (selected - 1) % len(apps)

                if action == Action.DOWN:
                    selected = (selected + 1) % len(apps)

                if action == Action.CONFIRM:
                    transitioning = True
                    transition_start = now

        _draw(screen, bg, font, main_menu_img, apps, splashes, selected, selected_color)
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
    font: PS1Font,
    main_menu_img: pygame.Surface,
    apps: list[tuple[str, str]],
    splashes: list[pygame.Surface],
    selected: int,
    selected_color: tuple[int, int, int] = COLOR_TEXT,
) -> None:
    screen.blit(bg, (0, 0))
    screen.blit(main_menu_img, (WIDTH - main_menu_img.get_width() - 100, 60))

    for i, (name, _) in enumerate(apps):
        is_selected = (i == selected)
        splash_surf = splashes[i]
        splash_w = splash_surf.get_width()
        splash_h = splash_surf.get_height()

        y_center = ITEM_START_Y + i * ITEM_SPACING
        splash_y = y_center - splash_h // 2

        screen.blit(splash_surf, (ITEM_X, splash_y))

        scale = FONT_SCALE_SELECTED if is_selected else FONT_SCALE
        text = name.upper()
        text_w = font.text_width(text, scale=scale)
        text_h = max((int(font.glyphs[c].get_size()[1] * scale) for c in text if c in font.glyphs), default=int(font.line_height * scale))
        splash_cx = ITEM_X + splash_w // 2
        text_x = splash_cx - text_w // 2
        text_y = splash_y + (splash_h - text_h) // 2

        color = selected_color if is_selected else COLOR_TEXT
        font.render(screen, text, text_x + SHADOW_OFFSET[0], text_y + SHADOW_OFFSET[1], color=COLOR_SHADOW, scale=scale)
        font.render(screen, text, text_x, text_y, color=color, scale=scale)
