import json
from pathlib import Path


def check(datadir, args, msg="", returncode=1):
    from devutils.fixtures import robocorp_tasks_run

    result = robocorp_tasks_run(
        ["run", "--console-colors=plain"] + args,
        returncode=returncode,
        cwd=str(datadir),
    )

    stdout = result.stdout.decode("utf-8")
    if returncode:
        assert (
            msg
        ), f'When an error is expected, the "msg" must be given. Found stdout: {stdout}'

    assert msg in stdout, f"{msg}\nnot in\n{stdout}"


def test_tasks_arguments_json_input(datadir, tmpdir) -> None:
    json_input = Path(tmpdir / "my.json")
    json_input.write_text(json.dumps({"s": "1"}))

    check(datadir, ["-t=accept_str", f"--json-input={json_input}"], returncode=0)

    json_input = Path(tmpdir / "my.json")
    json_input.write_text(json.dumps({"s": 1}))

    check(
        datadir,
        ["-t=accept_str", f"--json-input={json_input}"],
        "Error. Expected the parameter: `s` to be of type: str. Found type: int.",
        returncode=1,
    )


def test_tasks_unicode(datadir) -> None:
    check(datadir, ["-t=unicode_ação_Σ", "--", "--ação=1"], returncode=0)


def test_tasks_custom_data(datadir) -> None:
    custom = json.dumps(
        {
            "name": "foo",
            "price": 22,
            "is_offer": None,
        }
    )
    check(datadir, ["-t=custom_data", "--", f"--data={custom}"], returncode=0)


def test_tasks_custom_bad_data(datadir) -> None:
    check(
        datadir,
        ["-t=custom_data", "--", "--data={error}"],
        returncode=1,
        msg="(error interpreting contents for data as a json)",
    )


def test_tasks_arguments(datadir) -> None:
    check(datadir, ["-t=accept_str", "--", "--s=1"], returncode=0)

    check(
        datadir,
        ["-t=return_tuple"],
        "It's not possible to call: 'return_tuple' because the passed arguments don't match the expected signature.",
    )

    check(
        datadir,
        ["-t=return_tuple", "--", "a=2"],
        "It's not possible to call: 'return_tuple' because the passed arguments don't match the expected signature.",
    )
    check(
        datadir,
        ["-t=return_tuple", "--", "a=2"],
        "Error: the following arguments are required: --a, --b.",
    )

    check(
        datadir,
        ["-t=return_tuple", "--", "--a", "a", "--b", "a"],
        "argument --b: invalid int value: 'a'.",
        returncode=1,
    )

    # This works.
    check(datadir, ["-t=return_tuple", "--", "--a", "2", "--b", "3"], returncode=0)

    check(
        datadir,
        ["-t=something_else", "--", "--f=a,b"],
        "Error. The param type 'list' in 'something_else' is not supported. Supported parameter types: str, int, float, bool",
        returncode=1,
    )
    check(
        datadir,
        ["-t=bool_true", "--", "--b=true"],
        returncode=0,
    )
    check(
        datadir,
        ["-t=bool_true", "--", "--b=1"],
        returncode=0,
    )
    check(
        datadir,
        ["-t=bool_true", "--", "--b=True"],
        returncode=0,
    )
    check(
        datadir,
        ["-t=bool_false", "--", "--b=false"],
        returncode=0,
    )
    check(
        datadir,
        ["-t=bool_false", "--", "--b=0"],
        returncode=0,
    )
    check(
        datadir,
        ["-t=bool_false", "--", "--b=False"],
        returncode=0,
    )
    check(
        datadir,
        ["-t=bool_false", "--", "--b=invalid"],
        "Error: argument --b: Invalid value for boolean flag: invalid.",
        returncode=1,
    )
