# Working with locators in robocorp-windows

The term `locator` means a string which identifies how to reach an
element in the application UI structure.

In the context of `robocorp-windows` it'll identify how to reach a window
or some element inside the window (such as a combo box, text edit, etc).

With `robocorp-windows`, a basic inspector which can be used to identify
the values which can be used in locators as well as testing locators can
be used with the `inspect()` method for some element.

To start from the desktop, the API used would be:

```python
from robocorp import windows
windows.desktop().inspect()
```

Then, using the `select window` (activated with `s:<optional window-related name>` -- 
i.e.: `s:note` to filter for windows with `note` in the name) 
can be used to inspect elements inside a given window 
(follow the text prompts to know what's available).

After you have the locator for the window, it's recommended to start from the
window directly:

Example with `Notepad++`:

```python
from robocorp import windows
windows.find_window('control:WindowControl class:Notepad++').inspect()
```

Usually the most useful approach is then asking for the `highlight mouse` 
(activated with `m`) and then hovering over the element of interest -- after
a timeout with the mouse in the same position the related element should be
highlighted and the information available to be used to reach it will be
printed to the output.

Example:

Hovering over the record button of Notepad++ will print something as:

```
1-5. control:PaneControl class:ReBarWindow32 name:"" id:"" handle:0xB60560(11928928) Search info(depth:1 index:5 path:5)
    2-1. control:ToolBarControl class:ToolbarWindow32 name:"" id:"" handle:0xA7110C(10948876) Search info(depth:2 index:1 path:5|1)
        3-35. control:ButtonControl class:"" name:"Start Recording" id:"" handle:0x0(0) Search info(depth:3 index:35 path:5|1|35)
```

In this case some valid locators to reach it could be:

- `name:"Start Recording"`
- `control:ButtonControl`
- `class:ToolbarWindow32 > control:ButtonControl and name:"Start Recording"`
- `path:5|1|35`

Note that it's important to select a locator that will uniquely identify the
element (so, for instance the `control:ButtonControl` may not be ideal because
it may match other buttons in the UI).

Also, it's important to note that when a given element is printed, in the
inspector you can interact with it to know whether it's actually valid,
so, for instance, it's possible to test a locator with:

    `h:control:ButtonControl`

to see which elements would be selected by it.

For the particular case of Notepad++, you may notice that doing something
as `h:name:"Start Recording"` may fail to actually highlight any element.

In the Notepad++ case this happens because the buttons in the toolbar will
only be accessible when the mouse is hovering over the toolbar.

In this case, the code to successfully access it would need to first hover
over the toolbar:

```python
window = windows.find_window("control:WindowControl class:Notepad++")
toolbar = window.find("class:ToolbarWindow32")
toolbar.mouse_hover()
toolbar.find('name:"Start Recording"')
```

Also note that if you're targetting multiple versions of some application,
it's possilbe to use more advanced expressions with `or` and `and` conditions
(by default the `and` is not needed as a `space` will mean `and` implicitly).

For instance, the windows calculator has different ways to reach buttons 
depending on the Windows version, on some versions the name to reach
it would be `name:0` or `name:Zero`. In this case it'd be possible to
write a locator such as `class:Button and (name:0 or name:Zero)`.
