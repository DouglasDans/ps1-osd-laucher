import pygame
from enum import Enum, auto


class Action(Enum):
    UP = auto()
    DOWN = auto()
    CONFIRM = auto()
    BACK = auto()
    QUIT = auto()


def init() -> None:
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        joy = pygame.joystick.Joystick(0)
        joy.init()


def get_action(event: pygame.event.Event) -> Action | None:
    # Teclado (fallback dev)
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            return Action.UP
        if event.key == pygame.K_DOWN:
            return Action.DOWN
        if event.key == pygame.K_RETURN:
            return Action.CONFIRM
        if event.key == pygame.K_ESCAPE:
            return Action.BACK

    if event.type == pygame.QUIT:
        return Action.QUIT

    # D-pad (PS e Xbox expõem como hat)
    if event.type == pygame.JOYHATMOTION:
        _, y = event.value
        if y == 1:
            return Action.UP
        if y == -1:
            return Action.DOWN

    # Botões: 0 = X/A (confirmar), 1 = O/B (voltar)
    if event.type == pygame.JOYBUTTONDOWN:
        if event.button == 0:
            return Action.CONFIRM
        if event.button == 1:
            return Action.BACK

    return None
