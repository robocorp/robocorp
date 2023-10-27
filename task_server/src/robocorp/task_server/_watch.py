import logging
from pathlib import Path
from threading import Event, Thread
from typing import Callable, Optional

import watchfiles

LOGGER = logging.getLogger(__name__)


class FileWatcher:
    DEFAULT_INCLUDES = ["*.py"]
    DEFAULT_EXCLUDES = [".*", ".py[cod]", "~*"]

    def __init__(self, path: Path, callback: Callable[[list[Path]], None]):
        self._path = path
        self._callback = callback
        self._stop = Event()
        self._thread: Optional[Thread] = None

    def start(self):
        assert self._thread is None
        assert not self._stop.is_set()
        self._thread = Thread(target=self._poll_watch)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        self._stop.set()

    def _poll_watch(self):
        watch = watchfiles.watch(
            self._path,
            stop_event=self._stop,
            recursive=True,
        )

        LOGGER.info("Starting file watch [path=%s]", self._path)
        for changes in watch:
            paths = {Path(change[1]) for change in changes}
            paths = [path for path in paths if self._is_valid(path)]
            if not paths:
                continue

            try:
                self._callback(paths)
            except Exception as exc:
                LOGGER.debug("Error in file watcher: %s", exc)

    @classmethod
    def _is_valid(cls, path: Path) -> bool:
        for include in cls.DEFAULT_INCLUDES:
            if path.match(include):
                break
        else:
            return False

        for exclude in cls.DEFAULT_EXCLUDES:
            if path.match(exclude):
                return False

        return True
