# ruff: noqa: E501
import logging
from typing import List, Optional, Tuple, Union

from ._errors import InvalidLocatorError
from ._match_common import (
    LocatorStrategyValues,
    SearchType,
    _LocatorKeys,
    _valid_strategies,
)
from .protocols import Locator

# This function is the only public API of this module. Everything else
# should be considered an implementation detail.

log = logging.getLogger(__name__)


def collect_search_params(
    locator: Locator, *, _cache={}
) -> Tuple["OrSearchParams", ...]:
    """
    Args:
        locator: The locator for which the search parameters are wanted.

    Returns:
        A tuple where each entry represents a level and each level has a single
        'OrSearchParams' for the matching (note that the returned 'OrSearchParams'
        should be comprised only of 'SearchParams' and it's possible that
        there's a single 'SearchParams' in it).
    """
    try:
        ret = _cache[locator]
    except KeyError:
        locator_match = _build_locator_match(locator)
        for warning in locator_match.warnings:
            log.warn(warning)
        only_ors: List[OrSearchParams] = []
        for params in locator_match.flattened:
            if isinstance(params, OrSearchParams):
                only_ors.append(params)
            else:
                if not isinstance(params, SearchParams):
                    raise InvalidLocatorError(
                        "Unable to flatten the or/and conditions as expected in the "
                        "locator.\nPlease report this as an error to robocorp-windows."
                        f"\nLocator: {locator}"
                    )
                if params.empty():
                    raise InvalidLocatorError(
                        "Unable to flatten the or/and conditions as expected in the "
                        "locator.\nPlease report this as an error to robocorp-windows."
                        f"\nLocator: {locator}"
                    )
                only_ors.append(OrSearchParams(params))
        ret = _cache[locator] = tuple(only_ors)
    return tuple(x.copy() for x in ret)


class _AbstractAstNode:
    """
    Base class for the AST nodes.
    """

    def empty(self) -> bool:
        raise NotImplementedError()

    def add_strategy(
        self,
        strategy: _LocatorKeys,
        value: str,
    ) -> None:
        raise NotImplementedError()

    def copy(self) -> "_AbstractAstNode":
        raise NotImplementedError()


class SearchParams(_AbstractAstNode):
    """
    This is a container class where the search parameters are actually stored.

    i.e.: a locator as `depth:1 name:Foo` will have as search params a
    dict with {'depth': 1, 'name': 'Foo'}.
    """

    def __init__(self) -> None:
        self.search_params: SearchType = {}

    def copy(self) -> "SearchParams":
        new_params = SearchParams()
        new_params.search_params = self.search_params.copy()
        return new_params

    def update(self, other: "SearchParams"):
        from ._errors import InvalidStrategyDuplicated

        search_params = self.search_params
        for strategy, value in other.search_params.items():
            if strategy in search_params:
                raise InvalidStrategyDuplicated(
                    f"Error: the strategy: {strategy!r} is already defined with: "
                    f"'{search_params[strategy]}' (unable to redefine it with: "  # type:ignore
                    f"'{value}')."
                )
            search_params[strategy] = value  # type:ignore

    def add_strategy(
        self,
        strategy: _LocatorKeys,
        value: str,
    ) -> None:
        from ._errors import InvalidStrategyDuplicated

        assert strategy in _valid_strategies
        assert isinstance(value, str)
        if not value:
            return

        if strategy == "automationid":
            strategy = "id"
        if strategy == "type":
            strategy = "control"

        use_value: LocatorStrategyValues = value
        if strategy in ("index", "depth", "handle"):
            use_value = int(value)
        elif strategy == "control":
            use_value = value if value.endswith("Control") else f"{value}Control"
        elif strategy == "path":
            use_value = [int(idx) for idx in value.strip(" |").split("|")]

        if strategy in self.search_params:
            raise InvalidStrategyDuplicated(
                f"Error: the strategy: {strategy!r} is already defined with: "
                f"'{self.search_params[strategy]}' (unable to redefine it with: "
                f"'{value}')."
            )

        self.search_params[strategy] = use_value

    def empty(self):
        return len(self.search_params) == 0

    def __str__(self):
        def fmt(s):
            s = str(s)
            if not s:
                return '""'

            if " " in s:
                s = f'"{s}"'
            return s

        ret = []
        for k, v in self.search_params.items():
            ret.append(f"{k}:{fmt(v)}")

        return "Search(" + " ".join(ret) + ")"

    __repr__ = __str__


