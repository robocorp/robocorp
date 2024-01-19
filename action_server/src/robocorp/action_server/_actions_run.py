import datetime
import inspect
import json
import logging
import time
import typing
from typing import Annotated, Any, Dict, Optional

from fastapi import HTTPException
from fastapi.params import Header, Param
from pydantic import BaseModel

if typing.TYPE_CHECKING:
    from ._models import Action, Run

log = logging.getLogger(__name__)


_spec_api_type_to_python_type_str = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
}

_spec_api_type_to_python_type = {
    "string": str,
    "integer": int,
    "number": float,
    "boolean": bool,
}


def _create_run_artifacts_dir(action: "Action", run_id: str) -> str:
    """
    Returns:
        The path, relative to the settings.artifacts_dir which should be used
        to store the output of the given run.
    """
    from ._settings import get_settings

    settings = get_settings()
    artifacts_dir = settings.artifacts_dir
    path = run_id
    target_dir = artifacts_dir / path
    target_dir.mkdir(parents=True, exist_ok=False)
    return path


def _create_run(
    action: "Action", run_id: str, inputs: dict, relative_artifacts_dir: str
) -> "Run":
    from robocorp.action_server._models import RUN_ID_COUNTER, Counter

    from ._database import datetime_to_str
    from ._models import Run, RunStatus, get_db
    from ._runs_state_cache import get_global_runs_state

    db = get_db()
    run_kwargs: Dict[str, Any] = dict(
        id=run_id,
        status=RunStatus.NOT_RUN,
        action_id=action.id,
        start_time=datetime_to_str(datetime.datetime.now(datetime.timezone.utc)),
        run_time=None,
        inputs=json.dumps(inputs),
        result=None,
        error_message=None,
        relative_artifacts_dir=relative_artifacts_dir,
    )
    with db.transaction():
        with db.cursor() as cursor:
            db.execute_update_returning(
                cursor,
                "UPDATE counter SET value=value+1 WHERE id=? RETURNING value",
                [RUN_ID_COUNTER],
            )
            counter_record = cursor.fetchall()
            if not counter_record:
                raise RuntimeError(
                    f"Error. No counter found for run_id. Counters in db: {db.all(Counter)}"
                )
            run_kwargs["numbered_id"] = counter_record[0][0]

        run = Run(**run_kwargs)
        db.insert(run)

    # Ok, transaction finished properly. Let's add it to our in-memory cache.
    global_runs_state = get_global_runs_state()
    global_runs_state.on_run_inserted(run)

    return run


def _update_run(run: "Run", initial_time: float, run_finished: bool, **changes):
    from ._models import get_db
    from ._runs_state_cache import get_global_runs_state

    if run_finished:
        changes["run_time"] = time.monotonic() - initial_time

    db = get_db()
    for k, v in changes.items():
        setattr(run, k, v)
    fields_changed = tuple(changes.keys())
    with db.transaction():
        db.update(run, *fields_changed)

    # Ok, transaction finished properly. Let's update our in-memory cache.
    global_runs_state = get_global_runs_state()
    global_runs_state.on_run_changed(run, changes)


def _set_run_as_finished_ok(run: "Run", result: str, initial_time: float):
    from ._models import RunStatus

    _update_run(run, initial_time, True, result=result, status=RunStatus.PASSED)


def _set_run_as_finished_failed(run: "Run", error_message: str, initial_time: float):
    from ._models import RunStatus

    _update_run(
        run, initial_time, True, status=RunStatus.FAILED, error_message=error_message
    )


def _set_run_as_running(run: "Run", initial_time: float):
    from ._models import RunStatus

    _update_run(run, initial_time, False, status=RunStatus.RUNNING)


