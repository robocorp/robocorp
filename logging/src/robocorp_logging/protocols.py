from types import TracebackType
from typing import Union, Literal

ExcInfo = tuple[type[BaseException], BaseException, TracebackType]
OptExcInfo = Union[ExcInfo, tuple[None, None, None]]

LogHTMLStyle = Literal["standalone", "vscode"]
