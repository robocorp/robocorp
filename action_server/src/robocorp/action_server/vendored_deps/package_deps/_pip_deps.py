from dataclasses import dataclass
from typing import Any, Iterator, List, Optional, Tuple

from ._deps_protocols import _RangeTypedDict


@dataclass
class PipDepInfo:
    name: str  # rpaframework
    extras: Any
    constraints: Optional[List[Tuple[str, str]]]  # i.e.: [('==', '22.5.3')]
    marker: Any
    url: str
    requirement: str  #'rpaframework == 22.5.3'
    dep_range: _RangeTypedDict
    error_msg: Optional[str]  # Error if we couldn't parse it.


class PipDeps:
    """
    pip references:
        pip._vendor.distlib.version.Matcher
        pip._vendor.distlib.util.parse_requirement
    """

    def __init__(self):
        self._pip_versions = {}

    def add_dep(self, value, as_range):
        from .pip_impl.pip_distlib_util import IDENTIFIER, parse_requirement

        try:
            req = parse_requirement(value)
        except Exception as e:
            remaining = value.strip()
            # -- ignored because it's used for pip flags (i.e.: --use-feature=trustore).
            if not remaining or remaining.startswith("#") or remaining.startswith("--"):
                return

            if value.startswith(("git+http", "http")) or value.endswith(
                (".whl", ".zip", "bz2", "gz")
            ):
                self._pip_versions[value] = PipDepInfo(
                    name=value,
                    extras=None,
                    constraints=None,
                    marker=None,
                    url="",
                    requirement=value,
                    dep_range=as_range,
                    error_msg=None,
                )
                return

            m = IDENTIFIER.match(remaining)
            if not m:
                name = "<unknown>"
            else:
                name = m.groups()[0]

            self._pip_versions[name] = PipDepInfo(
                name=name,
                extras=None,
                constraints=None,
                marker=None,
                url="",
                requirement=value,
                dep_range=as_range,
                error_msg=f"Error parsing '{value}': {e}",
            )
        else:
            self._pip_versions[req.name] = PipDepInfo(
                **req.__dict__, error_msg=None, dep_range=as_range
            )

    def iter_pip_dep_infos(self) -> Iterator[PipDepInfo]:
        yield from self._pip_versions.values()
