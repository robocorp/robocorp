# Quickstart

Getting started with `robocorp.windows` is as simple as:

```python
windows.desktop().windows_run("notepad.exe")  # starts Notepad with Windows Run
notepad = windows.find_window('subname:"Notepad"')  # controls & gets the window into focus
notepad.find('control:"MenuItemControl" and name:"File"').click()  # clicks the found "File" menu item
notepad.close_window()  # closes the current window
```

Now, if we put this in a Task/Action Package, we could save a _tasks.py_ file with the
following content:

```python
from robocorp import windows
from robocorp.tasks import task

desktop = windows.desktop()

@task
def automate_notepad():
    """Automates the Notepad app by clicking the 'File' menu item, then exits."""
    desktop.windows_run("notepad.exe")
    notepad = windows.find_window('subname:"Notepad"')
    try:
        notepad.find('control:"MenuItemControl" and name:"File"').click()
    finally:
        notepad.close_window()
```
