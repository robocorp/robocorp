import json

from robocorp.action_server._selftest import ActionServerClient, ActionServerProcess


def test_issue_167_access_headers(
    action_server_process: ActionServerProcess,
    client: ActionServerClient,
):
    from action_server_tests.fixtures import get_in_resources

    pack = get_in_resources("no_conda", "check_headers")
    action_server_process.start(
        cwd=pack,
        actions_sync=True,
        db_file="server.db",
    )

    found = client.post_get_str(
        "api/actions/check-headers/check-headers/run",
        {"name": "Foo"},
        headers={"header1": "value-header1"},
        cookies=dict(cookie1="foo", cookie2="bar"),
    )
    found = json.loads(json.loads(found))
    assert "cookies" in found
    assert "headers" in found

    headers = found["headers"]
    assert headers["HEADER1"] == "value-header1"

    cookies = found["cookies"]
    assert cookies == dict(COOKIE1="foo", COOKIE2="bar")
