import datetime
import json

from robocorp.action_server._database import datetime_to_str
from robocorp.action_server._models import Action, ActionPackage, Run, RunStatus

ACTION_PACKAGE = ActionPackage(
    id="ap-001-e8efd343-ccd5-470c-84bf-a32b9752e324",
    name="greeter",
    directory="C:/temp/greeter",
    conda_hash="7c7a3dc1af2ba64fd30b9512f8e9c44405f57be8b609de9859173bf55f28b943",
    env_json='{"PYTHON_EXE": "c:/temp/python.exe"}',
)


ACTION = Action(
    id="act-001-bed9c7fd-9615-4bbe-a59a-5f35cb1c0f11",
    action_package_id=ACTION_PACKAGE.id,
    name="greet",
    docs="Provides a greeting for a person.",
    file="greeter_task.py",
    lineno=4,
    input_schema=(
        '{"additionalProperties": false, '
        '"properties": {"name": '
        '{"type": "string", '
        '"description": "The name of the person to greet.", '
        '"title": "Name"},'
        '"title": {"type": "string", '
        '"description": "The title for the persor (Mr., Mrs., ...).", '
        '"title": "Title", '
        '"default": "Mr."}}, "type": "object", "required": ["name"]}'
    ),
    output_schema='{"type": "string", "description": "The greeting for the person."}',
)

RUN = Run(
    id="run-001-usanoth-uosnthuo-uneothu-usneoth",
    status=RunStatus.NOT_RUN,
    action_id=ACTION.id,
    start_time=datetime_to_str(
        datetime.datetime(2023, 11, 25, tzinfo=datetime.timezone.utc)
    ),
    run_time=None,
    inputs=json.dumps({"name": "foo", "title": "Mr."}),
    result=json.dumps("Hello Mr. foo."),
    error_message=None,
    relative_artifacts_dir="run-001-usanoth-uosnthuo-uneothu-usneoth",
)

RUN2 = Run(
    id="run-002-usanoth-uosnthuo-uneothu-usneoth",
    status=RunStatus.NOT_RUN,
    action_id=ACTION.id,
    start_time=datetime_to_str(
        datetime.datetime(2023, 11, 26, tzinfo=datetime.timezone.utc)
    ),
    run_time=None,
    inputs=json.dumps({"name": "bar", "title": "Mr."}),
    result=json.dumps("Hello Mr. bar."),
    error_message=None,
    relative_artifacts_dir="run-001-usanoth-uosnthuo-uneothu-usneoth",
)
