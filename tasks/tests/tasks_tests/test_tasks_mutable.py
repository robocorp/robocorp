def test_tasks_mutable(datadir) -> None:
    from devutils.fixtures import robocorp_tasks_run

    result = robocorp_tasks_run(
        ["run", "--console-colors=plain"],
        returncode=0,
        cwd=str(datadir),
    )

    stdout = result.stdout.decode("utf-8")
    assert "Something went wrong" in stdout
    assert "division by zero" in stdout
