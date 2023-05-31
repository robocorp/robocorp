from pathlib import Path
from typing import Any, List, Optional

from ._protocols import IContextErrorReport, PyProjectInfo


def read_pyproject_toml(path: Path) -> Optional[PyProjectInfo]:
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
        pyproject: The path to the pyproject.toml file.
        toml_contents: The toml contents read.
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
