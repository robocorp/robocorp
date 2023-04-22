from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Any

from ._protocols import ITask
from robocorp import robolog


def read_filters_from_pyproject_toml(context, path: Path) -> robolog.BaseConfig:
    filters: List[robolog.Filter] = []

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
            return robolog.ConfigFilesFiltering()
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
    for part in "tool.robocorp.robolog".split("."):
        read_parts.append(part)

        obj = obj.get(part)
        if not obj:
            break

        elif not isinstance(obj, dict):
            context.show_error(
                f"Expected {'.'.join(read_parts)} to be a dict in {pyproject}."
            )
            break

    log_filter_rules: list = []
    obj = obj.get("log_filter_rules")
    if obj:
        if isinstance(obj, list):
            log_filter_rules = obj
        else:
            context.show_error(
                f"Expected {'.'.join(read_parts)} to be a list in {pyproject}."
            )

    # If we got here we have the 'log_filter_rules', which should be a list of
    # dicts in a structure such as: {name = "difflib", kind = "log_on_project_call"}
    # expected kinds are the values of the FilterKind.
    for rule in log_filter_rules:
        if isinstance(rule, dict):
            name = rule.get("name")
            kind = rule.get("kind")
            if not name:
                context.show_error(
                    f"Expected a rule from 'tool.robocorp.robolog.log_filter_rules' to have a 'name' in {pyproject}."
                )
                continue

            if not kind:
                context.show_error(
                    f"Expected a rule from 'tool.robocorp.robolog.log_filter_rules' to have a 'kind' in {pyproject}."
                )
                continue

            if not isinstance(name, str):
                context.show_error(
                    f"Expected a rule from 'tool.robocorp.robolog.log_filter_rules' to have 'name' as a str in {pyproject}."
                )
                continue

            if not isinstance(kind, str):
                context.show_error(
                    f"Expected a rule from 'tool.robocorp.robolog.log_filter_rules' to have 'kind' as a str in {pyproject}."
                )
                continue

            f: Optional[robolog.FilterKind] = getattr(robolog.FilterKind, kind, None)
            if f is None:
                context.show_error(
                    f"Rule from 'tool.robocorp.robolog.log_filter_rules' has invalid 'kind': >>{kind}<< in {pyproject}."
                )
                continue

            filters.append(robolog.Filter(name, f))

    return robolog.ConfigFilesFiltering(filters=filters)


def _log_before_task_run(task: ITask):
    robolog.start_task(
        task.name,
        task.module_name,
        task.filename,
        task.method.__code__.co_firstlineno,
        [],
    )


def _log_after_task_run(task: ITask):
    status = task.status
    robolog.end_task(task.name, task.module_name, status, task.message)


@contextmanager
def setup_cli_auto_logging(config: Optional[robolog.BaseConfig]):
    # This needs to be called before importing code which needs to show in the log
    # (user or library).

    from robocorp.tasks._hooks import before_task_run
    from robocorp.tasks._hooks import after_task_run

    with robolog.setup_auto_logging(config):
        with before_task_run.register(_log_before_task_run), after_task_run.register(
            _log_after_task_run
        ):
            try:
                yield
            finally:
                robolog.close_log_outputs()
