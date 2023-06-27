import enum
from typing import Dict, Optional, Sequence, Callable

from robocorp import log
from functools import partial
from fnmatch import fnmatch
import itertools
from dataclasses import dataclass

# Examples:
# Filter("mymodule.ignore", kind=FilterKind.exclude)
# Filter("mymodule.rpa", kind=FilterKind.full_log)
# Filter("RPA", kind=FilterKind.log_on_project_call)


class FilterKind(enum.Enum):
    # Note: the values are the name which appears in the .pyc cache.
    full_log = "full"
    log_on_project_call = "call"
    exclude = "exc"


@dataclass
class Filter:
    name: str
    kind: FilterKind


class GeneralLogConfig:
    __slots__ = ["max_value_repr_size"]

    def __init__(self) -> None:
        from ._convert_units import _convert_to_bytes

        # Setup defaults.
        self.max_value_repr_size: int = _convert_to_bytes("200k")

    def get_max_value_repr_size(self) -> int:
        return self.max_value_repr_size


# Default instance. Not exposed to clients.
_general_log_config = GeneralLogConfig()


class AutoLogConfigBase:
    def __init__(
        self,
        rewrite_assigns=True,
        rewrite_yields=True,
    ):
        self.rewrite_assigns = rewrite_assigns
        self.rewrite_yields = rewrite_yields

    def get_rewrite_yields(self) -> bool:
        """
        Returns:
            Whether yield pauses and resumes should be tracked. Note that
            not tracking those with user code which actually has yields may
            show weird representations as the contents of the caller of a
            generator function will show inside the generator.
        """
        return self.rewrite_yields

    def get_rewrite_assigns(self) -> bool:
        """
        Returns:
            Whether assigns should be tracked. When assigns are tracked,
            any assign in a module which has mapped to `FilterKind.full_log`
            will be logged.
        """
        return self.rewrite_assigns

    def get_filter_kind_by_module_name(self, module_name: str) -> Optional[FilterKind]:
        """
        Args:
            module_name: the name of the module to check.

        Returns:
            The filter kind or None if the filter kind couldn't be discovered
            just with the module name.
        """
        raise NotImplementedError()

    def get_filter_kind_by_module_name_and_path(
        self, module_name: str, filename: str
    ) -> FilterKind:
        """
        Args:
            module_name: the name of the module to check.

        Returns:
            The filter kind to be applied.
        """
        raise NotImplementedError()

    def set_as_global(self):
        """
        May be used to set this config as the global one to determine if a
        given file is in the project or not.
        """


class _FiterMatch:
    _match_filter: Callable[[str], bool]

    def __init__(self, filter: Filter) -> None:  # @ReservedAssignment
        self._filter = filter
        name = filter.name
        self._filter_name = name

        if "*" in name or "[" in name or "?" in name:
            self._match_filter = partial(self._fnmatch, name)
        else:
            self._match_filter = self._match_module_name

        self._kind = filter.kind

    def _fnmatch(self, pattern: str, module_name: str) -> bool:
        return fnmatch(module_name, pattern)

    def _match_module_name(self, module_name: str) -> bool:
        return self._filter_name == module_name or module_name.startswith(
            self._filter_name + "."
        )

    def get_filter_kind_match(self, module_name: str) -> Optional[FilterKind]:
        if self._match_filter(module_name):
            return self._kind
        return None


