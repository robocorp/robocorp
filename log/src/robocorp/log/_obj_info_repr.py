from typing import Tuple, Any


def get_obj_type_and_repr(obj: Any) -> Tuple[str, str]:
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
    return val_type, r
