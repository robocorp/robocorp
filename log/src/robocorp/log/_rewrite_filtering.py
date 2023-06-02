import logging
import os.path
import platform
import sys
import threading
from typing import Dict, List, Optional, Sequence

log = logging.getLogger(__name__)


def normcase(s, NORMCASE_CACHE={}):
    try:
        return NORMCASE_CACHE[s]
    except:
        normalized = NORMCASE_CACHE[s] = s.lower()
        return normalized


IS_PYPY = platform.python_implementation() == "PyPy"
IS_WINDOWS = sys.platform == "win32"
IS_LINUX = sys.platform in ("linux", "linux2")
IS_MAC = sys.platform == "darwin"

LIBRARY_CODE_BASENAMES_STARTING_WITH = ("<",)


def _convert_to_str_and_clear_empty(roots):
    new_roots = []
    for root in roots:
        assert isinstance(root, str), "%s not str (found: %s)" % (root, type(root))
        if root:
            new_roots.append(root)
    return new_roots


class FilesFiltering(object):
    """
    Usage is something as:

    files_filtering = FilesFiltering(...)

    # Detects if a given file is user-code.
    files_filtering.in_project_roots(mod.__file__)
    """

    def __init__(
        self,
        project_roots: Optional[Sequence[str]] = None,
        library_roots: Optional[Sequence[str]] = None,
    ):
        self._project_roots: List[str] = []
        self._library_roots: List[str] = []
        self._cache_in_project_roots: Dict[str, bool] = {}

        if project_roots is None:
            # If the ROBOT_ROOT is available, use it to signal it's
            # user code beneath that folder.
            robot_root = os.environ.get("ROBOT_ROOT")
            if robot_root:
                if os.path.isdir(robot_root):
                    project_roots = [robot_root]

        if project_roots is not None:
            self._set_project_roots(project_roots)

        if library_roots is None:
            library_roots = self._get_default_library_roots()
        self._set_library_roots(library_roots)

    @classmethod
    def _get_default_library_roots(cls):
        log.debug("Collecting default library roots.")
        # Provide sensible defaults if not in env vars.
        import site

        roots = []

        try:
            import sysconfig  # Python 2.7 onwards only.
        except ImportError:
            pass
        else:
            for path_name in set(("stdlib", "platstdlib", "purelib", "platlib")) & set(
                sysconfig.get_path_names()
            ):
                roots.append(sysconfig.get_path(path_name))

        # Make sure we always get at least the standard library location (based on the `os` and
        # `threading` modules -- it's a bit weird that it may be different on the ci, but it happens).
        roots.append(os.path.dirname(os.__file__))
        roots.append(os.path.dirname(threading.__file__))
        if IS_PYPY:
            # On PyPy 3.6 (7.3.1) it wrongly says that sysconfig.get_path('stdlib') is
            # <install>/lib-pypy when the installed version is <install>/lib_pypy.
            try:
                import _pypy_wait  # type: ignore
            except ImportError:
                log.debug(
                    "Unable to import _pypy_wait on PyPy when collecting default library roots."
                )
            else:
                pypy_lib_dir = os.path.dirname(_pypy_wait.__file__)
                log.debug("Adding %s to default library roots.", pypy_lib_dir)
                roots.append(pypy_lib_dir)

        if hasattr(site, "getusersitepackages"):
            site_paths = site.getusersitepackages()
            if isinstance(site_paths, (list, tuple)):
                for site_path in site_paths:
                    roots.append(site_path)
            else:
                roots.append(site_paths)

        if hasattr(site, "getsitepackages"):
            site_paths = site.getsitepackages()
            if isinstance(site_paths, (list, tuple)):
                for site_path in site_paths:
                    roots.append(site_path)
            else:
                roots.append(site_paths)

        for path in sys.path:
            if os.path.exists(path) and os.path.basename(path) in (
                "site-packages",
                "pip-global",
            ):
                roots.append(path)

        roots.extend([os.path.realpath(path) for path in roots])

        return sorted(set(roots))

    def _fix_roots(self, roots):
        roots = _convert_to_str_and_clear_empty(roots)
        new_roots = []
        for root in roots:
            path = self._absolute_normalized_path(root)
            if IS_WINDOWS:
                new_roots.append(path + "\\")
            else:
                new_roots.append(path + "/")
        return new_roots

    def _absolute_normalized_path(self, filename, cache={}):
        """
        Provides a version of the filename that's absolute and normalized.
        """
        try:
            return cache[filename]
        except KeyError:
            pass

        if filename.startswith("<"):
            cache[filename] = normcase(filename)
            return cache[filename]

        cache[filename] = normcase(os.path.abspath(filename))
        return cache[filename]

    def _set_project_roots(self, project_roots):
        self._project_roots = self._fix_roots(project_roots)
        log.debug("ROBOT_ROOTS %s\n" % project_roots)

    def _get_project_roots(self):
        return self._project_roots

    def _set_library_roots(self, roots):
        self._library_roots = self._fix_roots(roots)
        log.debug("LIBRARY_ROOTS %s\n" % roots)

    def _get_library_roots(self):
        return self._library_roots

    def _in_project_roots(self, received_filename: str) -> bool:
        """
        Note: uncached. Use `in_project_roots`.
        """
        DEBUG = False

        if received_filename.startswith(LIBRARY_CODE_BASENAMES_STARTING_WITH):
            if DEBUG:
                log.debug(
                    "Not in in_project_roots - library basenames - starts with %s (%s)",
                    received_filename,
                    LIBRARY_CODE_BASENAMES_STARTING_WITH,
                )
            return False

        project_roots = self._get_project_roots()  # roots are absolute/normalized.

        absolute_normalized_filename = self._absolute_normalized_path(received_filename)
        absolute_normalized_filename_as_dir = absolute_normalized_filename + (
            "\\" if IS_WINDOWS else "/"
        )

        found_in_project = []
        for root in project_roots:
            if root and (
                absolute_normalized_filename.startswith(root)
                or root == absolute_normalized_filename_as_dir
            ):
                if DEBUG:
                    log.debug("In project: %s (%s)", absolute_normalized_filename, root)
                found_in_project.append(root)

        found_in_library = []
        library_roots = self._get_library_roots()
        for root in library_roots:
            if root and (
                absolute_normalized_filename.startswith(root)
                or root == absolute_normalized_filename_as_dir
            ):
                found_in_library.append(root)
                if DEBUG:
                    log.debug("In library: %s (%s)", absolute_normalized_filename, root)
            else:
                if DEBUG:
                    log.debug(
                        "Not in library: %s (%s)", absolute_normalized_filename, root
                    )

        if not project_roots:
            # If we have no project roots configured, consider it being in the project
            # roots if it's not found in site-packages (because we have defaults for those
            # and not the other way around).
            in_project = not found_in_library
            if DEBUG:
                log.debug(
                    "Final in project (no project roots): %s (%s)",
                    absolute_normalized_filename,
                    in_project,
                )

        else:
            in_project = False
            if found_in_project:
                if not found_in_library:
                    if DEBUG:
                        log.debug(
                            "Final in project (in_project and not found_in_library): %s (True)",
                            absolute_normalized_filename,
                        )
                    in_project = True
                else:
                    # Found in both, let's see which one has the bigger path matched.
                    if max(len(x) for x in found_in_project) > max(
                        len(x) for x in found_in_library
                    ):
                        in_project = True
                    if DEBUG:
                        log.debug(
                            "Final in project (found in both): %s (%s)",
                            absolute_normalized_filename,
                            in_project,
                        )

        return in_project

    def in_project_roots(self, filename: str) -> bool:
        try:
            return self._cache_in_project_roots[filename]
        except KeyError:
            pass

        in_project_roots = self._in_project_roots(filename)
        self._cache_in_project_roots[filename] = in_project_roots
        return in_project_roots