class _ImmutableList(list):  # Helper class just to make sure this won't be mutated.
    def append(self, item):
        raise AssertionError("Immutable")

    def extend(self, items):
        raise AssertionError("Immutable")


class _AbstractPartsAstNode(_AbstractAstNode):
    """
    A node which has multiple other parts inside it.
    """

    # A list, but make sure that the default instance is not mutated (subclasses
    # should initialize in the instance as needed).
    parts: List[_AbstractAstNode] = _ImmutableList()

    # If True adding a new strategy will first add a new SearchParams class.
    on_first_append_create: bool = True

    def empty(self):
        for p in self.parts:
            if not p.empty():
                return False
        return True

    def add_strategy(self, *args, **kwargs) -> None:
        if self.on_first_append_create:
            self.parts.append(SearchParams())
            self.on_first_append_create = False
        self.parts[-1].add_strategy(*args, **kwargs)


class _LocatorMatch(_AbstractPartsAstNode):
    """
    The object which has the state related to building up the locator AST
    from the locator text.
    """

    def __init__(self, locator: Locator) -> None:
        self.locator = locator

        # The parts are temporary information while building the ast.
        self.parts = []

        # Warnings found when building the AST.
        self.warnings: List[str] = []

        # This is what we should actually match with (each new '>' entry adds
        # a new entry here), close to what the AST has.
        self.levels: List[_MatchOneLevelParams] = []

        # The flattened version, each entry represents one level and it's flattened
        # so that it's a single or with multiple parts or a single search parameter
        # to be matched for each level.
        # This is the information that should be used when actually doing a match.
        self.flattened: List[Union[SearchParams, OrSearchParams]]

    def add_warning(self, msg: str):
        self.warnings.append(msg)

    def __str__(self):
        contents = []

        if self.flattened:
            for i, node in enumerate(self.flattened):
                contents.append(str(node))
                if not i == len(self.flattened) - 1:
                    # Last one
                    contents.append(">")
        elif self.levels:
            # Should the info that's not flattened yet.
            for i, level in enumerate(self.levels):
                contents.append(str(level))
                if not i == len(self.levels) - 1:
                    # Last one
                    contents.append(">")

        if self.parts:
            # If there are any parts show it (should only appear
            # while building the ast).
            contents.append("Building (locator parts):\n")
            for part in self.parts:
                contents.append(str(part))

        return " ".join(contents)

    __repr__ = __str__

    def _build_level(self):
        found_parts = [p for p in self.parts if not p.empty()]
        if not found_parts:
            raise InvalidLocatorError(
                f"Error. No search parameters defined (at level: {len(self.levels)})."
            )
        self.levels.append(_MatchOneLevelParams(found_parts))

    def push_match_child(self):
        self._build_level()
        self.on_first_append_create = True
        self.parts = []

    def finish_locator(self) -> None:
        self._build_level()
        self.parts = []

        # Now, let's flatten our conditions so that we just have 1-level
        # to check (so, at the root we have either a single OrSearchParams() with
        # all the 'or' conditions or just one SearchParams).
        curr_levels: List[_MatchOneLevelParams] = self.levels

        for _i in range(100):
            is_fully_flattened = True
            new_levels: List[_MatchOneLevelParams] = []
            for level in curr_levels:
                flattened = self._flatten(level)

                # Verify that there are no nested or expressions
                # (a single pass may not be enough)
                if isinstance(flattened, OrSearchParams):
                    for part in flattened.parts:
                        if isinstance(part, OrSearchParams):
                            is_fully_flattened = False
                            break
                new_levels.append(_MatchOneLevelParams([flattened]))
            curr_levels = new_levels

            if is_fully_flattened:
                # At this point we know it's properly flattened.
                new_flattened: List[Union[SearchParams, OrSearchParams]] = []
                for level in curr_levels:
                    if len(level.parts) != 1:
                        raise InvalidLocatorError(
                            "Unable to flatten the or/and conditions as expected in "
                            "the locator.\n Please report this as an error to "
                            f"robocorp-windows.\nLocator: {self.locator}"
                        )
                    new_flattened.append(level.parts[0])
                self.flattened = new_flattened
                break
        else:
            raise InvalidLocatorError(
                "Unable to flatten the or/and conditions as expected in the locator.\n"
                "Please report this as an error to robocorp-windows.\n"
                f"Locator: {self.locator}"
            )

    def _flatten_or(self, or_expr) -> "OrSearchParams":
        assert isinstance(or_expr, OrSearchParams)
        parts: List[_AbstractAstNode] = []
        for part in or_expr.parts:
            if isinstance(part, _ParensExpr):
                parts.append(self._flatten(part))
            elif isinstance(part, OrSearchParams):
                inner_or = self._flatten_or(part)
                parts.extend(inner_or.parts)
            else:
                parts.append(part)
        ret = OrSearchParams(None)
        ret.parts = parts
        return ret

    def _flatten(self, level) -> Union[SearchParams, "OrSearchParams"]:
        if isinstance(level, (_MatchOneLevelParams, _ParensExpr)):
            root: Optional[Union[SearchParams, OrSearchParams]] = None

            for part in level.parts:
                if isinstance(part, _ParensExpr):
                    part = self._flatten(part)

                if isinstance(part, SearchParams):
                    # SearchParams is in practice an _AndExpr.
                    if root is None:
                        root = part
                    else:
                        if isinstance(root, SearchParams):
                            cp = root.copy()
                            cp.update(part)
                            root = cp

                        elif isinstance(root, OrSearchParams):
                            new_root_parts: List[_AbstractAstNode] = []
                            for root_part in root.parts:
                                if isinstance(root_part, SearchParams):
                                    root_part = root_part.copy()
                                    root_part.update(part)
                                    new_root_parts.append(root_part)

                            root.parts = new_root_parts

                elif isinstance(part, OrSearchParams):
                    part = self._flatten_or(part)
                    if root is None:
                        root = part
                    else:
                        if isinstance(root, OrSearchParams):
                            root.parts.extend(part.parts)
                        elif isinstance(root, SearchParams):
                            part.parts.insert(0, root)
                            root = part

                else:
                    raise InvalidLocatorError(
                        f"Error: Unable to recognize part: {type(part)}."
                    )

            if root is None:
                raise InvalidLocatorError(
                    f"Unable to flatten condition. Empty part found in {level}."
                )
            return root
        else:
            raise InvalidLocatorError(
                f"Unable to flatten condition. Expected either _MatchOneLevelParams or "
                f"_ParensExpr. Found: {type(level)}"
            )


