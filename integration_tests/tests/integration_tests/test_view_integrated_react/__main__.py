# This is a helper file so that we can run scripts directly without robo and without
# any IDE customization.
#
# Important: this file could be used in clients, but it cannot import any library
# code as such code would then not be logged properly.

from pathlib import Path

if __name__ == "__main__":
    from robocorp.tasks import cli

    target = Path(__file__).absolute().parent / "tasks.py"
    cases = [
        "case_generators",
        "case_failure",
        "case_task_and_element",
        "case_log",
        "case_search",
        "case_big_structures",
    ]

    cli.main(["run", str(target)] + [f"-t={c}" for c in cases], exit=True)
