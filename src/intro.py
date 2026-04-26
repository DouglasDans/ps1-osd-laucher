import logging
import os
import struct
import fcntl
import subprocess

log = logging.getLogger("ps1.intro")


def play_intro(video_path: str, splash_path: str | None = None) -> None:
    is_pi = os.path.exists("/dev/fb0")

    if is_pi:
        _hide_tty()

    if not os.path.exists(video_path):
        log.warning("Vídeo de intro não encontrado: %s", video_path)
        return

    cmd = ["mpv", "--fullscreen", "--no-config"]
    if is_pi:
        cmd += ["--vo=drm"]

    cmd.append(video_path)
    log.info("Reproduzindo intro: %s", video_path)
    result = subprocess.run(cmd)
    log.info("Intro encerrada: returncode=%d", result.returncode)

    if splash_path and os.path.exists(splash_path):
        _show_splash(splash_path)


def _show_splash(image_path: str) -> None:
    """Exibe imagem no framebuffer durante a transição entre intro e pygame."""
    try:
        import numpy as np
        from PIL import Image

        with open("/dev/fb0", "rb+") as fb:
            info = fcntl.ioctl(fb, 0x4600, b"\x00" * 160)
            xres = struct.unpack_from("I", info, 0)[0]
            yres = struct.unpack_from("I", info, 4)[0]
            bpp  = struct.unpack_from("I", info, 24)[0]

            img = Image.open(image_path).convert("RGB").resize((xres, yres))
            arr = np.array(img, dtype=np.uint16)

            if bpp == 16:
                pixels = ((arr[:, :, 0] & 0xF8) << 8) | \
                         ((arr[:, :, 1] & 0xFC) << 3) | \
                         (arr[:, :, 2] >> 3)
                data = pixels.astype("<u2").tobytes()
            else:
                b, g, r = arr[:, :, 2], arr[:, :, 1], arr[:, :, 0]
                data = np.stack([b, g, r, np.full_like(r, 255)], axis=-1).tobytes()

            fb.seek(0)
            fb.write(data)

    except Exception:
        log.exception("Erro ao exibir splash no framebuffer")
        try:
            with open("/dev/fb0", "wb") as fb:
                fb.write(b"\x00" * (1366 * 768 * 2))
        except OSError:
            pass


_KDSETMODE = 0x4B3A
_KD_GRAPHICS = 0x01
_KD_TEXT = 0x00


def _hide_tty() -> None:
    try:
        with open("/dev/tty1", "w") as tty:
            tty.write("\033[?25l\033[2J\033[H")
        with open("/dev/tty1", "wb") as tty:
            fcntl.ioctl(tty, _KDSETMODE, _KD_GRAPHICS)
    except OSError:
        pass


def restore_tty() -> None:
    try:
        with open("/dev/tty1", "wb") as tty:
            fcntl.ioctl(tty, _KDSETMODE, _KD_TEXT)
    except OSError:
        pass
