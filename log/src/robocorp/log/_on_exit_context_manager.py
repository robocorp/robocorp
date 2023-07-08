from types import TracebackType
from typing import Optional


class OnExitContextManager:
    def __init__(self, on_exit):
        self.on_exit = on_exit

    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        self.on_exit()
