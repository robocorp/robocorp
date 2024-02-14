"""
This package should be independent of the rest as we can potentially make
it a standalone package in the future (maybe with a command line UI).
"""

import pathlib
from typing import Any, Iterator, List, Optional, Tuple

import yaml

from ._conda_deps import CondaDepInfo
from ._deps_protocols import (
    ICondaCloud,
    IPyPiCloud,
    _DiagnosticSeverity,
    _DiagnosticsTypedDict,
    _RangeTypedDict,
)
from ._pip_deps import PipDepInfo
from .conda_impl.conda_version import VersionSpec
from .pypi_cloud import PyPiCloud


class ScalarInfo:
    def __init__(self, scalar: Any, location: Optional[Tuple[int, int, int, int]]):
        """
        Args:
            scalar:
            location: tuple(start_line, start_col, end_line, end_col)
        """
        self.scalar = scalar
        self.location = location

    def __repr__(self):
        return repr(self.scalar)

    def __str__(self):
        return str(self.scalar)

    def __eq__(self, o):
        if isinstance(o, ScalarInfo):
            return self.scalar == o.scalar

        return False

    def __ne__(self, o):
        return not self == o

    def __hash__(self):
        return hash(self.scalar)

    def as_range(self) -> _RangeTypedDict:
        assert self.location
        start_line, start_col, end_line, end_col = self.location
        return create_range_from_location(start_line, start_col, end_line, end_col)


def create_range_from_location(
    start_line: int,
    start_col: int,
    end_line: Optional[int] = None,
    end_col: Optional[int] = None,
) -> _RangeTypedDict:
    """
    If the end_line and end_col aren't passed we consider
    that the location should go up until the end of the line.
    """
    if end_line is None:
        assert end_col is None
        end_line = start_line + 1
        end_col = 0
    assert end_col is not None
    dct: _RangeTypedDict = {
        "start": {
            "line": start_line,
            "character": start_col,
        },
        "end": {
            "line": end_line,
            "character": end_col,
        },
    }
    return dct


class LoaderWithLines(yaml.SafeLoader):
    def construct_scalar(self, node, *args, **kwargs):
        scalar = yaml.SafeLoader.construct_scalar(self, node, *args, **kwargs)
        return ScalarInfo(
            scalar=scalar,
            location=(
                node.start_mark.line,
                node.start_mark.column,
                node.end_mark.line,
                node.end_mark.column,
            ),
        )


