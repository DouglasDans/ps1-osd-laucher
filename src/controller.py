import os

import pygame
from pygame._sdl2 import controller as sdl2_ctrl
from enum import Enum, auto

GAMECONTROLLERDB = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "gamecontrollerdb.txt"
)


class Action(Enum):
    UP = auto()
    DOWN = auto()
    CONFIRM = auto()
    BACK = auto()
    QUIT = auto()


def init() -> None:
    # Carrega banco de mapeamentos comunitário (mesmo usado pelo RetroArch)
    if os.path.exists(GAMECONTROLLERDB):
        os.environ["SDL_GAMECONTROLLERCONFIG_FILE"] = GAMECONTROLLERDB

    sdl2_ctrl.init()

    for i in range(sdl2_ctrl.get_count()):
        if sdl2_ctrl.is_controller(i):
            sdl2_ctrl.Controller(i)


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

    # GameController API — PS, Xbox, 8BitDo e qualquer controle no SDL_GameControllerDB
    # Valores inteiros SDL2 estáveis (constantes nomeadas indisponíveis em algumas versões)
    # Ref: https://wiki.libsdl.org/SDL2/SDL_GameControllerButton
    if event.type == pygame.CONTROLLERBUTTONDOWN:
        if event.button == 11:   # SDL_CONTROLLER_BUTTON_DPAD_UP
            return Action.UP
        if event.button == 12:   # SDL_CONTROLLER_BUTTON_DPAD_DOWN
            return Action.DOWN
        if event.button == 0:    # SDL_CONTROLLER_BUTTON_A
            return Action.CONFIRM
        if event.button == 1:    # SDL_CONTROLLER_BUTTON_B
            return Action.BACK

    # Novo controle conectado em runtime
    if event.type == pygame.CONTROLLERDEVICEADDED:
        if sdl2_ctrl.is_controller(event.device_index):
            sdl2_ctrl.Controller(event.device_index)

    return None
