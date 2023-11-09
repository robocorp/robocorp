import enum
import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import List, Literal, Optional, Sequence, Union

from ._argdispatch import arg_dispatch as _arg_dispatch


# Note: the args must match the 'dest' on the configured argparser.
@_arg_dispatch.register(name="list")
def list_tasks(
    path: str,
) -> int:
    """
    Prints the tasks available at a given path to the stdout in json format.

    [
        {
            "name": "task_name",
            "line": 10,
            "file": "/usr/code/projects/tasks.py",
            "docs": "Task docstring",
        },
        ...
    ]

    Args:
        path: The path (file or directory) from where tasks should be collected.
    """
    from contextlib import redirect_stdout

    from robocorp.tasks._collect_tasks import collect_tasks
    from robocorp.tasks._protocols import ITask
    from robocorp.tasks._task import Context

    p = Path(path)
    context = Context()
    if not p.exists():
        context.show_error(f"Path: {path} does not exist")
        return 1

    original_stdout = sys.stdout
    with redirect_stdout(sys.stderr):
        task: ITask
        tasks_found = []
        for task in collect_tasks(p):
            tasks_found.append(
                {
                    "name": task.name,
                    "line": task.lineno,
                    "file": task.filename,
                    "docs": getattr(task.method, "__doc__") or "",
                }
            )

        original_stdout.write(json.dumps(tasks_found))
        original_stdout.flush()
    return 0


def _os_exit(retcode: int):
    """
    Kills subprocesses and exits with the given returncode.
    """
    from robocorp import log

    try:
        import psutil

        curr_process = psutil.Process()
        try:
            try:
                children_processes = list(curr_process.children(recursive=True))
            except Exception:
                # Retry once
                children_processes = list(curr_process.children(recursive=True))

            log.info(
                f"robocorp-tasks killing processes after run: {children_processes}"
            )
            for p in children_processes:
                try:
                    p.kill()
                except Exception as e:
                    log.debug(f"Exception when terminating process: {p.pid}: {e}")

            # Give processes 2 seconds to exit cleanly and force-kill afterwards
            _gone, alive = psutil.wait_procs(children_processes, 2)
            for p in alive:
                try:
                    p.terminate()
                except Exception as e:
                    # Expected: process no longer exists.
                    log.debug(f"Exception when killing process: {p.pid}: {e}")
                # Wait a bit more after terminate.
                psutil.wait_procs(alive, 5)
        except Exception as e:
            log.debug(f"Exception when listing/killing processes: {e}")

        sys.stdout.flush()
        sys.stderr.flush()
        # Give some time for other threads to run just a little bit more.
        time.sleep(0.2)
    finally:
        os._exit(retcode)


class _OsExit(enum.Enum):
    NO = 0
    BEFORE_TEARDOWN = 1
    AFTER_TEARDOWN = 2


