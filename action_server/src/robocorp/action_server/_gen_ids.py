import itertools
from typing import Literal, Optional
from uuid import uuid4

_counters: dict = {}


def get_counter(counter_name: Optional[str] = None):
    try:
        return _counters[counter_name]
    except KeyError:
        _counters[counter_name] = itertools.count()
        return _counters[counter_name]


def gen_uuid(counter_name: Optional[Literal["action_package", "action", "run"]] = None):
    if not counter_name:
        prefix = ""
    elif counter_name == "action_package":
        prefix = "ap-"
    else:
        prefix = f"{str(counter_name)[0:3]}-"
    return f"{prefix}{next(get_counter(counter_name)):03d}-{uuid4()}"
