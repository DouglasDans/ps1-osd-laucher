import os
import subprocess


def play_intro(video_path: str) -> None:
    if not os.path.exists(video_path):
        return

    is_pi = os.path.exists("/dev/fb0")

    cmd = ["mpv", "--fullscreen", "--no-config"]
    if is_pi:
        cmd += ["--vo=drm"]

    cmd.append(video_path)
    subprocess.run(cmd)
