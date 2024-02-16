import logging
import os
import sys
import typing
from pathlib import Path
from typing import List, Optional, Tuple

from .cli_errors import ActionPackageError

log = logging.getLogger(__name__)


def _verify_name(package_yaml: Path, name: str) -> None:
    # Could be used to verify that something is not declared (no-op for now).
    pass


_version_chars_without_eq = (">", "<", "^", "~", "!", ",", ";")


def _interpret_entry(package_yaml: Path, entry: str) -> Tuple[str, str, str]:
    # https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers
    # https://packaging.python.org/en/latest/specifications/version-specifiers/#compatible-release
    for c in _version_chars_without_eq:
        if c in entry:
            raise ActionPackageError(
                f"Error in entry: {entry}. Using: {c!r} is not currently supported (in {package_yaml})."
            )

    i = entry.find("=")
    if i == -1:
        # No version specified.
        name = entry
        _verify_name(package_yaml, name)
        return name, "", ""

    name, version = entry[:i], entry[i + 1 :]
    if "=" in version:
        raise ActionPackageError(
            f"Error in entry: {entry}. Only a single '=' should be used (in {package_yaml})."
        )
    _verify_name(package_yaml, name)
    return name, "=", version


def convert_conda_entry(package_yaml: Path, entry: str) -> Tuple[str, str]:
    name, op, version = _interpret_entry(package_yaml, entry)

    if op:
        if op == "=":
            return name, f"{name}={version}"
        raise ActionPackageError(
            f"Error in entry: {entry}. {op!r} not supported (in {package_yaml})."
        )

    assert not version
    return name, name


def convert_pip_entry(package_yaml: Path, entry: str) -> Tuple[str, str]:
    name, op, version = _interpret_entry(package_yaml, entry)
    if op:
        if op == "=":
            return name, f"{name}=={version}"
        raise ActionPackageError(
            f"Error in entry: {entry}. {op!r} not supported (in {package_yaml})."
        )

    assert not version
    return name, name


