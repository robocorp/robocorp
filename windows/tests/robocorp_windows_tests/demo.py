import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def demo():
    import subprocess
    import sys

    from robocorp_windows_tests import snippet_tk

    from robocorp import windows

    windows_locator = "name:Calculator"
    cmd = ["C:\\Windows\\System32\\calc.exe"]

    # Could be used to
    windows_locator = 'name:"Tkinter Elements Showcase"'
    cmd = [sys.executable, snippet_tk.__file__]

    windows.desktop().close_windows(windows_locator)

    subprocess.Popen(cmd)
    window = windows.find_window(windows_locator, timeout=10, wait_time=0)

    # Some sample commands
    # a
    # p
    # f:Button
    # h:control:ButtonControl
    # m
    window.inspect()


if __name__ == "__main__":
    demo()