class _MatchOneLevelParams:
    def __init__(self, parts):
        assert len(parts)
        self.parts = parts

    def empty(self) -> bool:
        # We don't build it if not empty!
        return False

    def __str__(self):
        contents = []
        for part in self.parts:
            contents.append(str(part))
        return " ".join(contents)

    __repr__ = __str__


class _ParensExpr(_AbstractPartsAstNode):
    def __init__(self):
        self.parts = []

    def __str__(self):
        contents = []
        for part in self.parts:
            contents.append(str(part))
        return "Parens(" + " ".join(contents) + ")"

    __repr__ = __str__


class OrSearchParams(_AbstractPartsAstNode):
    def __init__(self, search_params):
        if search_params and not search_params.empty():
            self.parts = [search_params]
        else:
            self.parts = []

    def copy(self) -> "OrSearchParams":
        ret = OrSearchParams(None)
        ret.parts = [p.copy() for p in self.parts]
        return ret

    def __str__(self):
        contents = []
        for part in self.parts:
            contents.append(str(part))
        return "Or(" + " or ".join(contents) + ")"

    __repr__ = __str__


class _StrategyBuilder:
    def __init__(self, strategy: str):
        from ._match_common import _strategies_accepting_multiple_strings
        from ._match_tokenization import Token

        self.strategy = strategy
        self.values: List[Token] = []
        self.accepts_multiple_strings = (
            strategy in _strategies_accepting_multiple_strings
        )

    def insert_strategy(self, locator_match: _LocatorMatch, stack):
        v = " ".join(v.token for v in self.values)
        if v.startswith("'") and v.endswith("'"):
            locator_match.add_warning(
                'Strings should be enclosed with " (double quotes), strings enclosed'
                " with single quotes will use the single quote as a part of the match."
            )
        stack[-1].add_strategy(self.strategy, v)


