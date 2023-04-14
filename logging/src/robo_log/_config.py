from typing import Optional, Sequence
from collections import namedtuple
import enum

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
        project_roots: Optional[Sequence[str]] = None,
        library_roots: Optional[Sequence[str]] = None,
        filters: Sequence[Filter] = (),
        set_as_global: bool = False,
    ):
        from robo_log._rewrite_filtering import FilesFiltering

        self._files_filtering = FilesFiltering(project_roots, library_roots, filters)
        if set_as_global:
            import robo_log

            robo_log._in_project_roots = self._files_filtering.in_project_roots

    def get_filter_kind_by_module_name(self, module_name: str) -> Optional[FilterKind]:
        if module_name.startswith("robo_log"):
            # We can't rewrite our own modules (we could end up recursing).
            if "check" in module_name:
                # Exception just for testing.
                return FilterKind.full_log
            return FilterKind.exclude

        return self._files_filtering.get_modname_filter_kind(module_name)

    def get_filter_kind_by_module_name_and_path(
        self, module_name: str, filename: str
    ) -> FilterKind:
        return self._files_filtering.get_modname_or_file_filter_kind(
            filename, module_name
        )
