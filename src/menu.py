import subprocess

import pygame

from src import controller
from src.controller import Action

FONT_PATH = "assets/fonts/PressStart2P.ttf"
BG_PATH = "assets/ps1-bios.jpg"

WIDTH, HEIGHT = 1920, 1080
FONT_SIZE = 30
ITEM_SPACING = 70

COLOR_TEXT = (255, 255, 255)
COLOR_TEXT_SELECTED = (255, 220, 100)
COLOR_HIGHLIGHT = (80, 0, 140, 160)  # roxo semi-transparente


def run(screen: pygame.Surface, apps: list[tuple[str, str]]) -> None:
    font = pygame.font.Font(FONT_PATH, FONT_SIZE)

    bg_raw = pygame.image.load(BG_PATH).convert()
    bg = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))

    selected = 0
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            action = controller.get_action(event)

            if action in (Action.QUIT, Action.BACK):
                return

            if action == Action.UP:
                selected = (selected - 1) % len(apps)

            if action == Action.DOWN:
                selected = (selected + 1) % len(apps)

            if action == Action.CONFIRM:
                _launch(screen, apps[selected][1])

        _draw(screen, bg, font, apps, selected)
        pygame.display.flip()
        clock.tick(30)


def _launch(screen: pygame.Surface, cmd: str) -> None:
    screen.fill((0, 0, 0))
    pygame.display.flip()
    subprocess.run(cmd, shell=True)


def _draw(
    screen: pygame.Surface,
    bg: pygame.Surface,
    font: pygame.font.Font,
    apps: list[tuple[str, str]],
    selected: int,
) -> None:
    screen.blit(bg, (0, 0))

    total_height = len(apps) * ITEM_SPACING
    start_y = (HEIGHT - total_height) // 2 + 80

    for i, (name, _) in enumerate(apps):
        y = start_y + i * ITEM_SPACING
        color = COLOR_TEXT_SELECTED if i == selected else COLOR_TEXT
        text_surf = font.render(name, True, color)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, y))

        if i == selected:
            pad_x, pad_y = 24, 12
            hl_rect = pygame.Rect(
                text_rect.left - pad_x,
                text_rect.top - pad_y,
                text_rect.width + pad_x * 2,
                text_rect.height + pad_y * 2,
            )
            hl_surf = pygame.Surface((hl_rect.width, hl_rect.height), pygame.SRCALPHA)
            hl_surf.fill(COLOR_HIGHLIGHT)
            screen.blit(hl_surf, hl_rect.topleft)

        screen.blit(text_surf, text_rect)