# Note: the args must match the 'dest' on the configured argparser.
@_arg_dispatch.register()
def run(
    output_dir: str,
    path: str,
    task_name: Union[Sequence[str], str, None],
    max_log_files: int = 5,
    max_log_file_size: str = "1MB",
    console_colors: str = "auto",
    log_output_to_stdout: str = "",
    no_status_rc: bool = False,
    teardown_dump_threads_timeout: Optional[float] = None,
    teardown_interrupt_timeout: Optional[float] = None,
    os_exit: Optional[str] = None,
) -> int:
    """
    Runs a task.

    Args:
        output_dir: The directory where output should be put.
        path: The path (file or directory where the tasks should be collected from.
        task_name: The name(s) of the task to run.
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
        teardown_dump_threads_timeout: Can be used to customize the time
            to dump threads in the teardown process if it doesn't complete
            until the specified timeout.
            It's also possible to specify it with the
            RC_TEARDOWN_DUMP_THREADS_TIMEOUT environment variable.
            Defaults to 5 seconds if not specified.
        teardown_interrupt_timeout: Can be used to customize the time
            to interrupt the teardown process after a given timeout.
            It's also possible to specify it with the
            RC_TEARDOWN_INTERRUPT_TIMEOUT environment variable.
            Defaults to not interrupting.
        os_exit: Can be used to exit the process early, without going through
            the regular process teardown. In general it's not recommended, but
            it can be used as a workaround to avoid crashes or deadlocks under
            specific situations found either during the tasks session teardown
            or during the interpreter exit.
            Note that subprocesses will be force-killed before exiting.
            Accepted values: 'before-teardown', 'after-teardown'.
            'before-teardown' means that the process will exit without running
                the tasks session teardown.
            'after-teardown' means that the process will exit right after the
                tasks session teardown takes place.

    Returns:
        0 if everything went well.
        1 if there was some error running the task.
    """
    from robocorp.log import console, redirect
    from robocorp.log.pyproject_config import (
        read_pyproject_toml,
        read_robocorp_auto_log_config,
    )

    from robocorp.tasks._interrupts import interrupt_on_timeout

    from ._collect_tasks import collect_tasks
    from ._config import RunConfig, set_config
    from ._exceptions import RobocorpTasksCollectError
    from ._hooks import (
        after_all_tasks_run,
        after_task_run,
        before_all_tasks_run,
        before_task_run,
    )
    from ._log_auto_setup import setup_cli_auto_logging
    from ._log_output_setup import setup_log_output, setup_log_output_to_port
    from ._protocols import ITask, Status
    from ._task import Context, set_current_task

    if not output_dir:
        output_dir = os.environ.get("ROBOT_ARTIFACTS", "")

    if not output_dir:
        output_dir = "./output"

    console.set_mode(console_colors)

    # Don't show internal machinery on tracebacks:
    # setting __tracebackhide__ will make it so that robocorp-log
    # won't show this frame onwards in the logging.
    __tracebackhide__ = 1

    p = Path(path).absolute()
    context = Context()
    if not p.exists():
        context.show_error(f"Path: {path} does not exist")
        return 1

    if teardown_dump_threads_timeout is None:
        v = os.getenv("RC_TEARDOWN_DUMP_THREADS_TIMEOUT", "5")

        try:
            teardown_dump_threads_timeout = float(v)
        except ValueError:
            sys.stderr.write(
                f"Value set for RC_TEARDOWN_DUMP_THREADS_TIMEOUT ({v}) is not a valid float."
            )
            sys.exit(1)

    if teardown_interrupt_timeout is None:
        v = os.getenv("RC_TEARDOWN_INTERRUPT_TIMEOUT", "-1")

        try:
            teardown_interrupt_timeout = float(v)
        except ValueError:
            sys.stderr.write(
                f"Value set for RC_TEARDOWN_INTERRUPT_TIMEOUT ({v}) is not a valid float."
            )
            sys.exit(1)

    os_exit_enum = _OsExit.NO
    used_env = False
    if not os_exit:
        os_exit = os.getenv("RC_OS_EXIT", "")
        used_env = True

    if os_exit:
        if os_exit == "before-teardown":
            os_exit_enum = _OsExit.BEFORE_TEARDOWN
        elif os_exit == "after-teardown":
            os_exit_enum = _OsExit.AFTER_TEARDOWN
        else:
            if used_env:
                context.show_error(f"Error: RC_OS_EXIT invalid value: {os_exit}")
            else:
                context.show_error(
                    f"Error: --os-exit argument invalid value: {os_exit}"
                )
            sys.exit(1)

    # Enable faulthandler (writing to sys.stderr) early on in the
    # task execution process.
    import faulthandler

    faulthandler.enable()

    from robocorp import log

    task_names: Sequence[str]
    if not task_name:
        task_names = []
        task_or_tasks = "tasks"
    elif isinstance(task_name, str):
        task_names = [task_name]
        task_or_tasks = "task"
    else:
        task_names = task_name
        task_name = ", ".join(str(x) for x in task_names)
        task_or_tasks = "task" if len(task_names) == 1 else "tasks"

    config: log.AutoLogConfigBase
    pyproject_path_and_contents = read_pyproject_toml(p)
    pyproject_toml_contents: dict
    if pyproject_path_and_contents is None:
        config = log.DefaultAutoLogConfig()
        pyproject_toml_contents = {}
    else:
        config = read_robocorp_auto_log_config(context, pyproject_path_and_contents)
        pyproject_toml_contents = pyproject_path_and_contents.toml_contents

    output_dir_path = Path(output_dir).absolute()
    output_dir_path.mkdir(parents=True, exist_ok=True)

    run_config = RunConfig(
        output_dir_path,
        p,
        task_names,
        max_log_files,
        max_log_file_size,
        console_colors,
        log_output_to_stdout,
        no_status_rc,
        pyproject_toml_contents,
    )

    retcode = 22  # Something went off if this was kept until the end.
    try:
        with set_config(run_config), setup_cli_auto_logging(
            # Note: we can't customize what's a "project" file or a "library" file,
            # right now the customizations are all based on module names.
            config
        ), redirect.setup_stdout_logging(log_output_to_stdout), setup_log_output(
            output_dir=output_dir_path,
            max_files=max_log_files,
            max_file_size=max_log_file_size,
        ), setup_log_output_to_port(), context.register_lifecycle_prints():
            run_name = os.path.basename(p)
            if task_name:
                run_name += f" - {task_name}"

            # Status string from `log` module
            # TODO: Replace with enum
            run_status: Union[Literal["PASS"], Literal["ERROR"]] = "PASS"
            log.start_run(run_name)
            try:
                setup_message = ""
                log.start_task("Collect tasks", "setup", "", 0)
                try:
                    if not task_name:
                        context.show(f"\nCollecting tasks from: {path}")
                    else:
                        context.show(
                            f"\nCollecting {task_or_tasks} {task_name} from: {path}"
                        )

                    tasks: List[ITask] = list(collect_tasks(p, task_names))

                    if not tasks:
                        raise RobocorpTasksCollectError(
                            f"Did not find any tasks in: {path}"
                        )
                except Exception as e:
                    run_status = "ERROR"
                    setup_message = str(e)

                    log.exception()
                    if not isinstance(e, RobocorpTasksCollectError):
                        traceback.print_exc()
                    else:
                        context.show_error(setup_message)

                    retcode = 1
                    return retcode
                finally:
                    log.end_task("Collect tasks", "setup", run_status, setup_message)

                before_all_tasks_run(tasks)

                try:
                    for task in tasks:
                        set_current_task(task)
                        before_task_run(task)
                        try:
                            task.run()
                            task.status = Status.PASS
                        except Exception as e:
                            task.status = Status.FAIL
                            task.message = str(e)
                            task.exc_info = sys.exc_info()
                        finally:
                            with interrupt_on_timeout(
                                teardown_dump_threads_timeout,
                                teardown_interrupt_timeout,
                                "Teardown",
                                "--teardown-dump-threads-timeout",
                                "RC_TEARDOWN_DUMP_THREADS_TIMEOUT",
                                "--teardown-interrupt-timeout",
                                "RC_TEARDOWN_INTERRUPT_TIMEOUT",
                            ):
                                after_task_run(task)
                            set_current_task(None)
                            if task.failed:
                                run_status = "ERROR"
                finally:
                    log.start_task("Teardown tasks", "teardown", "", 0)
                    try:
                        with interrupt_on_timeout(
                            teardown_dump_threads_timeout,
                            teardown_interrupt_timeout,
                            "Teardown",
                            "--teardown-dump-threads-timeout",
                            "RC_TEARDOWN_DUMP_THREADS_TIMEOUT",
                            "--teardown-interrupt-timeout",
                            "RC_TEARDOWN_INTERRUPT_TIMEOUT",
                        ):
                            if os_exit_enum == _OsExit.BEFORE_TEARDOWN:
                                log.info(
                                    "The tasks teardown was skipped due to option to os._exit before teardown."
                                )
                            else:
                                after_all_tasks_run(tasks)
                        # Always do a process snapshot as the process is about to finish.
                        log.process_snapshot()
                    finally:
                        log.end_task("Teardown tasks", "teardown", Status.PASS, "")

                if no_status_rc:
                    retcode = 0
                    return retcode
                else:
                    retcode = int(any(task.failed for task in tasks))
                    return retcode
            finally:
                log.end_run(run_name, run_status)
    except:
        # This means we had an error in the framework (as user errors should
        # be handled on the parts that call user code).
        if os_exit_enum != _OsExit.NO:
            # Show the exception if we'll do an early exit, otherwise
            # let Python itself print it.
            retcode = 23
            traceback.print_exc()
        raise
    finally:
        if os_exit_enum != _OsExit.NO:
            # Either before or after will exit here (the difference is that
            # if before teardown was requested the teardown is skipped).
            log.info(f"robocorp-tasks: os._exit option: {os_exit}")
            _os_exit(retcode)

        # After the run is finished, start a timer which will print the
        # current threads if the process doesn't exit after a given timeout.
        from threading import Timer

        teardown_time = time.monotonic()
        var_name_dump_threads = "RC_DUMP_THREADS_AFTER_RUN"
        if os.environ.get(var_name_dump_threads, "1").lower() not in (
            "",
            "0",
            "f",
            "false",
        ):
            var_name_dump_threads_timeout = "RC_DUMP_THREADS_AFTER_RUN_TIMEOUT"
            try:
                timeout = float(os.environ.get(var_name_dump_threads_timeout, "40"))
            except Exception:
                sys.stderr.write(
                    f"Invalid value for: {var_name_dump_threads_timeout} environment value. Cannot convert to float."
                )
                timeout = 40

            from robocorp.tasks._interrupts import dump_threads

            def on_timeout():
                dump_threads(
                    message=(
                        f"All tasks have run but the process still hasn't exited "
                        f"elapsed {time.monotonic() - teardown_time:.2f} seconds after teardown end. Showing threads found:"
                    )
                )

            t = Timer(timeout, on_timeout)
            t.daemon = True
            t.start()
