import json
import os
from robocorp.log import html

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


X_ACTION_TRACE = os.environ.get("X_ACTION_TRACE", "")

if X_ACTION_TRACE:
    html(
        f'<p style="line-height:34px">External <a href="{X_ACTION_TRACE}"'
        'style="color:rgb(var(--color-content-accent))">Client Application Trace</a> reported</p>'
    )
