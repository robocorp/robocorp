from types import TracebackType
from typing import Union

ExcInfo = tuple[type[BaseException], BaseException, TracebackType]
OptExcInfo = Union[ExcInfo, tuple[None, None, None]]
