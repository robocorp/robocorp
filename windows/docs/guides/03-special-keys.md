# Special keys

It's possible to send special keys (using the [send_keys](https://github.com/robocorp/robocorp/blob/master/windows/docs/api/robocorp.windows.md#method-send_keys) method) 
by wrapping the related code below with `{}` (Example: `{Ctrl}`, `{Enter}`). 

| Key code            | Key description                                                          |
| --------------------|--------------------------------------------------------------------------|
| LBUTTON             | Left mouse button                                                        | 
| RBUTTON             | Right mouse button                                                       |
| CANCEL              | Control-break processing                                                 |
| MBUTTON             | Middle mouse button (three-button mouse)                                 |
| XBUTTON1            | X1 mouse button                                                          |
| XBUTTON2            | X2 mouse button                                                          |
| BACK                | BACKSPACE key                                                            |
| TAB                 | TAB key                                                                  |
| CLEAR               | CLEAR key                                                                |
| RETURN              | ENTER key                                                                |
| ENTER               | ENTER key                                                                |
| SHIFT               | SHIFT key                                                                |
| CTRL                | CTRL key                                                                 |
| CONTROL             | CTRL key                                                                 |
| ALT                 | ALT key                                                                  |
| PAUSE               | PAUSE key                                                                |
| CAPITAL             | CAPS LOCK key                                                            |
| KANA                | IME Kana mode                                                            |
| HANGUEL             | IME Hanguel mode (maintained for compatibility; use VK_HANGUL)           |
| HANGUL              | IME Hangul mode                                                          |
| JUNJA               | IME Junja mode                                                           |
| FINAL               | IME final mode                                                           |
| HANJA               | IME Hanja mode                                                           |
| KANJI               | IME Kanji mode                                                           |
| ESC                 | ESC key                                                                  |
| ESCAPE              | ESC key                                                                  |
| CONVERT             | IME convert                                                              |
| NONCONVERT          | IME nonconvert                                                           |
| ACCEPT              | IME accept                                                               |
| MODECHANGE          | IME mode change request                                                  |
| SPACE               | SPACEBAR                                                                 |
| PRIOR               | PAGE UP key                                                              |
| PAGEUP              | PAGE UP key                                                              |
| NEXT                | PAGE DOWN key                                                            |
| PAGEDOWN            | PAGE DOWN key                                                            |
| END                 | END key                                                                  |
| HOME                | HOME key                                                                 |
| LEFT                | LEFT ARROW key                                                           |
| UP                  | UP ARROW key                                                             |
| RIGHT               | RIGHT ARROW key                                                          |
| DOWN                | DOWN ARROW key                                                           |
| SELECT              | SELECT key                                                               |
| PRINT               | PRINT key                                                                |
| EXECUTE             | EXECUTE key                                                              |
| SNAPSHOT            | PRINT SCREEN key                                                         |
| PRINTSCREEN         | PRINT SCREEN key                                                         |
| INSERT              | INS key                                                                  |
| INS                 | INS key                                                                  |
| DELETE              | DEL key                                                                  |
| DEL                 | DEL key                                                                  |
| HELP                | HELP key                                                                 |
| WIN                 | Left Windows key (Natural keyboard)                                      |
| LWIN                | Left Windows key (Natural keyboard)                                      |
| RWIN                | Right Windows key (Natural keyboard)                                     |
| APPS                | Applications key (Natural keyboard)                                      |
| SLEEP               | Computer Sleep key                                                       |
| NUMPAD0             | Numeric keypad 0 key                                                     |
| NUMPAD1             | Numeric keypad 1 key                                                     |
| NUMPAD2             | Numeric keypad 2 key                                                     |
| NUMPAD3             | Numeric keypad 3 key                                                     |
| NUMPAD4             | Numeric keypad 4 key                                                     |
| NUMPAD5             | Numeric keypad 5 key                                                     |
| NUMPAD6             | Numeric keypad 6 key                                                     |
| NUMPAD7             | Numeric keypad 7 key                                                     |
| NUMPAD8             | Numeric keypad 8 key                                                     |
| NUMPAD9             | Numeric keypad 9 key                                                     |
| MULTIPLY            | Multiply key                                                             |
| ADD                 | Add key                                                                  |
| SEPARATOR           | Separator key                                                            |
| SUBTRACT            | Subtract key                                                             |
| DECIMAL             | Decimal key                                                              |
| DIVIDE              | Divide key                                                               |
| F1                  | F1 key                                                                   |
| F2                  | F2 key                                                                   |
| F3                  | F3 key                                                                   |
| F4                  | F4 key                                                                   |
| F5                  | F5 key                                                                   |
| F6                  | F6 key                                                                   |
| F7                  | F7 key                                                                   |
| F8                  | F8 key                                                                   |
| F9                  | F9 key                                                                   |
| F10                 | F10 key                                                                  |
| F11                 | F11 key                                                                  |
| F12                 | F12 key                                                                  |
| F13                 | F13 key                                                                  |
| F14                 | F14 key                                                                  |
| F15                 | F15 key                                                                  |
| F16                 | F16 key                                                                  |
| F17                 | F17 key                                                                  |
| F18                 | F18 key                                                                  |
| F19                 | F19 key                                                                  |
| F20                 | F20 key                                                                  |
| F21                 | F21 key                                                                  |
| F22                 | F22 key                                                                  |
| F23                 | F23 key                                                                  |
| F24                 | F24 key                                                                  |
| NUMLOCK             | NUM LOCK key                                                             |
| SCROLL              | SCROLL LOCK key                                                          |
| LSHIFT              | Left SHIFT key                                                           |
| RSHIFT              | Right SHIFT key                                                          |
| LCONTROL            | Left CONTROL key                                                         |
| LCTRL               | Left CONTROL key                                                         |
| RCONTROL            | Right CONTROL key                                                        |
| RCTRL               | Right CONTROL key                                                        |
| LALT                | Left MENU key                                                            |
| RALT                | Right MENU key                                                           |
| BROWSER_BACK        | Browser Back key                                                         |
| BROWSER_FORWARD     | Browser Forward key                                                      |
| BROWSER_REFRESH     | Browser Refresh key                                                      |
| BROWSER_STOP        | Browser Stop key                                                         |
| BROWSER_SEARCH      | Browser Search key                                                       |
| BROWSER_FAVORITES   | Browser Favorites key                                                    |
| BROWSER_HOME        | Browser Start and Home key                                               |
| VOLUME_MUTE         | Volume Mute key                                                          |
| VOLUME_DOWN         | Volume Down key                                                          |
| VOLUME_UP           | Volume Up key                                                            |
| MEDIA_NEXT_TRACK    | Next Track key                                                           |
| MEDIA_PREV_TRACK    | Previous Track key                                                       |
| MEDIA_STOP          | Stop Media key                                                           |
| MEDIA_PLAY_PAUSE    | Play/Pause Media key                                                     |
| LAUNCH_MAIL         | Start Mail key                                                           |
| LAUNCH_MEDIA_SELECT | Select Media key                                                         |
| LAUNCH_APP1         | Start Application 1 key                                                  |
| LAUNCH_APP2         | Start Application 2 key                                                  |
| OEM_1               | Used for miscellaneous characters; it can vary by keyboard.For the US standard keyboard, the ';:' key |
| OEM_PLUS            | For any country/region, the '+' key                                      |
| OEM_COMMA           | For any country/region, the ',' key                                      |
| OEM_MINUS           | For any country/region, the '-' key                                      |
| OEM_PERIOD          | For any country/region, the '.' key                                      |
| OEM_2               | Used for miscellaneous characters; it can vary by keyboard.              |
| OEM_3               | Used for miscellaneous characters; it can vary by keyboard.              |
| OEM_4               | Used for miscellaneous characters; it can vary by keyboard.              |
| OEM_5               | Used for miscellaneous characters; it can vary by keyboard.              |
| OEM_6               | Used for miscellaneous characters; it can vary by keyboard.              |
| OEM_7               | Used for miscellaneous characters; it can vary by keyboard.              |
| OEM_8               | Used for miscellaneous characters; it can vary by keyboard.              |
| OEM_102             | Either the angle bracket key or the backslash key on the RT 102-key keyboard |
| PROCESSKEY          | IME PROCESS key                                                          |
| PACKET              | Used to pass Unicode characters as if they were keystrokes. The VK_PACKET key is the low word of a 32-bit Virtual Key value used for non-keyboard input methods. For more information, see Remark in KEYBDINPUT, SendInput, WM_KEYDOWN, and WM_KeyUp |
| ATTN                | Attn key                                                                 |
| CRSEL               | CrSel key                                                                |
| EXSEL               | ExSel key                                                                |
| EREOF               | Erase EOF key                                                            |
| PLAY                | Play key                                                                 |
| ZOOM                | Zoom key                                                                 |
| NONAME              | Reserved                                                                 |
| PA1                 | PA1 key                                                                  |
| OEM_CLEAR           | Clear key                                                                |
