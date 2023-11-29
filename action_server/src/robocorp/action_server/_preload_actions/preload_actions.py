import json
import os

RC_ACTION_RESULT_LOCATION = os.environ.get("RC_ACTION_RESULT_LOCATION", "")

if RC_ACTION_RESULT_LOCATION:
    from pathlib import Path

    from robocorp.actions import IAction, teardown

    @teardown
    def on_teardown_save_result(action: IAction):
        result = action.result
        p = Path(RC_ACTION_RESULT_LOCATION)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(result))
