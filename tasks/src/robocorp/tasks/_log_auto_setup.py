from contextlib import contextmanager
from pathlib import Path
from typing import Any, List, Optional

from robocorp import log
from robocorp.tasks._protocols import PyProjectInfo

from ._protocols import IContextErrorReport, ITask


def read_robocorp_log_config(
    context: IContextErrorReport, pyproject: PyProjectInfo
) -> log.BaseConfig:
    from ._toml_settings import read_section_from_toml

    if not pyproject.toml_contents:
        log.ConfigFilesFiltering()

    obj: Any = pyproject.toml_contents
    filters: List[log.Filter] = []
    if isinstance(obj, dict):
        # Filter(name="RPA", kind=FilterKind.log_on_project_call),
        # Filter("selenium", FilterKind.log_on_project_call),
        # Filter("SeleniumLibrary", FilterKind.log_on_project_call),
        obj = read_section_from_toml(pyproject, "tool.robocorp.log", context)

        if isinstance(obj, dict):
            filters = _load_filters(obj, context, pyproject.pyproject)

    return log.ConfigFilesFiltering(filters=filters)


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
