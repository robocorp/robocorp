from typing import Any, Tuple

from . import _config, suppress


def get_obj_type_and_repr(obj: Any) -> Tuple[str, str]:
    with suppress():
        # Anything called during a repr must be suppressed.
        try:
            val_type = obj.__class__.__name__
        except Exception:
            try:
                val_type = str(type(obj))
            except Exception:
                val_type = "<type unavailable>"
            except RecursionError:
                val_type = "<recursion error getting type>"

        try:
            r = repr(obj)
        except (Exception, RecursionError) as e:
            r = f"<error getting repr: {e}>"

        max_size = _config._general_log_config.max_value_repr_size
        if len(r) > max_size:
            diff = len(r) - max_size
            r = f"{r[:max_size]} <clipped {diff} chars>"

        return val_type, r