def _build_locator_match(locator: Locator) -> _LocatorMatch:
    """
    Args:
        locator: The locator to be parsed.

    Raises: InvalidLocatorError if the locator is not valid.
    """
    if not locator.strip():
        raise InvalidLocatorError("The locator may not be empty.")
    from ._match_tokenization import Token, TokenKind, _Tokenizer

    locator_match = _LocatorMatch(locator)

    stack: list = [locator_match]

    strategy_builder: Optional[_StrategyBuilder] = None

    require_next: Tuple[TokenKind, ...] = ()
    prev: Optional[Token] = None

    parens_level = 0

    tokenizer = _Tokenizer(locator)
    for tok in tokenizer.tokenize():
        if require_next:
            if tok.kind not in require_next:
                if not prev:
                    raise InvalidLocatorError(
                        "Internal error. Expected prev to be defined."
                    )

                prev_token = prev.token
                next_expected = "', '".join(tuple(x.name for x in require_next))
                raise InvalidLocatorError(
                    f"Error. Expected token after '{prev_token}' to be of kind: "
                    f"'{next_expected}'. Found: '{tok}'"
                )
            require_next = ()

        prev = tok

        if tok.kind == TokenKind.desktop:
            stack[-1].add_strategy("desktop", "desktop")
            continue

        # These 2 can change the strategy
        if tok.kind == TokenKind.strategy:
            if strategy_builder is not None:
                strategy_builder.insert_strategy(locator_match, stack)
            strategy_builder = _StrategyBuilder(tok.token)
            require_next = (TokenKind.value,)
            continue

        elif tok.kind == TokenKind.value:
            if strategy_builder is not None and tok.quoted:
                # This one is a token by itself, it cannot be joined with
                # another value.
                if not strategy_builder is not None and strategy_builder.values:
                    strategy_builder.insert_strategy(locator_match, stack)
                    strategy_builder = None

            if strategy_builder is None:
                # Consider it as 'name' strategy.
                strategy_builder = _StrategyBuilder("name")

                locator_match.add_warning(
                    f"No locator strategy found in: {tok.token!r} "
                    f"(using: 'name:\"{tok.token}\"' as the locator).\n"
                    f"Valid strategies: {tuple(sorted(_valid_strategies))}.",
                )

            strategy_builder.values.append(tok)

            if not strategy_builder.accepts_multiple_strings or tok.quoted:
                strategy_builder.insert_strategy(locator_match, stack)
                strategy_builder = None
            continue

        # The ones below don't change the strategy, but, it needs to be handled
        # before we get into it.
        if strategy_builder is not None:
            strategy_builder.insert_strategy(locator_match, stack)
            strategy_builder = None

        if tok.kind == TokenKind.parens_start:
            parens_expr = _ParensExpr()
            stack.append(parens_expr)
            parens_level += 1

        elif tok.kind == TokenKind.parens_end:
            parens_level -= 1
            if parens_level < 0:
                raise InvalidLocatorError("Unbalanced parenthesis.")

            while True:
                if not stack:  # Shouldn't really happen
                    raise InvalidLocatorError(
                        "Unbalanced parenthesis (possible internal error)."
                    )
                parens_expr = stack.pop()
                if isinstance(parens_expr, _ParensExpr):
                    break
            stack[-1].parts.append(parens_expr)
            # New elements should not be added to the parens anymore.
            stack[-1].on_first_append_create = True

        elif tok.kind == TokenKind.or_token:
            last_part = stack[-1].parts.pop(-1)
            or_expr = OrSearchParams(last_part)
            stack[-1].parts.append(or_expr)
            stack.append(or_expr)
            require_next = (
                TokenKind.parens_start,
                TokenKind.strategy,
                TokenKind.value,
                TokenKind.desktop,
            )

        elif tok.kind == TokenKind.and_token:
            require_next = (
                TokenKind.parens_start,
                TokenKind.strategy,
                TokenKind.value,
                TokenKind.desktop,
            )
            pass  # Ignore (by default it's 'and').

        elif tok.kind == TokenKind.match_child:
            # New scope (>)
            if parens_level != 0:
                raise InvalidLocatorError('">" may not appear inside parenthesis.')

            while len(stack) != 1:
                curr = stack.pop()
                if isinstance(curr, (_ParensExpr)):
                    raise InvalidLocatorError('">" may not appear inside parenthesis.')

            locator_match.push_match_child()

    if require_next:
        if not prev:
            raise InvalidLocatorError("Internal error. Expected prev to be defined.")
        prev_token = prev.token
        next_expected = "', '".join(tuple(x.name for x in require_next))
        raise InvalidLocatorError(
            f"Error. Expected token after '{prev_token}' to be of kind: "
            f"'{next_expected}'. Found the end of the locator instead."
        )

    if parens_level != 0:
        raise InvalidLocatorError("Unbalanced parenthesis.")

    if strategy_builder is not None:
        strategy_builder.insert_strategy(locator_match, stack)

    # Validate that the last level is not empty.
    locator_match.finish_locator()

    return locator_match
