import os
import subprocess

import pygame

from src import controller
from src.controller import Action

IS_PI = os.path.exists("/dev/fb0")

FONT_PATH = "assets/fonts/PressStart2P.ttf"
BG_PATH = "assets/ps1-bios.jpg"

WIDTH, HEIGHT = 1920, 1080

FONT_SIZE = 42
ITEM_X = 80           # alinhamento esquerdo, fiel ao PS1
ITEM_START_Y = 440
ITEM_SPACING = 180

COLOR_TEXT = (255, 255, 255)

# Arco-íris do seletor (vermelho → verde → azul → roxo)
RAINBOW = [
    (220,  30,  30),
    (255, 120,   0),
    (220, 220,   0),
    (  0, 200,  50),
    (  0, 200, 220),
    ( 50,  80, 220),
    (140,   0, 220),
]

SELECTOR_H = 80   # altura da faixa do seletor
SELECTOR_W = 580  # largura da faixa do seletor


def _make_selector_surface() -> pygame.Surface:
    surf = pygame.Surface((SELECTOR_W, SELECTOR_H), pygame.SRCALPHA)
    n = len(RAINBOW)
    strip_w = SELECTOR_W // n
    for i, color in enumerate(RAINBOW):
        x = i * strip_w
        w = strip_w if i < n - 1 else SELECTOR_W - x
        s = pygame.Surface((w, SELECTOR_H), pygame.SRCALPHA)
        s.fill((*color, 190))
        surf.blit(s, (x, 0))
    return surf


def _draw_main_menu_label(screen: pygame.Surface, font: pygame.font.Font) -> None:
    label = font.render("MAIN MENU", True, (255, 255, 255))
    pad_x, pad_y = 20, 14
    box_w = label.get_width() + pad_x * 2
    box_h = label.get_height() + pad_y * 2
    box_x = WIDTH - box_w - 60
    box_y = 60

    pygame.draw.rect(screen, (30, 60, 160), (box_x, box_y, box_w, box_h))
    pygame.draw.rect(screen, (100, 140, 255), (box_x, box_y, box_w, box_h), 3)
    screen.blit(label, (box_x + pad_x, box_y + pad_y))


def run(screen: pygame.Surface, apps: list[tuple[str, str]]) -> None:
    font = pygame.font.Font(FONT_PATH, FONT_SIZE)

    bg_raw = pygame.image.load(BG_PATH).convert()
    bg = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))

    selector_surf = _make_selector_surface()

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

        _draw(screen, bg, font, selector_surf, apps, selected)
        pygame.display.flip()
        clock.tick(30)


def _launch(cmd: str) -> pygame.Surface:
    # Libera o DRM antes de lançar o app
    pygame.display.quit()

    # Remove variáveis SDL do ambiente — são específicas do pygame
    # e interferem em apps externos
    clean_env = {k: v for k, v in os.environ.items() if not k.startswith("SDL_")}
    subprocess.run(cmd, shell=True, env=clean_env)

    # Reinicializa o display depois que o app fechar
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
    selector_surf: pygame.Surface,
    apps: list[tuple[str, str]],
    selected: int,
) -> None:
    screen.blit(bg, (0, 0))
    _draw_main_menu_label(screen, font)

    for i, (name, _) in enumerate(apps):
        y = ITEM_START_Y + i * ITEM_SPACING

        if i == selected:
            sel_y = y - (SELECTOR_H - font.get_height()) // 2
            screen.blit(selector_surf, (ITEM_X - 10, sel_y))

        text_surf = font.render(name.upper(), True, COLOR_TEXT)
        screen.blit(text_surf, (ITEM_X, y))
