import os
import subprocess


def play_intro(video_path: str) -> None:
    is_pi = os.path.exists("/dev/fb0")

    if is_pi:
        _hide_tty()

    if not os.path.exists(video_path):
        return

    cmd = ["mpv", "--fullscreen", "--no-config"]
    if is_pi:
        cmd += ["--vo=drm"]

    cmd.append(video_path)
    subprocess.run(cmd)


def _hide_tty() -> None:
    """Esconde cursor e limpa o TTY1 para não aparecer entre intro e menu."""
    try:
        with open("/dev/tty1", "w") as tty:
            tty.write("\033[?25l\033[2J\033[H")  # oculta cursor, limpa tela
    except OSError:
        pass
