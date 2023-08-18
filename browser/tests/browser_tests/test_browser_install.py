from devutils.fixtures import RobocorpTaskRunner


def test_playwright_browser_install(datadir, robocorp_task_runner: RobocorpTaskRunner):
    from robocorp.log import verify_log_messages_from_log_html

    robocorp_task_runner.run_tasks(
        ["run", "-t", "check_browser_install"], returncode=1, cwd=datadir
    )
    assert robocorp_task_runner.log_html
    verify_log_messages_from_log_html(
        robocorp_task_runner.log_html,
        [
            {
                "message_type": "STB",
                "message": "InstallError: Failed to install chrome\n"
                "Return code: 1\n"
                "Output: Output: 0\n"
                "Output: 1\n"
                "Output: 2\n"
                "Output: 3\n"
                "Output: 4\n"
                "Output: 5\n"
                "Output: 6\n"
                "Output: 7\n"
                "Output: 8\n"
                "Output: 9\n"
                "Output: 10\n"
                "Output: 11\n"
                "Output: 12\n",
            },
            {
                "message_type": "L",
                "level": "I",
                "__check__": lambda dct: dct["message"].startswith(
                    "Playwright browser install in process. Last output:"
                ),
            },
            {
                "message_type": "L",
                "level": "D",
                "message": "Output: 5",
            },
            {
                "message_type": "L",
                "level": "D",
                "message": "Output: 12",
            },
        ],
    )
