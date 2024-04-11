import enum
import inspect
import json
import os
import sys
import time
import traceback
import typing
from argparse import ArgumentParser, ArgumentTypeError
from ast import FunctionDef
from io import StringIO
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Sequence, Union, overload

from robocorp.tasks._customization._extension_points import EPManagedParameters
from robocorp.tasks._protocols import ITask

from . import _constants
from ._argdispatch import arg_dispatch as _arg_dispatch
from ._constants import SUPPORTED_TYPES_IN_SCHEMA
from ._customization._plugin_manager import PluginManager


# Note: the args must match the 'dest' on the configured argparser.
@_arg_dispatch.register(name="list")
def list_tasks(
    *,
    path: str,
    glob: Optional[str] = None,
    __stream__: Optional[typing.IO] = None,
    pm: Optional[PluginManager] = None,
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
    from robocorp.tasks._protocols import TasksListTaskTypedDict
    from robocorp.tasks._task import Context

    p = Path(path)
    context = Context()
    if not p.exists():
        context.show_error(f"Path: {path} does not exist")
        return 1

    if pm is None:
        pm = PluginManager()

    original_stdout = sys.stdout
    if __stream__ is not None:
        write_to = __stream__
    else:
        write_to = original_stdout

    with redirect_stdout(sys.stderr):
        task: ITask
        tasks_found: List[TasksListTaskTypedDict] = []
        for task in collect_tasks(pm, p, glob=glob):
            entry: TasksListTaskTypedDict = {
                "name": task.name,
                "line": task.lineno,
                "file": task.filename,
                "docs": getattr(task.method, "__doc__") or "",
                "input_schema": task.input_schema,
                "output_schema": task.output_schema,
                "managed_params_schema": task.managed_params_schema,
                "options": task.options,
            }
            tasks_found.append(entry)

        write_to.write(json.dumps(tasks_found))
        write_to.flush()
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
    *,
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
    additional_arguments: Optional[List[str]] = None,
    preload_module: Optional[List[str]] = None,
    glob: Optional[str] = None,
    json_input: Optional[str] = None,
    pm: Optional[PluginManager] = None,
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
        additional_arguments: The arguments passed to the task.
        preload_module: The modules which should be pre-loaded (i.e.: loaded
            after the logging is in place but before any other task is collected).
        glob: A glob to define from which module names the tasks should be loaded.
        json_input: The path to a json file to be loaded to get the arguments.

    Returns:
        0 if everything went well.
        1 if there was some error running the task.
    """
    import copy

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
    from ._protocols import Status
    from ._task import Context, set_current_task

    if not output_dir:
        output_dir = os.environ.get("ROBOT_ARTIFACTS", "")

    if not output_dir:
        output_dir = "./output"

    if pm is None:
        pm = PluginManager()

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

    json_loaded_arguments: Optional[Dict[str, Any]] = None
    if json_input:
        json_path: Path = Path(json_input)
        if not json_path.exists():
            context.show_error(
                f"Error: The file passed as `--json-arguments` does not exist ({json_input})"
            )
            sys.exit(1)

        with json_path.open("rb") as stream:
            try:
                arguments = json.load(stream)
            except Exception as e:
                context.show_error(
                    f"Error: Unable to read the contents of {json_input} as json.\nOriginal error: {e}"
                )
                sys.exit(1)
            if not isinstance(arguments, dict):
                context.show_error(
                    f"Error: Expected the root of '{json_input}' to be a json object. Found: {type(arguments)} ({arguments})"
                )
                sys.exit(1)
            for key in arguments.keys():
                if not isinstance(key, str):
                    context.show_error(
                        f"Error: Expected all the keys in '{json_input}' to be strings. Found: {type(key)} ({key})"
                    )
                    sys.exit(1)
            json_loaded_arguments = arguments

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

            run_status: Union[Literal["PASS"], Literal["ERROR"]] = "PASS"
            log.start_run(run_name)
            try:
                setup_message = ""
                log.start_task("Collect tasks", "setup", "", 0)
                try:
                    if preload_module:
                        import importlib

                        for module in preload_module:
                            context.show(f"\nPre-loading module: {module}")
                            importlib.import_module(module)

                    if not task_name:
                        context.show(f"\nCollecting tasks from: {path}")
                    else:
                        context.show(
                            f"\nCollecting {task_or_tasks} {task_name} from: {path}"
                        )

                    tasks: List[ITask] = list(collect_tasks(pm, p, task_names, glob))

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
                            if json_loaded_arguments is not None:
                                kwargs = copy.deepcopy(json_loaded_arguments)
                                kwargs = _validate_and_convert_kwargs(pm, task, kwargs)

                            else:
                                kwargs = _normalize_arguments(
                                    pm, task, additional_arguments or []
                                )

                            result = task.run(**kwargs)
                            task.result = result
                            task.status = Status.PASS
                        except Exception as e:
                            task.status = Status.FAIL
                            # Make sure we put some message even if str(e) is empty.
                            task.message = str(e) or f"{e.__class__}"
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


class _CustomArgumentParser(ArgumentParser):
    def error(self, msg):
        raise RuntimeError(msg)

    def exit(self, status=0, message=None):
        raise RuntimeError(message or "")


def str_to_bool(s):
    # Convert string to boolean
    return s.lower() in ["true", "t", "yes", "1"]


def check_boolean(value):
    if value.lower() not in ["true", "false", "t", "f", "yes", "no", "1", "0"]:
        raise ArgumentTypeError(f"Invalid value for boolean flag: {value}")
    return str_to_bool(value)


def _validate_and_convert_kwargs(
    pm: PluginManager, task: ITask, kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    from typing import get_type_hints

    from robocorp.tasks._exceptions import InvalidArgumentsError

    target_method = task.method
    sig = inspect.signature(target_method)
    type_hints = get_type_hints(target_method)
    method_name = target_method.__code__.co_name
    new_kwargs: Dict[str, Any] = {}

    for param_name, param in sig.parameters.items():
        param_type = type_hints.get(param_name)

        is_managed_param = _is_managed_param(pm, param.name, param=param)
        if param_type is None:
            # If not given, default to `str`.
            if is_managed_param:
                param_type = _get_managed_param_type(pm, param)
            else:
                param_type = str

        if param.default is inspect.Parameter.empty:
            # It's required, so, let's see if it's in the kwargs.
            if not is_managed_param:
                if param_name not in kwargs:
                    raise InvalidArgumentsError(
                        f"Error. The parameter `{param_name}` was not defined in the input."
                    )

        passed_value = kwargs.get(param_name, inspect.Parameter.empty)

        if passed_value is not inspect.Parameter.empty:
            if param_type not in SUPPORTED_TYPES_IN_SCHEMA:
                model_validate = getattr(param_type, "model_validate", None)
                if model_validate is not None:
                    # Support for pydantic models.
                    try:
                        created = model_validate(passed_value)
                    except Exception as e:
                        msg = f"(error converting received json contents to pydantic model: {e}."
                        raise InvalidArgumentsError(
                            f"It's not possible to call: '{method_name}' because the passed arguments don't match the expected signature.\n{msg}"
                        )
                    new_kwargs[param_name] = created
                    continue
                else:
                    raise InvalidArgumentsError(
                        f"Error. The param type '{param_type.__name__}' in '{method_name}' is not supported. Supported parameter types: str, int, float, bool and pydantic.Model."
                    )

            check_type = param_type
            if param_type == float:
                check_type = (float, int)
            if not isinstance(passed_value, check_type):
                raise InvalidArgumentsError(
                    f"Error. Expected the parameter: `{param_name}` to be of type: {param_type.__name__}. Found type: {type(passed_value).__name__}."
                )

            new_kwargs[param_name] = passed_value

    new_kwargs = _inject_managed_params(pm, sig, new_kwargs, kwargs)
    error_message = ""
    try:
        sig.bind(**new_kwargs)
    except Exception as e:
        error_message = f"It's not possible to call: '{method_name}' because the passed arguments don't match the expected signature.\nError: {e}"
    if error_message:
        raise InvalidArgumentsError(error_message)

    return new_kwargs


def _inject_managed_params(
    pm: PluginManager,
    sig: inspect.Signature,
    new_kwargs: Dict[str, Any],
    original_kwargs: Dict[str, Any],
) -> Dict[str, Any]:
    if pm.has_instance(EPManagedParameters):
        ep_managed_parameters = pm.get_instance(EPManagedParameters)
        return ep_managed_parameters.inject_managed_params(
            sig, new_kwargs, original_kwargs
        )
    return new_kwargs


@overload
def _is_managed_param(
    pm: PluginManager,
    param_name: str,
    *,
    node: FunctionDef,
) -> bool:
    pass


@overload
def _is_managed_param(
    pm: PluginManager,
    param_name: str,
    *,
    param: inspect.Parameter,
) -> bool:
    pass


def _is_managed_param(
    pm: PluginManager,
    param_name: str,
    *,
    node: Optional[FunctionDef] = None,
    param: Optional[inspect.Parameter] = None,
) -> bool:
    """
    Verified if the given parameter is a managed parameter.

    Args:
        pm: The plugin manager.
        param_name: The name of the parameter to check.
        node: The FunctionDef node (ast), should be passed when doing lint
            analysis.
        param: The actual introspected parameter of the function, should
            be passed when actually calling the function.

    Returns: True if the given parameter is managed and False otherwise.

    Note: either node or param must be passed (but not both at the same time).
    """
    if node is None and param is None:
        raise AssertionError("Either node or param must be passed.")

    if node is not None and param is not None:
        raise AssertionError(
            "Either the node or param must be passed, but not both at the same time."
        )

    if pm.has_instance(EPManagedParameters):
        ep_managed_parameters = pm.get_instance(EPManagedParameters)
        if node is not None:
            return ep_managed_parameters.is_managed_param(param_name, node=node)
        elif param is not None:
            return ep_managed_parameters.is_managed_param(param_name, param=param)
        else:
            raise AssertionError("Not expected to get here.")
    return False


def _get_managed_param_type(pm: PluginManager, param: inspect.Parameter) -> type:
    if pm.has_instance(EPManagedParameters):
        ep_managed_parameters = pm.get_instance(EPManagedParameters)
        managed_param_type = ep_managed_parameters.get_managed_param_type(param)
        assert managed_param_type is not None
        return managed_param_type
    raise RuntimeError(
        "Error: Asked managed param type for a param which is not managed."
    )


def _normalize_arguments(
    pm: PluginManager, task: ITask, args: list[str]
) -> Dict[str, Any]:
    from typing import get_type_hints

    from robocorp.tasks._exceptions import InvalidArgumentsError

    target_method = task.method
    sig = inspect.signature(target_method)
    type_hints = get_type_hints(target_method)
    method_name = target_method.__code__.co_name

    # Prepare the argument parser
    parser = _CustomArgumentParser(
        prog=f"python -m {_constants.MODULE_ENTRY_POINT} {method_name} --",
        description=f"{method_name} task.",
        add_help=False,
    )

    # Add arguments to the parser based on the function signature and type hints
    for param_name, param in sig.parameters.items():
        if _is_managed_param(pm, param.name, param=param):
            continue

        param_type = type_hints.get(param_name)

        if param_type:
            if param_type not in SUPPORTED_TYPES_IN_SCHEMA:
                if hasattr(param_type, "model_validate"):
                    # Support for pydantic models.
                    parser.add_argument(f"--{param_name}", required=True)
                    continue

                raise InvalidArgumentsError(
                    f"Error. The param type '{param_type.__name__}' in '{method_name}' is not supported. Supported parameter types: str, int, float, bool and pydantic.Model."
                )

            if param_type == bool:
                param_type = check_boolean
            if param.default is not inspect.Parameter.empty:
                parser.add_argument(
                    f"--{param_name}", type=param_type, default=param.default
                )
            else:
                parser.add_argument(f"--{param_name}", type=param_type, required=True)
        else:
            parser.add_argument(f"--{param_name}", required=True)

    error_message = None
    try:
        parsed_args, argv = parser.parse_known_args(args)
    except (Exception, SystemExit) as e:
        error_message = f"It's not possible to call: '{method_name}' because the passed arguments don't match the expected signature.\n{_get_usage(parser)}.\nError: {str(e)}."

    if error_message:
        raise InvalidArgumentsError(error_message)

    if argv:
        msg = "Unrecognized arguments: %s" % " ".join(argv)
        raise InvalidArgumentsError(
            f"It's not possible to call: '{method_name}' because the passed arguments don't match the expected signature.\n{_get_usage(parser)}.\n{msg}"
        )

    # Call the user function with the parsed arguments.
    kwargs = {}
    for param_name in sig.parameters:
        param_value = getattr(parsed_args, param_name)

        if param_type not in SUPPORTED_TYPES_IN_SCHEMA:
            model_validate = getattr(param_type, "model_validate", None)
            if model_validate is not None:
                try:
                    param_value = json.loads(param_value)
                except Exception:
                    msg = f"(error interpreting contents for {param_name} as a json)."
                    raise InvalidArgumentsError(
                        f"It's not possible to call: '{method_name}' because the passed arguments don't match the expected signature.\n{msg}"
                    )

        kwargs[param_name] = param_value

    kwargs = _validate_and_convert_kwargs(pm, task, kwargs)
    return kwargs


def _get_usage(parser) -> str:
    f = StringIO()
    parser.print_usage(f)
    usage = f.getvalue().strip()
    if usage:
        usage = usage[0].upper() + usage[1:]
    return usage
