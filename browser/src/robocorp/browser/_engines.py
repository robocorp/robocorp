import os
import platform
import subprocess
import sys
import threading
from pathlib import Path
from typing import BinaryIO, List, Optional

from robocorp import log

from ._types import BrowserEngine, InstallError

# Map of BrowserEngine to Playwright driver & channel
ENGINE_TO_ARGS = {
    BrowserEngine.CHROMIUM: ("chromium", None),
    BrowserEngine.CHROME: ("chromium", "chrome"),
    BrowserEngine.CHROME_BETA: ("chromium", "chrome-beta"),
    BrowserEngine.MSEDGE: ("chromium", "msedge"),
    BrowserEngine.MSEDGE_BETA: ("chromium", "msedge-beta"),
    BrowserEngine.MSEDGE_DEV: ("chromium", "msedge-dev"),
    BrowserEngine.FIREFOX: ("firefox", None),
    BrowserEngine.WEBKIT: ("webkit", None),
}


def _holotree_path() -> Optional[Path]:
    if holotree := os.getenv("RCC_HOLOTREE_SPACE_ROOT"):
        return Path(holotree) / "robocorp" / "playwright"
    return None


def _robocorp_home_path() -> Path:
    if platform.system() == "Windows":
        return Path.home() / "AppData" / "Local" / "robocorp" / "playwright"
    else:
        return Path.home() / ".robocorp" / "playwright"


def browsers_path(isolated: bool = False) -> Path:
    if isolated:
        path = _holotree_path()
        if path is None:
            raise InstallError("Not inside isolated environment")
    else:
        path = _robocorp_home_path()

    return path


def _build_install_command_line(engine, force):
    """
    Note: this function is mocked in tests.
    """
    cmd = [sys.executable, "-m", "playwright", "install"]
    if force:
        cmd.append("--force")
    name = BrowserEngine(engine).value
    cmd.append(name)
    return cmd


def install_browser(
    engine: BrowserEngine,
    force: bool = False,
    interactive: bool = False,
    isolated: bool = False,
) -> Path:
    from concurrent import futures

    cmd = _build_install_command_line(engine, force)
    name = BrowserEngine(engine).value

    path = browsers_path(isolated=isolated)
    env = dict(os.environ)
    env["PLAYWRIGHT_BROWSERS_PATH"] = str(path)
    log.info(f"Installing browsers at: {path} (interactive: {interactive})")

    if interactive:
        # This can take a while, but the output should be seen in 'sys.stderr',
        # so, no additional handling done.
        result = subprocess.run(cmd, env=env)

        if result.returncode != 0:
            raise InstallError(f"Failed to install {name}")
    else:
        # Note: this can take a while (especially with a slow network connection
        # so, display some information if it's not interactive the user is not
        # supposed to see the output in sys.stderr, but we can still log
        # something).

        stdout_lines_lock = threading.Lock()
        stdout_lines: List[bytes] = []

        def _stream_reader(stream: BinaryIO, lst: List[bytes]) -> None:
            try:
                while True:
                    line: bytes = stream.readline()
                    if line.endswith(b"\r\n"):
                        line = line[:-2]
                    elif line.endswith((b"\r", b"\n")):
                        line = line[:-1]
                    if not line:
                        break
                    with stdout_lines_lock:
                        lst.append(line)
            except Exception:
                pass

        future: "futures.Future[int]" = futures.Future()

        def install_in_thread():
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    env=env,
                    bufsize=0,
                )

                threading.Thread(
                    target=_stream_reader,
                    args=(process.stdout, stdout_lines),
                    name="Playwright browser install stdout reader",
                    daemon=True,
                ).start()

                returncode = process.wait()
                future.set_result(returncode)
            except BaseException as e:
                future.set_exception(e)
                raise

        t = threading.Thread(
            target=install_in_thread,
            name="Playwright browser install thread",
            daemon=True,
        )
        t.start()

        import locale

        encoding = locale.getpreferredencoding()

        reported_from = 0
        returncode = None
        log.info(
            "Browser install (with playwright) in process "
            "(see debug messages for more information)."
        )
        while returncode is None:
            try:
                returncode = future.result(10)
            except futures.TimeoutError:
                pass

            if stdout_lines:
                with stdout_lines_lock:
                    add_to_debug = stdout_lines[reported_from:]
                    reported_from = len(stdout_lines)

                for line in add_to_debug:
                    log.debug(line.decode(encoding, "replace"))

        if returncode != 0:
            stdout = b"\n".join(stdout_lines).decode(encoding, "replace")
            raise InstallError(
                f"Failed to install {name}\n"
                + f"Return code: {returncode}\n"
                + f"Output: {stdout}\n"
            )

    return path
