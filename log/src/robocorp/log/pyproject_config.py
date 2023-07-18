"""
This module contains functions to read a pyproject.toml file and 
read the related tool.robocorp.log section.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, List, Optional

from robocorp import log
from robocorp.log.protocols import IContextErrorReport


@dataclass
class PyProjectInfo:
    pyproject: Path
    toml_contents: dict


def read_pyproject_toml(path: Path) -> Optional[PyProjectInfo]:
    """
    Args:
        path:
            This is the path where the `pyproject.toml` file should be found.
            If it's not found directly in the given path, parent folders will
            be searched for the `pyproject.toml`.

    Returns:
        The information on the pyproject file (the toml contents and the actual
        path where the pyproject.toml was found).
    """
    while True:
        pyproject = path / "pyproject.toml"
        try:
            if pyproject.exists():
                break
        except OSError:
            continue

        parent = path.parent
        if parent == path or not parent:
            # Couldn't find pyproject.toml
            return None
        path = parent

    try:
        toml_contents = pyproject.read_text(encoding="utf-8")
    except Exception:
        raise OSError(f"Could not read the contents of: {pyproject}.")

    pyproject_toml: Any = None
    try:
        try:
            import tomllib  # type: ignore
        except ImportError:
            import tomli as tomllib  # type: ignore

        pyproject_toml = tomllib.loads(toml_contents)
    except Exception:
        raise RuntimeError(f"Could not interpret the contents of {pyproject} as toml.")
    return PyProjectInfo(pyproject=pyproject, toml_contents=pyproject_toml)


def read_section_from_toml(
    pyproject_info: PyProjectInfo,
    section_name: str,
    context: Optional[IContextErrorReport] = None,
) -> Any:
    """
    Args:
        pyproject_info: Information on the pyroject toml.
        section_name: The name of the section to be read
            i.e.: tool.robocorp.log
        context: The context used to report errors.

    Returns:
        The section which was read.
    """
    read_parts: List[str] = []
    obj: Any = pyproject_info.toml_contents
    parts = section_name.split(".")

    last_part = parts[-1]
    parts = parts[:-1]

    for part in parts:
        read_parts.append(part)

        obj = obj.get(part)
        if obj is None:
            return None

        elif not isinstance(obj, dict):
            if context is not None:
                context.show_error(
                    f"Expected '{'.'.join(read_parts)}' to be a dict in {pyproject_info.pyproject}."
                )
            return None

    if not isinstance(obj, dict):
        if obj is not None:
            if context is not None:
                context.show_error(
                    f"Expected '{'.'.join(read_parts)}' to be a dict in {pyproject_info.pyproject}."
                )
        return None

    return obj.get(last_part)


def read_robocorp_auto_log_config(
    context: IContextErrorReport, pyproject: PyProjectInfo
) -> log.AutoLogConfigBase:
    """
    Args:
        context: The context used to report errors.
        pyproject: The pyproject information from where the configuration should
            be loaded.

    Returns:
        The autolog configuration read from the given pyproject information.
    """
    from robocorp.log import FilterKind

    if not pyproject.toml_contents:
        log.DefaultAutoLogConfig()

    obj: Any = pyproject.toml_contents
    filters: List[log.Filter] = []

    default_library_filter_kind = FilterKind.log_on_project_call

    if isinstance(obj, dict):
        # Filter(name="RPA", kind=FilterKind.log_on_project_call),
        # Filter("selenium", FilterKind.log_on_project_call),
        # Filter("SeleniumLibrary", FilterKind.log_on_project_call),
        obj = read_section_from_toml(pyproject, "tool.robocorp.log", context)

        if isinstance(obj, dict):
            filters = _load_filters(obj, context, pyproject.pyproject)
            kind = obj.get("default_library_filter_kind")

            if kind is not None:
                if not isinstance(kind, str):
                    context.show_error(
                        f"Expected 'tool.robocorp.log.log_filter_rules.default_library_filter_kind' to have "
                        f"'kind' as a str (and not {type(kind)} in {pyproject}."
                    )
                else:
                    f: Optional[log.FilterKind] = getattr(log.FilterKind, kind, None)
                    if f is None:
                        context.show_error(
                            f"Rule from 'tool.robocorp.log.log_filter_rules.default_library_filter_kind' "
                            f"has invalid 'kind': >>{kind}<< in {pyproject}."
                        )
                    else:
                        default_library_filter_kind = f

    return log.DefaultAutoLogConfig(
        filters=filters, default_library_filter_kind=default_library_filter_kind
    )


def _load_filters(
    obj: dict, context: IContextErrorReport, pyproject: Path
) -> List[log.Filter]:
    filters: List[log.Filter] = []
    log_filter_rules: list = []
    list_obj = obj.get("log_filter_rules")
    if not list_obj:
        return filters

    if isinstance(list_obj, list):
        log_filter_rules = list_obj
    else:
        context.show_error(
            f"Expected 'tool.robocorp.log.log_filter_rules' to be a list in {pyproject}."
        )
        return filters

    # If we got here we have the 'log_filter_rules', which should be a list of
    # dicts in a structure such as: {name = "difflib", kind = "log_on_project_call"}
    # expected kinds are the values of the FilterKind.
    for rule in log_filter_rules:
        if isinstance(rule, dict):
            name = rule.get("name")
            kind = rule.get("kind")
            if not name:
                context.show_error(
                    f"Expected rule: {rule} from 'tool.robocorp.log.log_filter_rules' to have a 'name' in {pyproject}."
                )
                continue

            if not kind:
                context.show_error(
                    f"Expected rule: {rule} from 'tool.robocorp.log.log_filter_rules' to have a 'kind' in {pyproject}."
                )
                continue

            if not isinstance(name, str):
                context.show_error(
                    f"Expected rule: {rule} from 'tool.robocorp.log.log_filter_rules' to have 'name' as a str in {pyproject}."
                )
                continue

            if not isinstance(kind, str):
                context.show_error(
                    f"Expected rule: {rule} from 'tool.robocorp.log.log_filter_rules' to have 'kind' as a str in {pyproject}."
                )
                continue

            f: Optional[log.FilterKind] = getattr(log.FilterKind, kind, None)
            if f is None:
                context.show_error(
                    f"Rule from 'tool.robocorp.log.log_filter_rules' ({rule}) has invalid 'kind': >>{kind}<< in {pyproject}."
                )
                continue

            filters.append(log.Filter(name, f))
    return filters
