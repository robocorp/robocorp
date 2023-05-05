import sys
from typing import Protocol


class _OnExitContextManager:
    def __init__(self, on_exit) -> None:
        self.on_exit = on_exit

    def __enter__(self) -> None:
        pass

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.on_exit()


class _IConsole(Protocol):
    def set_color(self, foreground_color: str) -> _OnExitContextManager:
        pass


# https://stackoverflow.com/questions/4842424/list-of-ansi-color-escape-sequences
class _AnsiConsole(object):
    color_map = {
        "BLACK": 30,
        "BLUE": 94,  # This is actually "bright blue"
        "CYAN": 96,  # This is actually "bright cyan"
        "GREEN": 32,
        "MAGENTA": 95,  # This is actually "bright magenta"
        "RED": 91,  # This is actually "bright red"
        "WHITE": 37,
        "YELLOW": 33,
    }

    def _escape(self, code):
        sys.stdout.flush()
        sys.stdout.buffer.write(b"\033[" + code)

    def set_color(self, foreground_color: str) -> _OnExitContextManager:
        self._escape(b"%dm" % self.color_map[foreground_color])
        return _OnExitContextManager(self.reset)

    def reset(self):
        self._escape(b"0m")


_console: _IConsole
_ansi_console: _IConsole
_default_console: _IConsole
_no_color_console: _IConsole

_ansi_console = _default_console = _AnsiConsole()


try:

    def _init_win32():
        """
        Based on https://www.burgaud.com/bring-colors-to-the-windows-console-with-python/
        (License: MIT)

        Colors text in console mode application (win32).
        Uses ctypes and Win32 methods SetConsoleTextAttribute and
        GetConsoleScreenBufferInfo.
        """
        from ctypes import Structure, byref, c_short, c_ushort, windll

        SHORT = c_short
        WORD = c_ushort

        class COORD(Structure):
            """struct in wincon.h."""

            _fields_ = [("X", SHORT), ("Y", SHORT)]

        class SMALL_RECT(Structure):
            """struct in wincon.h."""

            _fields_ = [
                ("Left", SHORT),
                ("Top", SHORT),
                ("Right", SHORT),
                ("Bottom", SHORT),
            ]

        class CONSOLE_SCREEN_BUFFER_INFO(Structure):
            """struct in wincon.h."""

            _fields_ = [
                ("dwSize", COORD),
                ("dwCursorPosition", COORD),
                ("wAttributes", WORD),
                ("srWindow", SMALL_RECT),
                ("dwMaximumWindowSize", COORD),
            ]

        class _Constants:
            # winbase.h
            STD_INPUT_HANDLE = -10
            STD_OUTPUT_HANDLE = -11
            STD_ERROR_HANDLE = -12

            # wincon.h
            FOREGROUND_BLACK = 0x0000
            FOREGROUND_BLUE = 0x0001
            FOREGROUND_GREEN = 0x0002
            FOREGROUND_CYAN = 0x0003
            FOREGROUND_RED = 0x0004
            FOREGROUND_MAGENTA = 0x0005
            FOREGROUND_YELLOW = 0x0006
            FOREGROUND_GREY = 0x0007
            FOREGROUND_INTENSITY = 0x0008  # foreground color is intensified.

            BACKGROUND_BLACK = 0x0000
            BACKGROUND_BLUE = 0x0010
            BACKGROUND_GREEN = 0x0020
            BACKGROUND_CYAN = 0x0030
            BACKGROUND_RED = 0x0040
            BACKGROUND_MAGENTA = 0x0050
            BACKGROUND_YELLOW = 0x0060
            BACKGROUND_GREY = 0x0070
            BACKGROUND_INTENSITY = 0x0080  # background color is intensified.

        stdout_handle = windll.kernel32.GetStdHandle(_Constants.STD_OUTPUT_HANDLE)
        SetConsoleTextAttribute = windll.kernel32.SetConsoleTextAttribute
        GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo

        def get_text_attr():
            """Returns the character attributes (colors) of the console screen
            buffer."""
            csbi = CONSOLE_SCREEN_BUFFER_INFO()
            GetConsoleScreenBufferInfo(stdout_handle, byref(csbi))
            return csbi.wAttributes

        def set_text_attr(color):
            """Sets the character attributes (colors) of the console screen
            buffer. Color is a combination of foreground and background color,
            foreground and background intensity."""

            sys.stdout.flush()  # Flush is needed on Python 3
            SetConsoleTextAttribute(stdout_handle, color)
            sys.stdout.flush()  # Flush is needed on Python 3

        class _Console(object):
            def __init__(self):
                colors = dict(
                    BLACK=[],
                    BLUE=["BLUE"],
                    CYAN=["GREEN", "BLUE"],
                    GREEN=["GREEN"],
                    MAGENTA=["RED", "BLUE"],
                    RED=["RED"],
                    WHITE=["RED", "GREEN", "BLUE"],
                    YELLOW=["RED", "GREEN"],
                )

                self._foreground_map = color_map = {"": 0}
                for color_name, color_components in colors.items():
                    if color_components:
                        value = _Constants.FOREGROUND_INTENSITY
                    else:
                        value = 0
                    for component in color_components:
                        value |= getattr(_Constants, "FOREGROUND_" + component)
                    color_map[color_name] = value

                # Some of the calls below could raise exceptions, in which case we should
                # fallback to another approach!
                self._reset = get_text_attr()

            def set_color(self, foreground_color: str) -> _OnExitContextManager:
                set_text_attr(self._foreground_map[foreground_color])
                return _OnExitContextManager(self.reset)

            def reset(self):
                set_text_attr(self._reset)

        return _Console()

    if sys.platform == "win32" and sys.stdout.isatty():
        _default_console = _init_win32()
    else:
        raise RuntimeError("Force ansi usage.")


except:
    # If anything fails there, use the version that prints ansi chars.
    pass


class _NoColorConsole:
    def set_color(self, foreground_color: str) -> _OnExitContextManager:
        return _OnExitContextManager(lambda: None)


_no_color_console = _NoColorConsole()

# This is the one we're actually using.
_console = _default_console


# Public API -----------

COLOR_BLACK = "BLACK"
COLOR_BLUE = "BLUE"
COLOR_CYAN = "CYAN"
COLOR_GREEN = "GREEN"
COLOR_MAGENTA = "MAGENTA"
COLOR_RED = "RED"
COLOR_WHITE = "WHITE"
COLOR_YELLOW = "YELLOW"


def set_color(foreground_color: str) -> _OnExitContextManager:
    """
    To be used as:

    with set_color(COLOR_BLACK):
        ...

    Args:
        foreground_color:
            The foreground color to be set (see COLOR_XXX constants).
    """
    return _console.set_color(foreground_color)


def set_mode(mode: str) -> None:
    """
    Can be used to set the mode of the console.
    Options:
        "auto": uses the default console
        "plain": disables colors
        "ansi": forces ansi color mode
    """
    global _console
    if mode == "plain":
        _console = _no_color_console
    elif mode == "auto":
        _console = _default_console
    elif mode == "ansi":
        _console = _ansi_console
    else:
        raise ValueError(f"Unexpected: {mode}.")


if __name__ == "__main__":
    for name in list(globals()):
        if name.startswith("COLOR"):
            with set_color(globals()[name]):
                print(f"In {name}")

    set_mode("plain")
    for name in list(globals()):
        if name.startswith("COLOR"):
            with set_color(globals()[name]):
                print(f"In {name}")

    set_mode("ansi")
    for name in list(globals()):
        if name.startswith("COLOR"):
            with set_color(globals()[name]):
                print(f"In {name}")