class DefaultAutoLogConfig(AutoLogConfigBase):
    """
    Configuration which provides information on which modules have to be rewritten
    and how to rewrite them based on filters.

    Note: Regular module names are accepted so that something as:

    `Filter("RPA", kind="log_on_project_call")`

    would match modules such as `RPA` or `RPA.Browser.Selenium` but not `RPA2`.

    Added in `robocorp.log 2.x`:

    Names can also be matched in `fnmatch` style, so, it's possible to create
    filters such as:

    `Filter("RPA.*", kind="log_on_project_call")`

    which would match only submodules starting with `RPA.` but would not
    match `RPA` directly.

    or even do something as:

    `Filter("*", kind="log_on_project_call")`

    which would match any module.

    Note: fnmatch-style filtering is used only if the name has a special
    character (such as `*`, `?` or `[`). Names without the special character
    match module names or submodules.

    Note that the order of the filter is important as filters are matched based
    on the ordering given, so, filters given first have higher priority as they
    are matched before filters which appear later.
    """

    def __init__(
        self,
        filters: Sequence[Filter] = (),
        rewrite_assigns=True,
        rewrite_yields=True,
        default_library_filter_kind=FilterKind.log_on_project_call,
    ):
        super().__init__(rewrite_assigns=rewrite_assigns, rewrite_yields=rewrite_yields)

        high_priority_filters = [
            # Make sure we don't log things internal to robocorp.log.
            Filter("robocorp.log", FilterKind.exclude),
            # Do you think there'll be anything good coming out of logging a debugger?
            # Exclude pydevd
            Filter("_pydev_*", FilterKind.exclude),
            Filter("_pydevd_*", FilterKind.exclude),
            Filter("pydev_*", FilterKind.exclude),
            Filter("pydevd_*", FilterKind.exclude),
            Filter("pydevd", FilterKind.exclude),
            Filter("pydevconsole", FilterKind.exclude),
            # Exclude pdb
            Filter("bdb", FilterKind.exclude),
            Filter("pdb", FilterKind.exclude),
            # The ones below are sensitive. Let's not log them.
            Filter("threading", FilterKind.exclude),
            Filter("queue", FilterKind.exclude),
            Filter("json", FilterKind.exclude),
            # Let's not log modules which aren't real.
            Filter("<*", FilterKind.exclude),
        ]

        low_priority_filters = [
            # The ones below aren't very interesting in general (exclude those
            # if no rule matching those was used).
            Filter("pkg_resources", FilterKind.exclude),
            Filter("collections", FilterKind.exclude),
            Filter("tkinter", FilterKind.exclude),
            Filter("unittest", FilterKind.exclude),
            Filter("linecache", FilterKind.exclude),
            Filter("string", FilterKind.exclude),
            Filter("trace", FilterKind.exclude),
            Filter("numpy", FilterKind.exclude),
            Filter("typing_extensions", FilterKind.exclude),
            Filter("pandas", FilterKind.exclude),
        ]

        has_robocorp_tasks = bool(
            tuple(f for f in filters if f.name == "robocorp.tasks")
        )
        if not has_robocorp_tasks:
            # If robocorp.tasks wasn't explicitly customized, add a high priority
            # rule for it.
            high_priority_filters.append(Filter("robocorp.tasks", FilterKind.exclude))

        self._filters = filters
        self._filter_matches = [
            _FiterMatch(f)
            for f in itertools.chain(
                high_priority_filters, filters, low_priority_filters
            )
        ]
        self._cache_modname_to_kind: Dict[str, Optional[FilterKind]] = {}
        self._cache_filename_to_kind: Dict[str, FilterKind] = {}
        self._default_library_filter_kind = default_library_filter_kind

    def _to_dict(self):
        return {
            "log_filter_rules": [
                {"name": f.name, "kind": str(f.kind).split(".")[-1]}
                for f in self._filters
            ],
            "default_library_filter_kind": str(self._default_library_filter_kind).split(
                "."
            )[-1],
        }

    def __repr__(self):
        import json

        return json.dumps(self._to_dict(), indent=2)

    def get_filter_kind_by_module_name(self, module_name: str) -> Optional[FilterKind]:
        return self._get_modname_filter_kind(module_name)

    def get_filter_kind_by_module_name_and_path(
        self, module_name: str, filename: str
    ) -> FilterKind:
        return self._get_modname_or_file_filter_kind(filename, module_name)

    # --- Internal APIs

    def _compute_filter_kind(self, module_name: str) -> Optional[FilterKind]:
        """
        :return: True if it should be excluded, False if it should be included
            and None if no rule matched the given file.
        """
        for filter_match in self._filter_matches:
            filter_kind_match = filter_match.get_filter_kind_match(module_name)
            if filter_kind_match is not None:
                return filter_kind_match
        return None

    def _get_modname_filter_kind(self, module_name: str) -> Optional[FilterKind]:
        cache_key = module_name
        try:
            return self._cache_modname_to_kind[cache_key]
        except KeyError:
            pass

        filter_kind = self._compute_filter_kind(module_name)
        self._cache_modname_to_kind[cache_key] = filter_kind
        return filter_kind

    def _get_modname_or_file_filter_kind(
        self, filename: str, module_name: str
    ) -> FilterKind:
        filter_kind = self._get_modname_filter_kind(module_name)
        if filter_kind is not None:
            return filter_kind

        absolute_filename = log._files_filtering._absolute_normalized_path(filename)

        cache_key = absolute_filename
        try:
            return self._cache_filename_to_kind[cache_key]
        except KeyError:
            pass

        in_project_roots = log._in_project_roots(absolute_filename)
        if in_project_roots:
            filter_kind = FilterKind.full_log
        else:
            filter_kind = self._default_library_filter_kind

        self._cache_filename_to_kind[cache_key] = filter_kind
        return filter_kind
