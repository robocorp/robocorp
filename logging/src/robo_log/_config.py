from typing import Optional, Sequence, Dict
from collections import namedtuple
import enum
import robo_log

_ROBO_LOG_MODULE_NAME = robo_log.__name__

# Examples:
# Filter("mymodule.ignore", kind="exclude")
# Filter("mymodule.rpa", kind="full_log")
# Filter("RPA", kind="log_on_project_call")
Filter = namedtuple("Filter", "name, kind")


class FilterKind(enum.Enum):
    full_log = "full"
    log_on_project_call = "call"
    exclude = "exc"


class BaseConfig:
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

    def get_rewrite_assigns(self) -> bool:
        """
        Returns:
            True if assign statements should be rewritten so that assigns
            appear in the log and False otherwise.
        """
        raise NotImplementedError()


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
    ):
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

        absolute_filename = robo_log._files_filtering._absolute_normalized_path(
            filename
        )

        cache_key = absolute_filename
        try:
            return self._cache_filename_to_kind[cache_key]
        except KeyError:
            pass

        exclude = not robo_log._in_project_roots(absolute_filename)
        if exclude:
            filter_kind = FilterKind.exclude
        else:
            filter_kind = FilterKind.full_log

        self._cache_filename_to_kind[cache_key] = filter_kind
        return filter_kind
