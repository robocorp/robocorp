# These are the keys for the values expected to be passed on to uiautomation.
from typing import List, Literal, Set, TypedDict, Union

_UIAutomationSearchTypeKeys = Literal[
    "AutomationId",
    "ClassName",
    "searchDepth",
    "Name",
    "RegexName",
    "SubName",
    "ControlType",
    "foundIndex",
    "offset",
    "desktop",
    "process",
    "handle",
    "executable",
    "path",
]


LocatorStrategyValues = Union[int, str, bool, List[int]]


# This is the information that the user can use to create a locator.
SearchType = TypedDict(
    "SearchType",
    {
        "automationid": str,
        "id": str,
        "class": str,
        "control": str,
        "depth": int,
        "name": str,
        "regex": str,
        "subname": str,
        "type": str,
        "index": int,
        "offset": str,
        "desktop": str,
        "process": str,
        "handle": int,
        "executable": str,
        "path": List[int],
    },
    total=False,
)

# The valid locator names that the user can use.
_LocatorKeys = Literal[
    "automationid",
    "id",
    "class",
    "control",
    "depth",
    "name",
    "regex",
    "subname",
    "type",
    "index",
    "offset",
    "desktop",
    "process",
    "handle",
    "executable",
    "path",
]

# The valid locator names that the user can use (as a set).

_valid_strategies: Set[str] = {
    "automationid",
    "id",
    "class",
    "control",
    "depth",
    "name",
    "regex",
    "subname",
    "type",
    "index",
    "offset",
    "desktop",
    "process",
    "handle",
    "executable",
    "path",
}


_strategies_accepting_multiple_strings: Set[str] = {
    # "automationid",
    # "id",
    # "class",
    # "control",
    # "depth",
    "name",
    "regex",
    "subname",
    # "type",
    # "index",
    # "offset",
    # "desktop",
    # "process",
    # "handle",
    # "executable",
    # "path",
}
