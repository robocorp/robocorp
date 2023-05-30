from pathlib import Path
from typing import Optional, Sequence


class RunConfig:
    def __init__(
        self,
        output_dir: Path,
        path: Path,
        task_names: Sequence[str],
        max_log_files: int,
        max_log_file_size: str,
        console_colors: str,
        log_output_to_stdout: str,
        no_status_rc: bool,
        pyproject_contents: dict,
    ):
        """
        Args:
            output_dir: The directory where output should be put.
            path: The path (file or directory where the tasks should be collected from.
            task_name: The name(s) of the task(s) to run.
            max_log_files: The maximum number of log files to be created (if more would
                be needed the oldest one is deleted).
            max_log_file_size: The maximum size for the created log files.
            console_colors:
                "auto": uses the default console
                "plain": disables colors
                "ansi": forces ansi color mode
            log_output_to_stdout:
                "": query the RC_LOG_OUTPUT_STDOUT value.
                "no": don't provide log output to the stdout.
                "json": provide json output to the stdout.
            no_status_rc:
                Set to True so that if running tasks has an error inside the task
                the return code of the process is 0.
            pyproject_contents:
                The contents loaded from pyproject.toml.
        """
        self.output_dir = output_dir
        self.path = path
        self.task_names = task_names
        self.max_log_files = max_log_files
        self.max_log_file_size = max_log_file_size
        self.console_colors = console_colors
        self.log_output_to_stdout = log_output_to_stdout
        self.no_status_rc = no_status_rc
        self.pyproject_contents = pyproject_contents


class _GlobalConfig:
    instance: Optional[RunConfig] = None


def set_config(config: Optional[RunConfig]):
    from ._callback import OnExitContextManager

    _GlobalConfig.instance = config

    def on_exit():
        _GlobalConfig.instance = None

    return OnExitContextManager(on_exit)


def get_config() -> Optional[RunConfig]:
    return _GlobalConfig.instance