def _create_package_from_conda_yaml(
    conda_yaml: Path, dry_run: bool, backup: bool, *, stream: Optional[typing.IO] = None
):
    import yaml

    from ..package_deps.conda_impl import conda_match_spec
    from ..package_deps.pip_impl.pip_distlib_util import parse_requirement
    from ..termcolors import bold_yellow

    with conda_yaml.open("r", encoding="utf-8") as s:
        contents = yaml.safe_load(s)

    dependencies = contents.get("dependencies")
    pip_deps: List[str] = []
    conda_deps: List[str] = []
    if isinstance(dependencies, list):
        for dep in dependencies:
            if isinstance(dep, dict):
                if tuple(dep.keys()) != ("pip",):
                    raise ActionPackageError(
                        f'Unable to convert to package.yaml: Keys of dependency dict is not just "pip" dependency. Found: {dep}.'
                    )

                for pip_dep in dep["pip"]:
                    if not isinstance(pip_dep, str):
                        raise ActionPackageError(
                            f"Unable to convert to package.yaml: Expected pip dep to be str. Found: {pip_dep} ({type(pip_dep)})."
                        )
                    pip_deps.append(pip_dep)

                continue

            if not isinstance(dep, str):
                raise ActionPackageError(
                    f"Unable to convert to package.yaml: Expected dep to be str. Found: {dep} ({type(dep)})."
                )

            conda_deps.append(dep)

    # Ok, at this point we should have the deps. Let's put them in the new format.
    new_pip_deps = []
    for dep in pip_deps:
        try:
            parsed = parse_requirement(dep)
            if parsed is None:
                continue

            for op, version in parsed.constraints:
                if op != "==":
                    print(
                        bold_yellow(
                            f"Found constraint: {op!r} for {parsed.name}. It'll be converted to '='"
                        ),
                        file=stream,
                    )
                new_pip_deps.append(f"{parsed.name}={version}")
                break

            for op, version in parsed.constraints[1:]:
                print(
                    bold_yellow(f"Ignoring constraint: {op!r} for {parsed.name}."),
                    file=stream,
                )

        except Exception:
            raise ActionPackageError(f"Unable to parse pip dep: {dep}.")

    new_conda_deps = []
    all_version_chars = _version_chars_without_eq + ("=",)
    for dep in conda_deps:
        try:
            spec = conda_match_spec.parse_spec_str(dep)

            # It may not have a version if it wasn't specified.
            version_spec = spec.get("version", "*").strip()
            name = spec["name"]

            while version_spec.endswith(("*", ".")):
                version_spec = version_spec[:-1]

            removed = []
            while version_spec.startswith(all_version_chars):
                removed.append(version_spec[0])
                version_spec = version_spec[1:]

            if removed:
                op = "".join(removed)
                if set(op) != set("="):
                    print(
                        bold_yellow(
                            f"Found constraint: {op!r} for {name}. It'll be converted to '='"
                        ),
                        file=stream,
                    )

            if not version_spec:
                new_conda_deps.append(name)
            else:
                new_conda_deps.append(f"{name}={version_spec}")
        except Exception:
            log.exception(f"Error collecting version info from: {dep}")

    new_dependencies = {
        "dependencies": {"conda-forge": new_conda_deps, "pip": new_pip_deps}
    }

    post_install = contents.get("rccPostInstall")
    post_install_str = ""
    if post_install:
        post_install_str = yaml.dump({"post-install": post_install})

    output = f"""
# Required: A description of what's in the action package.
description: Action package description

# Required: The current version of this action package.
version: 0.0.1

# Required: A link to where the documentation on the package lives.
documentation: https://github.com/...

{yaml.safe_dump(new_dependencies, sort_keys=False)}{post_install_str}
"""

    target = conda_yaml.parent / "package.yaml"

    print(f"Creating {target.name}", file=stream)
    if dry_run:
        print(f"Contents:\n----------------\n{output}----------------\n", file=stream)
    else:
        target.write_text(output, encoding="utf-8")

    # Remove conda.yaml
    if backup:
        new_conda_yaml_path = conda_yaml.parent / (conda_yaml.name + ".bak")
        print(f"Renaming {conda_yaml.name} to {new_conda_yaml_path.name}", file=stream)
        if not dry_run:
            conda_yaml.rename(new_conda_yaml_path)
    else:
        print(f"Removing {conda_yaml.name}", file=stream)
        if not dry_run:
            os.remove(conda_yaml)

    # Remove robot.yaml
    robot_yaml = conda_yaml.parent / "robot.yaml"
    if robot_yaml.exists():
        if backup:
            new_robot_yaml_path = robot_yaml.parent / (robot_yaml.name + ".bak")
            print(
                f"Renaming {robot_yaml.name} to {new_robot_yaml_path.name}", file=stream
            )
            if not dry_run:
                robot_yaml.rename(new_robot_yaml_path)
        else:
            print(f"Removing {robot_yaml.name}", file=stream)
            if not dry_run:
                os.remove(robot_yaml)


def update_package(
    cwd: Path, dry_run: bool, backup: bool = True, *, stream=None
) -> None:
    """
    Updates a given package to conform to the latest structure.

    Current operations done:
        Convert conda.yaml or action-server.yaml to package.yaml

    Args:
        cwd: This is the directory where the action package is
        (i.e.: the directory with package.yaml or some older version
        having conda.yaml or action-server.yaml).
    """
    if stream is None:
        stream = sys.stdout
    conda_yaml = cwd / "conda.yaml"
    if not conda_yaml.exists():
        conda_yaml = cwd / "action-server.yaml"

    if conda_yaml.exists():
        print(f"Generating package.yaml from {conda_yaml.name}", file=stream)
        _create_package_from_conda_yaml(
            conda_yaml, dry_run=dry_run, backup=backup, stream=stream
        )


def create_hash(contents: str) -> str:
    import hashlib

    sha256_hash = hashlib.sha256()
    sha256_hash.update(contents.encode("utf-8"))
    return sha256_hash.hexdigest()