def _run_action_in_thread(
    action: "Action",
    signature: inspect.Signature,
    headers: Dict[str, str],
    *args,
    **kwargs,
):
    """
    This is where the user actually runs something.

    This runs in a thread (so, be careful when talking to the database).

    We have to take care of making a run with the proper environment,
    creating the run, collecting output info, etc.
    """
    from robocorp.action_server._gen_ids import gen_uuid
    from robocorp.action_server._settings import get_settings

    from ._actions_process_pool import get_actions_process_pool
    from ._models import Run, get_db

    settings = get_settings()
    ret_type = kwargs.pop("__ret_type__", "")
    if not ret_type:
        ret_type = "string"

    db = get_db()
    with db.connect():  # Connection is per-thread, so, we need to create a new one.
        inputs = {}
        if args or kwargs:
            bound = signature.bind(*args, **kwargs)

            for k, v in bound.arguments.items():
                inputs[k] = v

        expected_return_type = _spec_api_type_to_python_type.get(ret_type)
        if not expected_return_type:
            raise RuntimeError(
                f"The return type in the spec for the action {action.name} is not valid. Found: {ret_type}."
            )

        actions_process_pool = get_actions_process_pool()
        reuse_process = settings.reuse_processes

        with actions_process_pool.obtain_process_for_action(action) as process_handle:
            run_id = gen_uuid("run")
            relative_artifacts_path: str = _create_run_artifacts_dir(action, run_id)
            run: Run = _create_run(action, run_id, inputs, relative_artifacts_path)

            input_json = (
                settings.artifacts_dir
                / relative_artifacts_path
                / "__action_server_inputs.json"
            )
            input_json.write_text(json.dumps(inputs))

            robot_artifacts = settings.artifacts_dir / relative_artifacts_path

            result_json = (
                settings.artifacts_dir
                / relative_artifacts_path
                / "__action_server_result.json"
            )

            output_file = (
                settings.artifacts_dir
                / relative_artifacts_path
                / "__action_server_output.txt"
            )

            initial_time = time.monotonic()
            try:
                _set_run_as_running(run, initial_time)
                returncode = process_handle.run_action(
                    action,
                    input_json,
                    robot_artifacts,
                    output_file,
                    result_json,
                    headers,
                    reuse_process,
                )

                if returncode == 0:
                    try:
                        result: str = result_json.read_text("utf-8", "replace")
                    except Exception:
                        raise RuntimeError(
                            "It was not possible to collect the contents of the "
                            "result (json not created)."
                        )
                    try:
                        _set_run_as_finished_ok(run, result, initial_time)
                        ret = json.loads(result)
                    except Exception:
                        raise RuntimeError(
                            "Error loading the contents of {result_json} as json."
                        )
                    else:
                        if not isinstance(ret, expected_return_type):
                            raise RuntimeError(
                                f"Error in action. Expected return type: {ret_type}. Found return type: {type(ret)} (value: {ret})."
                            )
                        return ret

                raise RuntimeError(
                    f"Error: the process did not complete successfully when "
                    f"running. returncode: {returncode}"
                )

            except BaseException as e:
                _set_run_as_finished_failed(run, str(e), initial_time)
                raise HTTPException(status_code=500, detail=str(e))


def _name_as_class_name(name):
    return name.replace("_", " ").title().replace(" ", "")


def generate_func_from_action(action: "Action"):
    """
    This function generates a method from the given action.

    def method(
        name: Annotated[str, Param(description="This is the name")],
        title: Annotated[str, Param(description="This is the title")] = None,
    ) -> int:
        pass

    class MethodInput(BaseModel):
        name: Annotated[str, Param(description="This is the name")]
        title: Annotated[str, Param(description="This is the title")] = None

    def method(
        args: MethodInput
    ) -> int:
        return 1
    """
    input_schema_dict = json.loads(action.input_schema)
    output_schema_dict = json.loads(action.output_schema)
    properties = input_schema_dict.get("properties", {})
    arguments = []
    argument_names = []
    for param_name, param_data in properties.items():
        desc = param_data.get("description", "")
        argument_names.append(f"args.{param_name}")
        param_type = param_data.get("type", "string")

        argument = f"""
    {param_name}: Annotated[{_spec_api_type_to_python_type_str[param_type]}, 
        Param(description={desc!r})]"""
        if "default" in param_data:
            default = param_data.get("default")
            argument = f"{argument}={default!r}"
        arguments.append(argument)

    # Note: Headers are explicitly hidden from spec to make the OpenAPI schema compatible with OpenAI
    headers = {
        "x_action_trace": "Optional[str] = Header(None, description='Client application run trace reference', alias='X-action-trace', include_in_schema=False)"
    }
    headers_as_params = [f"{key}: {value}" for key, value in headers.items()]
    headers_as_values = [f"'{key}': {key}" for key, _ in headers.items()]

    ret_type = output_schema_dict.get("type", "")
    ret = ""
    if ret_type:
        ret_desc = output_schema_dict.get("description")
        ret = f"""-> Annotated[{_spec_api_type_to_python_type_str[ret_type]}, 
        Param(description={ret_desc!r})]"""
    argument_names.append(f"__ret_type__={ret_type!r}")

    code = f"""
class {_name_as_class_name(action.name)}Input(BaseModel):
    pass
{''.join(arguments)}
    
def {action.name}_as_params({', '.join(arguments)}){ret}:
    pass

def {action.name}(args:{_name_as_class_name(action.name)}Input, {", ".join(headers_as_params)}){ret}:
    headers = {{{", ".join(headers_as_values)}}}
    return _run_action_in_thread(action, signature, headers, {', '.join(argument_names)})

signature = inspect.signature({action.name}_as_params)
"""

    compiled = compile(code, "<string>", "exec")
    ctx: dict = {
        "Annotated": Annotated,
        "Param": Param,
        "Header": Header,
        "BaseModel": BaseModel,
        "Optional": Optional,
        "action": action,
        "inspect": inspect,
        "_run_action_in_thread": _run_action_in_thread,
    }
    exec(compiled, ctx)
    method = ctx[action.name]
    return method
