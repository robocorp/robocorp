def test_fixture_module(datadir, str_regression):
    from devutils.fixtures import robocorp_tasks_run

    result = robocorp_tasks_run(
        [
            "run",
            "--console-colors=plain",
            "--preload-module=my_config",
            "--preload-module=my_config2",
        ],
        returncode=0,
        cwd=str(datadir),
    )

    stdout = result.stdout.decode("utf-8")
    found = []
    for line in stdout.splitlines(keepends=False):
        if "my_config" in line:
            found.append(line)
    str_regression.check("\n".join(found))
