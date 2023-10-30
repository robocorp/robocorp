import logging
import typing
from typing import Optional

if typing.TYPE_CHECKING:
    from PIL.Image import Image

    from ._vendored.uiautomation.uiautomation import Control


log = logging.getLogger(__name__)


def screenshot(control: "Control") -> Optional["Image"]:
    """
    Returns:
        A PIL image with the contents of the bitmap.
    """
    from PIL import Image

    try:
        bitmap = control.ToBitmap()
    except AttributeError:
        log.info(f"Unable to take screenshot of {control} (ToBitmap not available).")
        return None
    if bitmap is None:
        return None
    w, h = bitmap.Width, bitmap.Height
    bits = bitmap.GetAllPixelColors()
    img = Image.frombuffer("RGB", (w, h), bits, "raw", "BGRX")

    # img.save("c:/temp/my2.png", format="PNG")
    return img


def screenshot_as_base64png(control: "Control") -> Optional[str]:
    """
    Returns:
        The image with the contents as a base64 png.
    """
    import base64
    from io import BytesIO

    img = screenshot(control)
    if img is None:
        return None

    buffered = BytesIO()

    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()
