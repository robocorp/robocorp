from ._conda_deps import CondaDeps
from ._pip_deps import PipDeps


class PackageDepsConda(CondaDeps):
    def add_dep(self, value: str, as_range):
        from ..action_package_handling import convert_conda_entry
        from ._conda_deps import CondaDepInfo

        try:
            _name, entry_in_conda, _op, _version = convert_conda_entry(None, value)
        except Exception as e:
            self._deps[value] = CondaDepInfo(
                value, value, "", as_range, error_msg=f"Error parsing '{value}': {e}"
            )

        else:
            CondaDeps.add_dep(self, entry_in_conda, as_range)


class PackageDepsPip(PipDeps):
    """
    Handles the format of versions supported by package.yaml.
    """

    def add_dep(self, value: str, as_range):
        from ..action_package_handling import convert_pip_entry
        from ._pip_deps import PipDepInfo

        try:
            _name, entry_in_pip, _op, _version = convert_pip_entry(None, value)
        except Exception as e:
            self._deps[value] = PipDepInfo(
                name=value,
                extras=None,
                constraints=None,
                marker=None,
                url="",
                requirement=value,
                dep_range=as_range,
                error_msg=f"Error parsing '{value}': {e}",
            )

        else:
            PipDeps.add_dep(self, entry_in_pip, as_range)
