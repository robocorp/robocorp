from pathlib import Path
import sys
from invoke import task
import os

# Add the devutils even if the poetry env isn't setup (to do a 'inv devinstall').
try:
    import devutils
except ImportError:
    devutils_src = Path(__file__).absolute().parent.parent / "devutils" / "src"
    assert devutils_src.exists(), f"{devutils_src} does not exist."
    sys.path.append(str(devutils_src))

from devutils.invoke_utils import build_common_tasks

globals().update(build_common_tasks(Path(__file__).absolute().parent, "robocorp.tasks"))

try:
    from robocorp import tasks
except ImportError:
    # I.e.: add relative path (the cwd must be the directory containing this file).
    sys.path.append("src")
    from robocorp import tasks

__file__ = os.path.abspath(__file__)


def get_tag():
    import subprocess

    # i.e.: Gets the last tagged version
    cmd = "git describe --tags --abbrev=0 --match robocorp-tasks*".split()
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = popen.communicate()

    # Something as: b'robocorp-tasks-0.0.1'
    return stdout.decode("utf-8").strip()


def get_all_tags():
    import subprocess

    cmd = "git tag".split()
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = popen.communicate()

    found = stdout.decode("utf-8").strip()
    return [x for x in found.splitlines() if "robocorp-tasks" in x]


@task
def check_tag_version(ctx):
    """
    Checks if the current tag matches the latest version (exits with 1 if it
    does not match and with 0 if it does match).
    """
    tag = get_tag()
    version = tag[tag.rfind("-") + 1 :]

    if tasks.__version__ == version:
        sys.stderr.write("Version matches (%s) (exit(0))\n" % (version,))
        sys.exit(0)
    else:
        sys.stderr.write(
            "Version does not match (robocorp-tasks: %s != repo tag: %s).\nTags:%s\n(exit(1))\n"
            % (tasks.__version__, version, get_all_tags())
        )
        sys.exit(1)


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


def _fix_robocorp_tasks_contents_version_in_poetry(contents, version):
    import re

    contents = re.sub(
        r"(robocorp-tasks\s*=\s*)\"\^?\d+\.\d+\.\d+", r'\1"^%s' % (version,), contents
    )
    return contents


@task
def set_version(ctx, version):
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
    update_version(
        version, browser_poetry, _fix_robocorp_tasks_contents_version_in_poetry
    )