def create_conda_contents_from_package_yaml_contents(
    package_yaml: Path, package_yaml_contents: dict
) -> dict:
    def _get_in_dict(
        dct: dict,
        entry: str,
        expected_result_type: Optional[type],
        required: bool = True,
    ):
        v = dct.get(entry)
        if v is None:
            if not required:
                return None

            raise ActionPackageError(
                f"'Required session: {entry}' not specified (in {package_yaml})."
            )
        if expected_result_type is not None and not isinstance(v, expected_result_type):
            raise ActionPackageError(
                f"{entry} is expected to be {expected_result_type}. Found: {type(v)} (in {package_yaml})."
            )

        return v

    found_names = set()

    def _validate_name(name):
        if name in found_names:
            raise ActionPackageError(
                f"Dependency: {name} specified more than once (in {package_yaml})."
            )
        found_names.add(name)

    if not isinstance(package_yaml_contents, dict):
        raise ActionPackageError(
            f"Dict not found as top-level element (in {package_yaml})."
        )

    python_deps = _get_in_dict(package_yaml_contents, "dependencies", dict)
    conda_forge = _get_in_dict(python_deps, "conda-forge", list)
    local_wheels = _get_in_dict(python_deps, "local-wheels", list, required=False)
    post_install = _get_in_dict(
        package_yaml_contents, "post-install", list, required=False
    )
    pip = _get_in_dict(python_deps, "pip", list)

    converted_conda_entries: list = []
    found_truststore = False
    for entry in conda_forge:
        name, entry = convert_conda_entry(package_yaml, entry)
        _validate_name(name)
        if name in ("truststore", "robocorp-truststore"):
            found_truststore = True
        converted_conda_entries.append(entry)

    if "pip" not in found_names:
        raise ActionPackageError(
            f"'pip' entry not found in 'environment.conda-forge' (in {package_yaml})."
        )

    if "python" not in found_names:
        raise ActionPackageError(
            f"'python' entry not found in 'environment.conda-forge' (in {package_yaml})."
        )

    converted_pip_entries: list = []
    for entry in pip:
        name, entry = convert_pip_entry(package_yaml, entry)
        _validate_name(name)
        if name in ("truststore", "robocorp-truststore"):
            found_truststore = True
        converted_pip_entries.append(entry)

    if found_truststore:
        converted_pip_entries.insert(0, "--use-feature=truststore")

    cwd_dir = package_yaml.parent.absolute()
    if local_wheels:
        for wheel in local_wheels:
            original = wheel
            if not os.path.isabs(wheel):
                wheel = os.path.join(str(cwd_dir / wheel))

            if not os.path.exists(wheel):
                raise ActionPackageError(
                    f"'local-wheel': {original} could not be found (in {package_yaml})."
                )

            converted_pip_entries.append(Path(wheel).as_posix())

    converted_conda_entries.append({"pip": converted_pip_entries})

    data: dict = {"channels": ["conda-forge"], "dependencies": converted_conda_entries}
    if post_install:
        data["rccPostInstall"] = post_install

    return data


def create_conda_from_package_yaml(datadir: Path, package_yaml: Path) -> Path:
    """
    Args:
        package_yaml: This is the package.yaml from which the conda.yaml
            (to be supplied to rcc to create the env) should be created.

        package_yaml_contents: If specified this are the yaml-loaded contents
            of the package yaml.

    Returns: The path to the generated conda.yaml.
    """
    import yaml

    if not package_yaml.exists():
        raise ActionPackageError(f"File does not exist ({package_yaml}).")

    try:
        with open(package_yaml, "r", encoding="utf-8") as stream:
            package_yaml_contents = yaml.safe_load(stream)
    except Exception:
        raise ActionPackageError(f"Error loading file as yaml ({package_yaml}).")

    data = create_conda_contents_from_package_yaml_contents(
        package_yaml, package_yaml_contents
    )

    tmpdir = datadir / "tmpdir"
    if not tmpdir.exists():
        tmpdir.mkdir(exist_ok=True)

    new_package_yaml_contents = yaml.dump(data)

    conda_path = tmpdir / f"conda_{create_hash(new_package_yaml_contents)[:12]}.yaml"
    conda_path.write_text(new_package_yaml_contents)

    return conda_path
