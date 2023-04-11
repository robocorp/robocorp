from typing import Optional, Sequence
from collections import namedtuple

# Examples:
# Filter("mymodule.ignore", exclude=True, is_path=False)
# Filter("mymodule.rpa", exclude=False, is_path=False)
# Filter("**/check/**", exclude=True, is_path=True)
Filter = namedtuple("Filter", "name, exclude, is_path")


class BaseConfig:
    def can_rewrite_module_name(self, module_name: str) -> bool:
        raise NotImplementedError()

    def can_rewrite_module(self, module_name: str, filename: str) -> bool:
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
    ):
        from robocorp_logging._rewrite_filtering import FilesFiltering

        self._files_filtering = FilesFiltering(project_roots, library_roots, filters)

    def can_rewrite_module_name(self, module_name: str) -> bool:
        if module_name.startswith("robocorp_logging"):
            # We can't rewrite our own modules (we could end up recursing).
            if "check" in module_name:
                # Exception just for testing.
                return True
            return False

        return self._files_filtering.accept_module_name(module_name)

    def can_rewrite_module(self, module_name: str, filename: str) -> bool:
        return self._files_filtering.accept(filename, module_name)
