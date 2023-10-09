import functools
import logging
import re
from dataclasses import dataclass, field
from typing import List, Literal, Set, Tuple, TypedDict, Union

log = logging.getLogger(__name__)


# These are the keys for the values expected to be passed on to uiautomation.
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

LocatorStrategyValues = Union[int, str, bool, List[int]]


# See: MatchObject.add_locator
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


@dataclass
class MatchObject:
    """Represents all locator parts as object properties"""

    # Assign to class scope.
    TREE_SEP = " > "
    PATH_SEP = "|"  # path locator index separator
    QUOTE = '"'  # enclosing quote character
    _LOCATOR_REGEX = re.compile(rf"\S*{QUOTE}[^{QUOTE}]+{QUOTE}|\S+", re.IGNORECASE)
    _LOGGER = logging.getLogger(__name__)

    locators: List[Tuple[_LocatorKeys, LocatorStrategyValues, int]] = field(
        default_factory=list
    )
    _classes: Set[str] = field(default_factory=set)
    max_level: int = 0

    def as_search_params(self) -> SearchType:
        search_params: SearchType = {}
        for loc in self.locators:
            search_params[loc[0]] = loc[1]
        return search_params

    @classmethod
    def parse_locator(cls, locator: str) -> "MatchObject":
        match_object = MatchObject()
        locator_tree = [loc.strip() for loc in locator.split(cls.TREE_SEP)]
        for level, branch in enumerate(locator_tree):
            default_values: List[str] = []
            for part in cls._LOCATOR_REGEX.finditer(branch):
                match_object.handle_locator_part(
                    level, part.group().strip(), default_values
                )
            if default_values:
                match_object.add_locator("name", " ".join(default_values), level=level)
        if not match_object.locators:
            match_object.add_locator("name", locator)
        return match_object

    def handle_locator_part(
        self, level: int, part_text: str, default_values: List[str]
    ) -> None:
        if not part_text:
            return

        add_locator = functools.partial(self.add_locator, level=level)

        if part_text in ("and", "or", "desktop"):
            # NOTE(cmin764): Only "and" is supported at the moment. (match type is
            #  ignored and spaces are treated as "and"s by default)
            if part_text == "desktop":
                add_locator("desktop", "desktop")
            return

        try:
            strategy, value = part_text.split(":", 1)
        except ValueError:
            log.warning(
                f"No locator strategy found in: {part_text!r} "
                f"(using: 'name:\"{part_text}\"' as the locator).\n"
                f"Valid strategies: {tuple(SearchType.__annotations__.keys())}."
            )

            default_values.append(part_text)
            return

        if strategy == "automationid":
            strategy = "id"
        if strategy == "type":
            strategy = "control"

        if strategy in SearchType.__annotations__:
            if default_values:
                add_locator("name", " ".join(default_values))
                default_values.clear()
            add_locator(strategy, value)
        else:
            log.warning(
                f"Possibly invalid locator strategy: {strategy!r} "
                f"(using: 'name:\"{part_text}\"' as the locator).\n"
                f"Valid strategies: {tuple(SearchType.__annotations__.keys())}."
            )
            default_values.append(part_text)

    def add_locator(
        self,
        control_strategy: _LocatorKeys,
        value: str,
        level: int = 0,
    ) -> None:
        value = value.strip(f"{self.QUOTE} ")
        if not value:
            return

        self.max_level = max(self.max_level, level)

        use_value: LocatorStrategyValues = value
        if control_strategy in ("index", "depth", "handle"):
            use_value = int(value)
        elif control_strategy == "control":
            use_value = value if value.endswith("Control") else f"{value}Control"
        elif control_strategy == "class":
            self._classes.add(value.lower())
        elif control_strategy == "path":
            use_value = [
                int(idx)
                for idx in value.strip(f" {self.PATH_SEP}").split(self.PATH_SEP)
            ]

        self.locators.append((control_strategy, use_value, level))

    @property
    def classes(self) -> List[str]:
        return list(self._classes)
