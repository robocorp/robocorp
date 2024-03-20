import json

from robocorp.action_server._selftest import ActionServerClient, ActionServerProcess


def test_server_custom_model_argument(
    action_server_process: ActionServerProcess,
    client: ActionServerClient,
    data_regression,
) -> None:
    from action_server_tests.fixtures import get_in_resources

    pack = get_in_resources("no_conda", "custom_model")
    action_server_process.start(
        cwd=pack,
        actions_sync=True,
        db_file="server.db",
    )

    openapi_json = client.get_openapi_json()
    spec = json.loads(openapi_json)
    # print(json.dumps(spec, indent=4))

    data_regression.check(spec)

    found = client.post_get_str(
        "api/actions/custom-model/my-action/run",
        {
            "x": "Foo",
            "data": {
                "name": "data-name",
                "price": 22,
                "is-offer": None,
                "depends_on": {"city": "Foo"},
            },
        },
    )
    assert json.loads(found) == {"accepted": True, "depends_on": {"city": "Foo"}}

    # Bad arguments
    client.post_error(
        "api/actions/custom-model/my-action/run",
        422,
        {"x": "Foo", "data": {"name": "data-name"}},  # Missing fields
    )
