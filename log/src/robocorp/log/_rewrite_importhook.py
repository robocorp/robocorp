"""
Rewrite assertion AST to generate the logging we'd like.

Based on code from pytest:
https://github.com/pytest-dev/pytest/blob/main/src/_pytest/assertion/rewrite.py

Original work Copyright (c) 2004 Holger Krekel and others (MIT)
All modifications Copyright (c) Robocorp Technologies Inc.
All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License")
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http: // www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import ast
import errno
import importlib.abc
import importlib.machinery
import importlib.util
import marshal
import os
import struct
import sys
import types
from pathlib import Path
from typing import IO, Callable, Dict, Optional, Sequence, Tuple, Union

from ._config import BaseConfig, FilterKind

# caches rewritten pycs in pycache dirs
# 0.0.1: Initial version
# 0.0.2: Bugfix: docstrings must be kept as the first statement
# 0.0.3: Support for exception handlers
# 0.0.4: Add __name__
# 0.0.5: Renames of internal modules.
# 0.0.6: Option to log just 1 level deep into library modules.
# 0.0.7: Just include __name__, note __package__.
# 0.0.9: Rewrite assign statements
# 0.0.10: Rewrite yields
# 0.0.11: Add method type as first parameter for start_method/except/end_method
# 0.0.12: Changed to use robocorp namespace.
# 0.0.13: Changed to use robocorp.log name.
# 0.0.14: Rewrite yield from
# 0.0.15: Rewrite for
# 0.0.16: Rewrite for without try..except
# 0.0.17: Rewrite while
# 0.0.18: Fixes in generation based on scoping (generator/untracked_generator,full_log,log_on_project_call).
version = "0.0.18"
NAME_WITH_TAG = f"{sys.implementation.cache_tag}-log-{version}"
PYC_EXT = ".py" + (__debug__ and "c" or "o")
PYC_TAIL = "." + NAME_WITH_TAG + PYC_EXT

FORCE_CODE_GENERATION = False
DEBUG = False


if DEBUG:

    def trace(msg):
        print(msg)

else:

    def trace(msg):
        pass


class RewriteHook(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """PEP302/PEP451 import hook which rewrites asserts."""

    def __init__(self, config: BaseConfig) -> None:
        self.config = config
        self._rewritten_names: Dict[str, Path] = {}
        # flag to guard against trying to rewrite a pyc file while we are already writing another pyc file,
        # which might result in infinite recursion (#3506)
        self._writing_pyc = False

    # Indirection so we can mock calls to find_spec originated from the hook during testing
    _find_spec = importlib.machinery.PathFinder.find_spec

    def find_spec(
        self,
        name: str,
        path: Optional[Sequence[Union[str, bytes]]] = None,
        target: Optional[types.ModuleType] = None,
    ) -> Optional[importlib.machinery.ModuleSpec]:
        if self._writing_pyc:
            return None

        filter_kind: Optional[FilterKind] = self.config.get_filter_kind_by_module_name(
            name
        )
        if filter_kind is not None:
            # Try to bail out as early as possible as the slow part is the "_find_spec".
            if filter_kind == FilterKind.exclude:
                return None

        trace("find_module called for: %s" % name)

        # Type ignored because mypy is confused about the `self` binding here.
        spec = self._find_spec(name, path)  # type: ignore
        if (
            # the import machinery could not find a file to import
            spec is None
            # this is a namespace package (without `__init__.py`)
            # there's nothing to rewrite there
            or spec.origin is None
            # we can only rewrite source files
            or not isinstance(spec.loader, importlib.machinery.SourceFileLoader)
            # if the file doesn't exist, we can't rewrite it
            or not os.path.exists(spec.origin)
        ):
            return None
        else:
            fn = spec.origin

        if filter_kind is None:
            filter_kind = self.config.get_filter_kind_by_module_name_and_path(name, fn)
            if filter_kind == FilterKind.exclude:
                return None

        return importlib.util.spec_from_file_location(
            name,
            fn,
            loader=self,
            submodule_search_locations=spec.submodule_search_locations,
        )

    def create_module(
        self, spec: importlib.machinery.ModuleSpec
    ) -> Optional[types.ModuleType]:
        return None  # default behavior is fine

    def exec_module(self, module: types.ModuleType) -> None:
        assert module.__spec__ is not None
        assert module.__spec__.origin is not None
        fn = Path(module.__spec__.origin)

        self._rewritten_names[module.__name__] = fn

        # The requested module looks like a test file, so rewrite it. This is
        # the most magical part of the process: load the source, rewrite the
        # asserts, and load the rewritten source. We also cache the rewritten
        # module code in a special pyc. We must be aware of the possibility of
        # concurrent pytest processes rewriting and loading pycs. To avoid
        # tricky race conditions, we maintain the following invariant: The
        # cached pyc is always a complete, valid pyc. Operations on it must be
        # atomic. POSIX's atomic rename comes in handy.
        write = not sys.dont_write_bytecode
        cache_dir = get_cache_dir(fn)
        if write:
            ok = try_makedirs(cache_dir)
            if not ok:
                write = False
                trace(f"read only directory: {cache_dir}")

        filter_kind: FilterKind = self.config.get_filter_kind_by_module_name_and_path(
            module.__name__, module.__spec__.origin
        )

        cache_name = fn.name[:-3] + filter_kind.value + PYC_TAIL

        pyc = cache_dir / cache_name
        # Notice that even if we're in a read-only directory, I'm going
        # to check for a cached pyc. This may not be optimal...
        if FORCE_CODE_GENERATION:
            co = None
        else:
            co = _read_pyc(fn, pyc, trace)
        if co is None:
            trace(f"rewriting {fn!r}")
            source_stat, co, _tree = _rewrite(fn, self.config, filter_kind)
            if write:
                self._writing_pyc = True
                try:
                    _write_pyc(co, source_stat, pyc)
                finally:
                    self._writing_pyc = False
        else:
            trace(f"found cached rewritten pyc for {fn}")
        exec(co, module.__dict__)

    def get_data(self, pathname: Union[str, bytes]) -> bytes:
        """Optional PEP302 get_data API."""
        with open(pathname, "rb") as f:
            return f.read()

    if sys.version_info >= (3, 10):
        if sys.version_info >= (3, 12):
            from importlib.resources.abc import TraversableResources
        else:
            from importlib.abc import TraversableResources

        def get_resource_reader(self, name: str) -> TraversableResources:  # type: ignore
            if sys.version_info < (3, 11):
                from importlib.readers import FileReader
            else:
                from importlib.resources.readers import FileReader

            return FileReader(  # type:ignore[no-any-return]
                types.SimpleNamespace(path=self._rewritten_names[name])
            )


def _write_pyc_fp(
    fp: IO[bytes], source_stat: os.stat_result, co: types.CodeType
) -> None:
    # Technically, we don't have to have the same pyc format as
    # (C)Python, since these "pycs" should never be seen by builtin
    # import. However, there's little reason to deviate.
    fp.write(importlib.util.MAGIC_NUMBER)
    # https://www.python.org/dev/peps/pep-0552/
    flags = b"\x00\x00\x00\x00"
    fp.write(flags)
    # as of now, bytecode header expects 32-bit numbers for size and mtime (#4903)
    mtime = int(source_stat.st_mtime) & 0xFFFFFFFF
    size = source_stat.st_size & 0xFFFFFFFF
    # "<LL" stands for 2 unsigned longs, little-endian.
    fp.write(struct.pack("<LL", mtime, size))
    fp.write(marshal.dumps(co))


def _write_pyc(
    co: types.CodeType,
    source_stat: os.stat_result,
    pyc: Path,
) -> bool:
    proc_pyc = f"{pyc}.{os.getpid()}"
    try:
        with open(proc_pyc, "wb") as fp:
            _write_pyc_fp(fp, source_stat, co)
    except OSError as e:
        trace(f"error writing pyc file at {proc_pyc}: errno={e.errno}")
        return False

    try:
        os.replace(proc_pyc, pyc)
    except OSError as e:
        trace(f"error writing pyc file at {pyc}: {e}")
        # we ignore any failure to write the cache file
        # there are many reasons, permission-denied, pycache dir being a
        # file etc.
        return False
    return True


def _rewrite(
    fn: Path, config: BaseConfig, filter_kind: FilterKind
) -> Tuple[os.stat_result, types.CodeType, ast.AST]:
    """Read and rewrite *fn* and return the code object."""
    from ._rewrite_ast_add_callbacks import rewrite_ast_add_callbacks

    stat = os.stat(fn)
    source = fn.read_bytes()
    strfn = str(fn)
    tree = ast.parse(source, filename=strfn)
    rewrite_ast_add_callbacks(tree, filter_kind, source, strfn, config)
    if DEBUG:
        print(f"Changed {strfn} to:")
        print(ast.unparse(tree))
    co = compile(tree, strfn, "exec", dont_inherit=True)
    return stat, co, tree


def _read_pyc(
    source: Path, pyc: Path, trace: Callable[[str], None] = lambda x: None
) -> Optional[types.CodeType]:
    """Possibly read a pytest pyc containing rewritten code.

    Return rewritten code if successful or None if not.
    """
    try:
        fp = open(pyc, "rb")
    except OSError:
        return None
    with fp:
        try:
            stat_result = os.stat(source)
            mtime = int(stat_result.st_mtime)
            size = stat_result.st_size
            data = fp.read(16)
        except OSError as e:
            trace(f"_read_pyc({source}): OSError {e}")
            return None
        # Check for invalid or out of date pyc file.
        if len(data) != (16):
            trace("_read_pyc(%s): invalid pyc (too short)" % source)
            return None
        if data[:4] != importlib.util.MAGIC_NUMBER:
            trace("_read_pyc(%s): invalid pyc (bad magic number)" % source)
            return None
        if data[4:8] != b"\x00\x00\x00\x00":
            trace("_read_pyc(%s): invalid pyc (unsupported flags)" % source)
            return None
        mtime_data = data[8:12]
        if int.from_bytes(mtime_data, "little") != mtime & 0xFFFFFFFF:
            trace("_read_pyc(%s): out of date" % source)
            return None
        size_data = data[12:16]
        if int.from_bytes(size_data, "little") != size & 0xFFFFFFFF:
            trace("_read_pyc(%s): invalid pyc (incorrect size)" % source)
            return None
        try:
            co = marshal.load(fp)
        except Exception as e:
            trace(f"_read_pyc({source}): marshal.load error {e}")
            return None
        if not isinstance(co, types.CodeType):
            trace("_read_pyc(%s): not a code object" % source)
            return None
        return co


def try_makedirs(cache_dir: Path) -> bool:
    """Attempt to create the given directory and sub-directories exist.

    Returns True if successful or if it already exists.
    """
    try:
        os.makedirs(cache_dir, exist_ok=True)
    except (FileNotFoundError, NotADirectoryError, FileExistsError):
        # One of the path components was not a directory:
        # - we're in a zip file
        # - it is a file
        return False
    except PermissionError:
        return False
    except OSError as e:
        # as of now, EROFS doesn't have an equivalent OSError-subclass
        if e.errno == errno.EROFS:
            return False
        raise
    return True


def get_cache_dir(file_path: Path) -> Path:
    """Return the cache directory to write .pyc files for the given .py file path."""
    if sys.version_info >= (3, 8) and sys.pycache_prefix:
        # given:
        #   prefix = '/tmp/pycs'
        #   path = '/home/user/proj/test_app.py'
        # we want:
        #   '/tmp/pycs/home/user/proj'
        return Path(sys.pycache_prefix) / Path(*file_path.parts[1:-1])
    else:
        # classic pycache directory
        return file_path.parent / "__pycache__"