class Analyzer:
    _pypi_cloud: IPyPiCloud
    _conda_cloud: ICondaCloud

    def __init__(
        self,
        contents: str,
        path: str,
        conda_cloud: ICondaCloud,
        pypi_cloud: Optional[IPyPiCloud] = None,
    ):
        """
        Args:
            contents: The contents of the conda.yaml/action-server.yaml.
            path: The path for the conda yaml.
        """
        from ._conda_deps import CondaDeps
        from ._pip_deps import PipDeps

        self.contents = contents
        self.path = path

        self._loaded_conda_yaml = False
        self._load_errors: List[_DiagnosticsTypedDict] = []
        self._conda_data: Optional[dict] = None

        self._pip_deps = PipDeps()
        self._conda_deps = CondaDeps()
        if pypi_cloud is None:
            self._pypi_cloud = PyPiCloud()
        else:
            self._pypi_cloud = pypi_cloud

        self._conda_cloud = conda_cloud

    def load_conda_yaml(self) -> None:
        if self._loaded_conda_yaml:
            return
        self._loaded_conda_yaml = True

        from yaml.parser import ParserError

        diagnostic: _DiagnosticsTypedDict

        try:
            loader = LoaderWithLines(self.contents)
            path: pathlib.Path = pathlib.Path(self.path)

            loader.name = f".../{path.parent.name}/{path.name}"
            data = loader.get_single_data()
            self._conda_data = data
        except ParserError as e:
            if e.problem_mark:
                diagnostic = {
                    "range": create_range_from_location(
                        e.problem_mark.line, e.problem_mark.column
                    ),
                    "severity": _DiagnosticSeverity.Error,
                    "source": "robocorp-code",
                    "message": f"Syntax error: {e}",
                }
                self._load_errors.append(diagnostic)
            return

        dependencies = data.get(
            ScalarInfo(
                "dependencies",
                None,
            ),
        )

        conda_versions = self._conda_deps
        pip_versions = self._pip_deps
        if dependencies:
            for dep in dependencies:
                # At this level we're seeing conda versions. The spec is:
                # https://docs.conda.io/projects/conda-build/en/latest/resources/package-spec.html#package-match-specifications
                # A bunch of code from conda was copied to handle that so that we
                # can just `conda_match_spec.parse_spec_str` to identify the version
                # we're dealing with.
                if isinstance(dep, ScalarInfo) and isinstance(dep.scalar, str):
                    conda_versions.add_dep(dep.scalar, dep.as_range())
                elif isinstance(dep, dict):
                    pip_deps = dep.get(ScalarInfo("pip", None))
                    if pip_deps:
                        for dep in pip_deps:
                            if isinstance(dep, ScalarInfo) and isinstance(
                                dep.scalar, str
                            ):
                                pip_versions.add_dep(dep.scalar, dep.as_range())

    def iter_issues(self) -> Iterator[_DiagnosticsTypedDict]:
        self.load_conda_yaml()
        if self._load_errors:
            yield from iter(self._load_errors)
            return

        data = self._conda_data
        if not data:
            return

        yield from self.iter_conda_issues()
        yield from self.iter_pip_issues()

    def iter_pip_issues(self):
        from .pip_impl import pip_packaging_version

        for dep_info in self._pip_deps.iter_pip_dep_infos():
            if dep_info.error_msg:
                diagnostic = {
                    "range": dep_info.dep_range,
                    "severity": _DiagnosticSeverity.Error,
                    "source": "robocorp-code",
                    "message": dep_info.error_msg,
                }

                yield diagnostic

                continue

            if dep_info.constraints and len(dep_info.constraints) == 1:
                # For now just checking versions '=='.
                constraint = next(iter(dep_info.constraints))
                if constraint[0] == "==":
                    local_version = constraint[1]
                    newer_cloud_versions = self._pypi_cloud.get_versions_newer_than(
                        dep_info.name, pip_packaging_version.parse(local_version)
                    )
                    if newer_cloud_versions:
                        latest_cloud_version = newer_cloud_versions[-1]
                        diagnostic = {
                            "range": dep_info.dep_range,
                            "severity": _DiagnosticSeverity.Warning,
                            "source": "robocorp-code",
                            "message": f"Consider updating '{dep_info.name}' to the latest version: '{latest_cloud_version}'. "
                            + f"Found {len(newer_cloud_versions)} versions newer than the current one: {', '.join(newer_cloud_versions)}.",
                        }

                        yield diagnostic

    def iter_conda_issues(self) -> Iterator[_DiagnosticsTypedDict]:
        from .conda_cloud import sort_conda_versions

        diagnostic: _DiagnosticsTypedDict
        dep_vspec = self._conda_deps.get_dep_vspec("python")

        # See: https://devguide.python.org/versions/

        if dep_vspec is not None:
            # We have the dep spec, not the actual version
            # (so, it could be something as >3.3 <4)
            # So, if an old version may be gotten from that spec, we warn about it.
            vspec = VersionSpec(dep_vspec)
            for old_version in "2 3.1 3.2 3.3 3.4 3.5 3.6 3.7".split(" "):
                if vspec.match(old_version):
                    dep_range = self._conda_deps.get_dep_range("python")

                    diagnostic = {
                        "range": dep_range,
                        "severity": _DiagnosticSeverity.Warning,
                        "source": "robocorp-code",
                        "message": "The official support for versions lower than Python 3.8 has ended. "
                        + " It is advisable to transition to a newer version "
                        + "(Python 3.9 or newer is recommended).",
                    }

                    yield diagnostic
                    break

        dep_vspec = self._conda_deps.get_dep_vspec("pip")

        if dep_vspec is not None:
            vspec = VersionSpec(dep_vspec)
            # pip should be 22 or newer, so, check if an older version matches.
            for old_version in (str(x) for x in range(1, 22)):
                if vspec.match(old_version):
                    dep_range = self._conda_deps.get_dep_range("pip")

                    diagnostic = {
                        "range": dep_range,
                        "severity": _DiagnosticSeverity.Warning,
                        "source": "robocorp-code",
                        "message": "Consider updating pip to a newer version (at least pip 22 onwards is recommended).",
                    }

                    yield diagnostic
                    break

        sqlite_queries = self._conda_cloud.sqlite_queries()
        if sqlite_queries:
            with sqlite_queries.db_cursors() as db_cursors:
                for conda_dep in self._conda_deps.iter_conda_dep_infos():
                    if conda_dep.name in ("python", "pip"):
                        continue

                    version_spec = conda_dep.get_dep_vspec()
                    if version_spec is None:
                        continue

                    versions = sqlite_queries.query_versions(conda_dep.name, db_cursors)
                    if not versions:
                        continue

                    sorted_versions = sort_conda_versions(versions)
                    last_version = sorted_versions[-1]
                    if not version_spec.match(last_version):
                        # The latest version doesn't match, let's show a warning.
                        newer_cloud_versions = []
                        for v in reversed(sorted_versions):
                            if not version_spec.match(v):
                                newer_cloud_versions.append(v)
                            else:
                                break

                        diagnostic = {
                            "range": conda_dep.dep_range,
                            "severity": _DiagnosticSeverity.Warning,
                            "source": "robocorp-code",
                            "message": f"Consider updating '{conda_dep.name}' to match the latest version: '{last_version}'. "
                            + f"Found {len(newer_cloud_versions)} versions that don't match the version specification: {', '.join(newer_cloud_versions)}.",
                        }

                        yield diagnostic

    def find_pip_dep_at(self, line, col) -> Optional[PipDepInfo]:
        self.load_conda_yaml()
        for dep_info in self._pip_deps.iter_pip_dep_infos():
            if is_inside(dep_info.dep_range, line, col):
                return dep_info
        return None

    def find_conda_dep_at(self, line, col) -> Optional[CondaDepInfo]:
        self.load_conda_yaml()
        for dep_info in self._conda_deps.iter_conda_dep_infos():
            if is_inside(dep_info.dep_range, line, col):
                return dep_info
        return None


