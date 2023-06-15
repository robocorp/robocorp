import enum
from collections import namedtuple
from typing import Dict, Optional, Sequence

from robocorp import log

_ROBO_LOG_MODULE_NAME = log.__name__

# Examples:
# Filter("mymodule.ignore", kind="exclude")
# Filter("mymodule.rpa", kind="full_log")
# Filter("RPA", kind="log_on_project_call")
Filter = namedtuple("Filter", "name, kind")


class FilterKind(enum.Enum):
    # Note: the values are the name which appears in the .pyc cache.
    full_log = "full"
    log_on_project_call = "call"
    exclude = "exc"


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


class BaseConfig:
    def __init__(
        self,
        rewrite_assigns=True,
        rewrite_yields=True,
        min_messages_per_file=50,
    ):
        self.rewrite_assigns = rewrite_assigns
        self.rewrite_yields = rewrite_yields
        self._min_messages_per_file = min_messages_per_file

    def get_min_messages_per_file(self) -> int:
        return self._min_messages_per_file

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


class ConfigFilesFiltering(BaseConfig):
    """
    A configuration in which modules are rewritten if they are considered "project" modules.

    If no arguments are passed, python is queried for the paths that are "library" paths
    and "project" paths are all that aren't inside the "library" paths.

    If "project_roots" is passed, then any file inside one of those folders is considered
    to be a file to be rewritten.
    """

    def __init__(
        self,
        filters: Sequence[Filter] = (),
        rewrite_assigns=True,
        rewrite_yields=True,
    ):
        super().__init__(rewrite_assigns=rewrite_assigns, rewrite_yields=rewrite_yields)
        self._filters = filters
        self._cache_modname_to_kind: Dict[str, Optional[FilterKind]] = {}
        self._cache_filename_to_kind: Dict[str, FilterKind] = {}

    def get_filter_kind_by_module_name(self, module_name: str) -> Optional[FilterKind]:
        if module_name.startswith(_ROBO_LOG_MODULE_NAME):
            # We can't rewrite our own modules (we could end up recursing).
            if "check" in module_name:
                # Exception just for testing.
                return FilterKind.full_log
            return FilterKind.exclude

        return self._get_modname_filter_kind(module_name)

    def get_filter_kind_by_module_name_and_path(
        self, module_name: str, filename: str
    ) -> FilterKind:
        return self._get_modname_or_file_filter_kind(filename, module_name)

    # --- Internal APIs

    def _compute_filter_kind(self, module_name: str) -> Optional[FilterKind]:
        """
        :return: True if it should be excluded, False if it should be included and None
            if no rule matched the given file.
        """
        for exclude_filter in self._filters:
            if exclude_filter.name == module_name or module_name.startswith(
                exclude_filter.name + "."
            ):
                return exclude_filter.kind
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

        exclude = not log._in_project_roots(absolute_filename)
        if exclude:
            filter_kind = FilterKind.exclude
        else:
            filter_kind = FilterKind.full_log

        self._cache_filename_to_kind[cache_key] = filter_kind
        return filter_kind
