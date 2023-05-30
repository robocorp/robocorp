from contextlib import contextmanager
from pathlib import Path
from typing import Any, List, Optional, Tuple

from robocorp import log

from ._protocols import ITask


def read_pyproject_toml(context, path: Path) -> Optional[Tuple[Path, dict]]:
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
    return pyproject, pyproject_toml


def read_robocorp_log_config(
    context, pyproject: Path, pyproject_toml_contents: dict
) -> log.BaseConfig:
    if not pyproject_toml_contents:
        log.ConfigFilesFiltering()

    obj: Any = pyproject_toml_contents
    filters: List[log.Filter] = []
    if isinstance(obj, dict):
        # Filter(name="RPA", kind=FilterKind.log_on_project_call),
        # Filter("selenium", FilterKind.log_on_project_call),
        # Filter("SeleniumLibrary", FilterKind.log_on_project_call),

        read_parts: List[str] = []
        for part in "tool.robocorp.log".split("."):
            read_parts.append(part)

            obj = obj.get(part)
            if not obj:
                break

            elif not isinstance(obj, dict):
                context.show_error(
                    f"Expected {'.'.join(read_parts)} to be a dict in {pyproject}."
                )
                break
        else:
            if isinstance(obj, dict):
                filters = _load_filters(obj, context, pyproject)

    return log.ConfigFilesFiltering(filters=filters)


def _load_filters(obj: dict, context, pyproject) -> List[log.Filter]:
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


def _log_before_task_run(task: ITask):
    log.start_task(
        task.name,
        task.module_name,
        task.filename,
        task.method.__code__.co_firstlineno,
        getattr(task.method, "__doc__", ""),
    )


def _log_after_task_run(task: ITask):
    status = task.status
    log.end_task(task.name, task.module_name, status, task.message)


@contextmanager
def setup_cli_auto_logging(config: Optional[log.BaseConfig]):
    # This needs to be called before importing code which needs to show in the log
    # (user or library).

    from robocorp.tasks._hooks import after_task_run, before_task_run

    with log.setup_auto_logging(config):
        with before_task_run.register(_log_before_task_run), after_task_run.register(
            _log_after_task_run
        ):
            try:
                yield
            finally:
                log.close_log_outputs()
