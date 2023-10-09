import itertools
import logging
import typing
from typing import Optional

import win32api
import win32con
import win32gui
import win32ui

log = logging.getLogger(__name__)


if typing.TYPE_CHECKING:
    from PIL.Image import Image


def get_icon_from_file(filepath: str) -> Optional["Image"]:
    small, large = win32gui.ExtractIconEx(filepath, 0, 1)
    if len(large) <= 0:
        return None  # no icon to extract

    try:
        from PIL import Image

        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        try:
            ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
            ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
            hbmp = win32ui.CreateBitmap()
            try:
                hbmp.CreateCompatibleBitmap(hdc, ico_x, ico_y)
                hdc2 = hdc.CreateCompatibleDC()
                try:
                    hdc2.SelectObject(hbmp)
                    hdc2.DrawIcon((0, 0), large[0])
                finally:
                    hdc2.DeleteDC()

                info = hbmp.GetInfo()
                bits = hbmp.GetBitmapBits(True)
                img = Image.frombytes(
                    "RGB", (info["bmWidth"], info["bmHeight"]), bits, "raw", "BGRX"
                )

                return img
            finally:
                win32gui.DeleteObject(hbmp.GetHandle())
        finally:
            hdc.DeleteDC()
    finally:
        # According to
        # https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-extracticonexa
        # When they are no longer needed, you must destroy all icons extracted
        # by ExtractIconEx by calling the DestroyIcon function.
        for icon_handle in itertools.chain(small, large):
            win32gui.DestroyIcon(icon_handle)
