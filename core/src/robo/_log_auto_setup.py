from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Sequence, Union, List, Any

from ._protocols import ITask
import typing

if typing.TYPE_CHECKING:
    from robo_log import Filter  # @UnusedImport


def read_filters_from_pyproject_toml(context, path: Path) -> List["Filter"]:
    from robo_log import Filter  # @Reimport
    from robo_log._config import FilterKind

    filters: List[Filter] = []

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
            return filters
        path = parent

    try:
        toml_contents = pyproject.read_text(encoding="utf-8")
    except Exception:
        raise OSError(f"Could not read the contents of: {pyproject}.")

    obj: Any
    try:
        try:
            import tomllib  # type: ignore
        except ImportError:
            import tomli as tomllib  # type: ignore

        obj = tomllib.loads(toml_contents)
    except Exception:
        raise RuntimeError(f"Could not interpret the contents of {pyproject} as toml.")

    # Filter(name="RPA", kind=FilterKind.log_on_project_call),
    # Filter("selenium", FilterKind.log_on_project_call),
    # Filter("SeleniumLibrary", FilterKind.log_on_project_call),

    read_parts: List[str] = []
    for part in "tool.robo.log.log_filter_rules".split("."):
        read_parts.append(part)

        obj = obj.get(part)
        if not obj:
            return filters

        if part == "log_filter_rules":
            if not isinstance(obj, (list, tuple)):
                context.show_error(
                    f"Expected {'.'.join(read_parts)} to be a list in {pyproject}."
                )
                return filters
            log_filter_rule = obj
            break

        elif not isinstance(obj, dict):
            context.show_error(
                f"Expected {'.'.join(read_parts)} to be a dict in {pyproject}."
            )
            return filters

    # If we got here we have the 'log_filter_rules', which should be a list of
    # dicts in a structure such as: {name = "difflib", kind = "log_on_project_call"}
    # expected kinds are the values of the FilterKind.
    if not isinstance(log_filter_rule, (list, tuple)):
        return filters

    for rule in log_filter_rule:
        if isinstance(rule, dict):
            name = rule.get("name")
            kind = rule.get("kind")
            if not name:
                context.show_error(
                    f"Expected a rule from 'tool.robo.log.log_filter_rules' to have a 'name' in {pyproject}."
                )
                continue

            if not kind:
                context.show_error(
                    f"Expected a rule from 'tool.robo.log.log_filter_rules' to have a 'kind' in {pyproject}."
                )
                continue

            if not isinstance(name, str):
                context.show_error(
                    f"Expected a rule from 'tool.robo.log.log_filter_rules' to have 'name' as a str in {pyproject}."
                )
                continue

            if not isinstance(kind, str):
                context.show_error(
                    f"Expected a rule from 'tool.robo.log.log_filter_rules' to have 'kind' as a str in {pyproject}."
                )
                continue

            f: Optional[FilterKind] = getattr(FilterKind, kind, None)
            if f is None:
                context.show_error(
                    f"Rule from 'tool.robo.log.log_filter_rules' has invalid 'kind': >>{kind}<< in {pyproject}."
                )
                continue

            filters.append(Filter(name, f))

    return filters


def _log_before_task_run(task: ITask):
    import robo_log

    robo_log.start_task(
        task.name,
        task.module_name,
        task.filename,
        task.method.__code__.co_firstlineno,
        [],
    )


def _log_after_task_run(task: ITask):
    import robo_log

    status = task.status
    robo_log.end_task(task.name, task.module_name, status, task.message)


@contextmanager
def setup_auto_logging(
    tracked_folders: Optional[Sequence[Union[Path, str]]] = None,
    untracked_folders: Optional[Sequence[Union[Path, str]]] = None,
    filters: Sequence["Filter"] = (),
):
    # This needs to be called before importing code which needs to show in the log
    # (user or library).

    import robo_log
    from robo._hooks import before_task_run
    from robo._hooks import after_task_run

    with robo_log.setup_auto_logging(
        tracked_folders=tracked_folders,
        untracked_folders=untracked_folders,
        filters=filters,
    ):
        with before_task_run.register(_log_before_task_run), after_task_run.register(
            _log_after_task_run
        ):
            try:
                yield
            finally:
                robo_log.close_log_outputs()
