from typing import Any, Tuple

from . import _config
from . import suppress


def get_obj_type_and_repr(obj: Any) -> Tuple[str, str]:
    with suppress():
        # Anything called during a repr must be suppressed.
        try:
            val_type = obj.__class__.__name__
        except:
            try:
                val_type = str(type(obj))
            except:
                val_type = "<type unavailable>"

        try:
            r = repr(obj)
        except Exception as e:
            r = f"<error getting repr: {e}>"

        max_size = _config._general_log_config.get_max_value_repr_size()
        if len(r) > max_size:
            diff = len(r) - max_size
            r = f"{r[:max_size]} <clipped {diff} chars>"

        return val_type, r