class _Position:
    def __init__(self, line: int = 0, character: int = 0):
        self.line: int = line
        self.character: int = character

    def __repr__(self):
        import json

        return json.dumps(self.to_dict(), indent=4)

    def __getitem__(self, name):
        # provide tuple-access, not just dict access.
        if name == 0:
            return self.line
        if name == 1:
            return self.character
        return getattr(self, name)

    def __eq__(self, other):
        return (
            isinstance(other, _Position)
            and self.line == other.line
            and self.character == other.character
        )

    def __ge__(self, other):
        line_gt = self.line > other.line

        if line_gt:
            return line_gt

        if self.line == other.line:
            return self.character >= other.character

        return False

    def __gt__(self, other):
        line_gt = self.line > other.line

        if line_gt:
            return line_gt

        if self.line == other.line:
            return self.character > other.character

        return False

    def __le__(self, other):
        line_lt = self.line < other.line

        if line_lt:
            return line_lt

        if self.line == other.line:
            return self.character <= other.character

        return False

    def __lt__(self, other):
        line_lt = self.line < other.line

        if line_lt:
            return line_lt

        if self.line == other.line:
            return self.character < other.character

        return False

    def __ne__(self, other):
        return not self.__eq__(other)


def is_inside(range_dct: _RangeTypedDict, line: int, col: int) -> bool:
    start = range_dct["start"]
    end = range_dct["end"]
    start_pos = _Position(start["line"], start["character"])
    end_pos = _Position(end["line"], end["character"])
    curr_pos = _Position(line, col)
    return start_pos <= curr_pos <= end_pos
