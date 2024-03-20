from dataclasses import dataclass
from typing import Dict, Iterator, Optional

from ._deps_protocols import _RangeTypedDict
from .conda_impl import conda_match_spec, conda_version


@dataclass
class CondaDepInfo:
    name: str  # The name of the dep (i.e.: python)
    value: str  # The full value of the dep (i.e.: python=3.7)
    version_spec: str  # The version SPEC of the dep (as seen by conda: '3.7.*' or '>3.2')
    dep_range: _RangeTypedDict
    error_msg: Optional[str] = None

    def get_dep_vspec(self) -> Optional[conda_version.VersionSpec]:
        try:
            vspec = conda_version.VersionSpec(self.version_spec)
        except Exception:
            return None
        return vspec


class CondaDeps:
    def __init__(self) -> None:
        self._deps: Dict[str, CondaDepInfo] = {}

    def add_dep(self, value: str, dep_range: _RangeTypedDict):
        """
        Args:
            value: This is the value found in the spec. Something as:
            'python==3.7'.
        """
        try:
            spec = conda_match_spec.parse_spec_str(value)

            # It may not have a version if it wasn't specified.
            version_spec = spec.get("version", "*")
            name = spec["name"]
        except Exception:
            pass
        else:
            self._deps[name] = CondaDepInfo(name, value, version_spec, dep_range)

    def get_dep_vspec(self, spec_name: str) -> Optional[conda_version.VersionSpec]:
        conda_dep_info = self._deps.get(spec_name)
        if conda_dep_info is None:
            return None
        return conda_dep_info.get_dep_vspec()

    def get_dep_range(self, spec_name: str) -> _RangeTypedDict:
        return self._deps[spec_name].dep_range

    def iter_deps_infos(self) -> Iterator[CondaDepInfo]:
        yield from self._deps.values()
