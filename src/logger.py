import logging
import logging.handlers
from pathlib import Path

LOG_DIR = Path.home() / ".local" / "share" / "ps1-osd-launcher"
LOG_FILE = LOG_DIR / "launcher.log"

_FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"


def setup() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    root = logging.getLogger("ps1")
    root.setLevel(logging.DEBUG)

    if root.handlers:
        return

    fmt = logging.Formatter(_FMT, datefmt=_DATE_FMT)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)

    root.addHandler(file_handler)
    root.addHandler(stream_handler)
