import os

import pytest


@pytest.mark.parametrize("kill", ["", "before-teardown", "after-teardown"])
def test_force_early_exit_cmdline(pyfile, kill):
    from devutils.fixtures import robocorp_tasks_run

    @pyfile
    def check():
        from robocorp.tasks import session_cache, task

        @task
        def my_task():
            import sys

            sys.stderr.write("Executed\n")
            import atexit

            @session_cache
            def my_cache():
                yield
                sys.stderr.write("my_cache_teardown\n")
                sys.stderr.flush()

            my_cache()

            def write_on_exit():
                sys.stderr.write("atexit_executed\n")
                sys.stderr.flush()

            atexit.register(write_on_exit)

    cmdline = ["run", check]
    if kill:
        cmdline.append(f"--os-exit={kill}")

    result = robocorp_tasks_run(cmdline, returncode=0, cwd=os.path.dirname(check))
    stderr = result.stderr.decode("utf-8")

    assert stderr.count("Executed") == 1
    if kill:
        assert stderr.count("atexit_executed") == 0, f"Found stderr: {stderr}"

        if kill == "before-teardown":
            assert "my_cache_teardown" not in stderr
        else:
            assert "my_cache_teardown" in stderr
    else:
        assert stderr.count("atexit_executed") == 1


@pytest.mark.parametrize("kill", ["", "before-teardown", "after-teardown"])
def test_force_early_exit(pyfile, kill):
    from devutils.fixtures import robocorp_tasks_run

    @pyfile
    def check():
        from robocorp.tasks import session_cache, task

        @task
        def my_task():
            import sys

            sys.stderr.write("Executed\n")
            import atexit

            @session_cache
            def my_cache():
                yield
                sys.stderr.write("my_cache_teardown\n")
                sys.stderr.flush()

            my_cache()

            def write_on_exit():
                sys.stderr.write("atexit_executed\n")
                sys.stderr.flush()

            atexit.register(write_on_exit)

    env = dict(RC_OS_EXIT=kill)
    result = robocorp_tasks_run(
        ["run", check], returncode=0, cwd=os.path.dirname(check), additional_env=env
    )
    stderr = result.stderr.decode("utf-8")

    assert stderr.count("Executed") == 1
    if kill:
        assert stderr.count("atexit_executed") == 0, f"Found stderr: {stderr}"

        if kill == "before-teardown":
            assert "my_cache_teardown" not in stderr
        else:
            assert "my_cache_teardown" in stderr
    else:
        assert stderr.count("atexit_executed") == 1


@pytest.mark.parametrize("kill", ["", "after-teardown"])
def test_force_early_exit_with_error(pyfile, kill):
    from devutils.fixtures import robocorp_tasks_run

    @pyfile
    def check():
        from robocorp.tasks import task

        @task
        def my_task():
            import sys

            sys.stderr.write("Executed\n")
            import atexit

            def write_on_exit():
                sys.stderr.write("atexit_executed\n")
                sys.stderr.flush()

            atexit.register(write_on_exit)
            raise RuntimeError("Something bad happened (retcode should be 1)")

    env = dict(RC_OS_EXIT=kill)
    result = robocorp_tasks_run(
        ["run", check], returncode=1, cwd=os.path.dirname(check), additional_env=env
    )
    stderr = result.stderr.decode("utf-8")

    assert stderr.count("Executed") == 1
    if kill:
        assert stderr.count("atexit_executed") == 0, f"Found stderr: {stderr}"
    else:
        assert stderr.count("atexit_executed") == 1


@pytest.mark.parametrize("kill", ["", "after-teardown"])
def test_force_early_exit_kills_subprocesses(pyfile, kill):
    from devutils.fixtures import robocorp_tasks_run

    @pyfile
    def check():
        from robocorp.tasks import task

        @task
        def my_task():
            import subprocess
            import sys
            import textwrap

            code = textwrap.dedent(
                """
            import time
            while True:
                print('.')
                time.sleep(1)
            """
            )
            process = subprocess.Popen([sys.executable, "-c", code])

            sys.stderr.write("Executed\n")
            import atexit

            print(f"pid:{process.pid}")

            def write_on_exit():
                sys.stderr.write("atexit_executed\n")
                sys.stderr.flush()
                process.terminate()

            atexit.register(write_on_exit)

    env = dict(RC_OS_EXIT=kill)
    result = robocorp_tasks_run(
        ["run", check], returncode=0, cwd=os.path.dirname(check), additional_env=env
    )
    stderr = result.stderr.decode("utf-8")
    assert stderr.count("Executed") == 1
    if kill:
        assert stderr.count("atexit_executed") == 0, f"Found stderr: {stderr}"
    else:
        assert stderr.count("atexit_executed") == 1
