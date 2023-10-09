import subprocess
import sys
import threading
import time

from robocorp_windows_tests.fixtures import wait_for_condition


def test_resize_and_close_window(tk_process):
    from robocorp_windows_tests.fixtures import wait_for_process_exit

    from robocorp import windows

    w = windows.find_window('name:"Tkinter Elements Showcase"')

    curr = w.rectangle

    def changed_rect():
        nonlocal curr
        w.update_geometry()
        new_rect = w.rectangle
        if new_rect != curr:
            curr = new_rect
            return True
        return False

    w.minimize_window()
    wait_for_condition(changed_rect)
    w.restore_window()
    wait_for_condition(changed_rect)

    w.maximize_window()
    wait_for_condition(changed_rect)
    w.restore_window()
    wait_for_condition(changed_rect)

    w.close_window()
    wait_for_process_exit(tk_process)


def test_close_windows():
    from robocorp_windows_tests import snippet_tk
    from robocorp_windows_tests.fixtures import wait_for_process_exit

    from robocorp import windows

    desktop = windows.desktop()

    popens = []
    for _i in range(2):
        f = snippet_tk.__file__
        popen = subprocess.Popen([sys.executable, f])
        popens.append(popen)

    def check_windows_created():
        from robocorp.windows import find_windows

        found = [w for w in find_windows() if w.name == "Tkinter Elements Showcase"]
        return len(found) == 2

    wait_for_condition(check_windows_created)
    desktop.close_windows('name:"Tkinter Elements Showcase"')
    for popen in popens:
        wait_for_process_exit(popen)


def test_find_window_started_afterwards():
    from robocorp_windows_tests import snippet_tk
    from robocorp_windows_tests.fixtures import wait_for_process_exit

    from robocorp import windows
    from robocorp.windows._processes import kill_process_and_subprocesses

    try:
        popen = None
        event = threading.Event()

        def launch():
            nonlocal popen

            time.sleep(1)
            f = snippet_tk.__file__
            popen = subprocess.Popen([sys.executable, f])
            event.set()

        t = threading.Thread(target=launch)
        t.start()
        # We want to start the find_window and only create the window
        # afterwards to check that the timeout works.
        w = windows.find_window('name:"Tkinter Elements Showcase"')

        # Make sure that the pid is set.
        event.wait()

        # w.print_tree(show_properties=True)

        w.click("name:Close")
        wait_for_process_exit(popen)

    finally:
        if popen.poll() is None:  # Still alive: kill it.
            kill_process_and_subprocesses(popen.pid)
