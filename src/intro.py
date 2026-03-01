import os
import struct
import fcntl
import subprocess


def play_intro(video_path: str, splash_path: str | None = None) -> None:
    is_pi = os.path.exists("/dev/fb0")

    if is_pi:
        _hide_tty()

    if not is_pi:
        return

    if not os.path.exists(video_path):
        return

    cmd = ["mpv", "--fullscreen", "--no-config"]
    if is_pi:
        cmd += ["--vo=drm"]

    cmd.append(video_path)
    subprocess.run(cmd)

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
        try:
            with open("/dev/fb0", "wb") as fb:
                fb.write(b"\x00" * (1366 * 768 * 2))
        except OSError:
            pass


def _hide_tty() -> None:
    """Esconde cursor e limpa o TTY1 para não aparecer entre intro e menu."""
    try:
        with open("/dev/tty1", "w") as tty:
            tty.write("\033[?25l\033[2J\033[H")  # oculta cursor, limpa tela
    except OSError:
        pass
