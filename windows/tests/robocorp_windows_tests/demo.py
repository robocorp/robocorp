import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def demo():
    import subprocess

    from robocorp import windows
    from robocorp.windows._processes import kill_process_and_subprocesses

    windows_locator = "name:Calculator"
    cmd = ["C:\\Windows\\System32\\calc.exe"]

    # Could be used to check snippet_tk sample
    # from robocorp_windows_tests import snippet_tk
    # windows_locator = 'name:"Tkinter Elements Showcase"'
    # cmd = [sys.executable, snippet_tk.__file__]

    windows.desktop().close_windows(windows_locator)

    popen = subprocess.Popen(cmd)
    window = windows.find_window(windows_locator, timeout=10, wait_time=0)

    # Some sample commands
    # a
    # p
    # f:Button
    # h:control:ButtonControl
    # m
    try:
        window.inspect()
    finally:
        kill_process_and_subprocesses(popen.pid)


if __name__ == "__main__":
    demo()
