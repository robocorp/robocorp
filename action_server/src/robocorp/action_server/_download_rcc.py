import logging
import os
import platform
import sys
from pathlib import Path
from typing import Optional

log = logging.getLogger(__name__)

# Note: also referenced in action_server/build.py
RCC_VERSION = "17.12.1"
RCC_URLS = {
    "Windows": f"https://downloads.robocorp.com/rcc/releases/v{RCC_VERSION}/windows64/rcc.exe",
    "Darwin": f"https://downloads.robocorp.com/rcc/releases/v{RCC_VERSION}/macos64/rcc",
    "Linux": f"https://downloads.robocorp.com/rcc/releases/v{RCC_VERSION}/linux64/rcc",
}


def get_default_rcc_location() -> Path:
    CURDIR = Path(__file__).parent.absolute()
    if sys.platform == "win32":
        rcc_path = CURDIR / "bin" / "rcc.exe"
    else:
        rcc_path = CURDIR / "bin" / "rcc"
    return rcc_path


def download_rcc(
    system: Optional[str] = None, target: Optional[str] = None, force=False
) -> Path:
    """
    Downloads RCC in the place where the action server expects it.
    """
    import stat
    import urllib.request

    if target:
        rcc_path = Path(target)
    else:
        rcc_path = get_default_rcc_location()

    if not force:
        if rcc_path.exists():
            return rcc_path

        log.info(f"RCC not available at: {rcc_path}. Downloading.")

    rcc_path.parent.mkdir(parents=True, exist_ok=True)

    rcc_url = RCC_URLS[system or platform.system()]

    print(f"Downloading '{rcc_url}' to '{rcc_path}'")

    # Cloudflare seems to be blocking "User-Agent: Python-urllib/3.9".
    # Use a different one as that must be sorted out.
    response = urllib.request.urlopen(
        urllib.request.Request(rcc_url, headers={"User-Agent": "Mozilla"})
    )

    with open(rcc_path, "wb") as stream:
        stream.write(response.read())

    st = os.stat(rcc_path)
    os.chmod(rcc_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return rcc_path
