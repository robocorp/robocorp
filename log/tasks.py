import os
from pathlib import Path
import subprocess
import sys

from invoke import task

# Add the devutils even if the poetry env isn't setup (to do a 'inv devinstall').
try:
    import devutils
except ImportError:
    devutils_src = Path(__file__).absolute().parent.parent / "devutils" / "src"
    assert devutils_src.exists(), f"{devutils_src} does not exist."
    sys.path.append(str(devutils_src))


from devutils.invoke_utils import build_common_tasks


globals().update(build_common_tasks(Path(__file__).absolute().parent, "robocorp.log"))

try:
    from robocorp import log
except ImportError:
    # I.e.: add relative path (the cwd must be the directory containing this file).
    sys.path.append("src")
    from robocorp import log

__file__ = os.path.abspath(__file__)

try:
    from robocorp import log
except ImportError:
    # I.e.: add relative path (the cwd must be the directory containing this file).
    sys.path.append("src")
    from robocorp import log


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
        r"(robocorp-log\s*=\s*)\"\^?\d+\.\d+\.\d+", r'\1"%s' % (version,), contents
    )
    return contents


def set_version(version):
    """
    Sets a new version for robocorp-log in all the needed files.
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
    update_version(version, os.path.join(".", "src", "robocorp", "log", "__init__.py"))
    logging_dir = Path(__file__).absolute().parent
    tasks_poetry = logging_dir.parent / "tasks" / "pyproject.toml"
    update_version(version, tasks_poetry, _fix_contents_version_in_poetry)


def get_tag():
    import subprocess

    # i.e.: Gets the last tagged version
    cmd = "git describe --tags --abbrev=0 --match robocorp-log*".split()
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = popen.communicate()

    # Something as: b'robocorp-log-0.0.1'
    return stdout.decode("utf-8").strip()


def get_all_tags():
    import subprocess

    # i.e.: Gets the last tagged version
    cmd = "git tag".split()
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    stdout, stderr = popen.communicate()

    return stdout.decode("utf-8").strip()


@task
def check_tag_version(ctx):
    """
    Checks if the current tag matches the latest version (exits with 1 if it
    does not match and with 0 if it does match).
    """
    tag = get_tag()
    version = tag[tag.rfind("-") + 1 :]

    if log.__version__ == version:
        sys.stderr.write("Version matches (%s) (exit(0))\n" % (version,))
        sys.exit(0)
    else:
        sys.stderr.write(
            "Version does not match (robocorp-log: %s != repo tag: %s).\nTags:%s\n(exit(1))\n"
            % (log.__version__, version, get_all_tags())
        )
        sys.exit(1)


@task
def check_no_git_changes(ctx):
    output = (
        subprocess.check_output(["git", "status", "-s"])
        .decode("utf-8", "replace")
        .strip()
    )
    if output:
        sys.stderr.write(f"Expected no changes in git. Found:\n{output}\n")
        subprocess.call(["git", "diff"])
        sys.exit(1)


@task
def build_output_view(ctx, dev=False, version=None):
    """
    Builds the output view in prod mode in `dist`.
    """
    import shutil
    import subprocess

    src_webview = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "output-webview",
        )
    )
    print("=== Yarn install")
    shell = sys.platform == "win32"
    subprocess.check_call(["yarn", "install"], cwd=src_webview, shell=shell)

    print("=== Building with webpack")

    if dev:
        print("=== Building dev mode")
    else:
        print("=== Building production mode")

    versions = [1, 2]
    if version:
        if isinstance(version, int):
            versions = [version]
        else:
            assert isinstance(version, (list, tuple))
            versions = version
            for el in versions:
                assert isinstance(el, int)

    for v in versions:
        assert v in (1, 2), f"Unexpected version: {v}"
        vtag = "" if v == 1 else "_v2"
        subprocess.check_call(
            ["yarn", ("build-prod" if not dev else "build-dev")]
            + ([] if v == 1 else ["--env", "v2"]),
            cwd=src_webview,
            shell=shell,
        )

        index_in_dist = os.path.join(src_webview, f"dist{vtag}", "index.html")
        assert os.path.exists(index_in_dist)

        # Now, let's embed the contents of the index.html into a python
        # module where it can be saved accordingly.

        index_in_src = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "src",
                "robocorp",
                "log",
                f"_index{vtag}.py",
            )
        )

        file_contents = {}

        dist_dirname = os.path.dirname(index_in_dist)
        for filename in os.listdir(dist_dirname):
            with open(os.path.join(dist_dirname, filename), encoding="utf-8") as stream:
                file_contents[filename] = stream.read()

        assert "index.html" in file_contents

        with open(index_in_src, "w", encoding="utf-8") as stream:
            stream.write(
                f"""# coding: utf-8
# Note: autogenerated file.
# To regenerate this file use: inv build-output-view.

# The FILE_CONTENTS contains the contents of the files with
# html/javascript code which can be used to visualize the contents of the
# output generated by robocorp-log (i.e.: the .log files).

FILE_CONTENTS = {repr(file_contents)}
"""
            )
