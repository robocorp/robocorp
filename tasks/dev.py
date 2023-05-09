"""
This is a script to help with the automation of common development tasks.

It requires 'fire' to be installed for the command line automation (i.e.: pip install fire).

Some example commands:

    python -m dev set-version 0.0.2
    python -m dev check-tag-version
"""
import sys
import os
import traceback
import subprocess
from pathlib import Path

__file__ = os.path.abspath(__file__)

if not os.path.exists(os.path.join(os.path.abspath("."), "dev.py")):
    raise RuntimeError('Please execute commands from the directory containing "dev.py"')

import fire


try:
    from robocorp import tasks
except ImportError:
    # I.e.: add relative path (the cwd must be the directory containing this file).
    sys.path.append("src")
    from robocorp import tasks


def _fix_contents_version(contents, version):
    import re

    contents = re.sub(
        r"(version\s*=\s*)\"\d+\.\d+\.\d+", r'\1"%s' % (version,), contents
    )
    contents = re.sub(
        r"(__version__\s*=\s*)\"\d+\.\d+\.\d+", r'\1"%s' % (version,), contents
    )
    contents = re.sub(
        r"(\"version\"\s*:\s*)\"\d+\.\d+\.\d+", r'\1"%s' % (version,), contents
    )

    return contents


def _fix_contents_version_in_poetry(contents, version):
    import re

    contents = re.sub(
        r"(robocorp-tasks\s*=\s*)\"\^?\d+\.\d+\.\d+", r'\1"^%s' % (version,), contents
    )
    return contents


class Dev(object):
    def set_version(self, version):
        """
        Sets a new version for robocorp-tasks in all the needed files.
        """

        def update_version(version, filepath, fix_func=_fix_contents_version):
            with open(filepath, "r") as stream:
                contents = stream.read()

            new_contents = fix_func(contents, version)
            if contents != new_contents:
                print("Changed: ", filepath)
                with open(filepath, "w") as stream:
                    stream.write(new_contents)

        update_version(version, "pyproject.toml")
        update_version(
            version, os.path.join(".", "src", "robocorp", "tasks", "__init__.py")
        )
        tasks_dir = Path(__file__).absolute().parent
        browser_poetry = tasks_dir.parent / "browser" / "pyproject.toml"
        update_version(version, browser_poetry, _fix_contents_version_in_poetry)

    def get_tag(self):
        import subprocess

        # i.e.: Gets the last tagged version
        cmd = "git describe --tags --abbrev=0 --match robocorp-tasks*".split()
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout, stderr = popen.communicate()

        # Something as: b'robocorp-tasks-0.0.1'
        return stdout.decode("utf-8").strip()

    def get_all_tags(self):
        import subprocess

        # i.e.: Gets the last tagged version
        cmd = "git tag".split()
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout, stderr = popen.communicate()

        return stdout.decode("utf-8").strip()

    def check_tag_version(self):
        """
        Checks if the current tag matches the latest version (exits with 1 if it
        does not match and with 0 if it does match).
        """
        tag = self.get_tag()
        version = tag[tag.rfind("-") + 1 :]

        if tasks.__version__ == version:
            sys.stderr.write("Version matches (%s) (exit(0))\n" % (version,))
            sys.exit(0)
        else:
            sys.stderr.write(
                "Version does not match (robocorp-tasks: %s != repo tag: %s).\nTags:%s\n(exit(1))\n"
                % (tasks.__version__, version, self.get_all_tags())
            )
            sys.exit(1)


if __name__ == "__main__":
    # Workaround so that fire always prints the output.
    # See: https://github.com/google/python-fire/issues/188
    def Display(lines, out):
        text = "\n".join(lines) + "\n"
        out.write(text)

    from fire import core

    core.Display = Display

    fire.Fire(Dev())
