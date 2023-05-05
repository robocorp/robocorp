# This is a helper file so that we can run scripts directly without robo and without
# any IDE customization.
#
# Important: this file could be used in clients, but it cannot import any library
# code as such code would then not be logged properly.

from pathlib import Path

if __name__ == "__main__":
    from robocorp.tasks import cli

    target = Path(__file__).absolute().parent / "tasks.py"

    cli.main(["run", str(target)], exit=True)
