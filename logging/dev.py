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

__file__ = os.path.abspath(__file__)

if not os.path.exists(os.path.join(os.path.abspath("."), "dev.py")):
    raise RuntimeError('Please execute commands from the directory containing "dev.py"')

import fire


try:
    import robo_log
except ImportError:
    # I.e.: add relative path (the cwd must be the directory containing this file).
    sys.path.append("src")
    import robo_log


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
    contents = re.sub(
        r"(blob/robotframework-lsp)-\d+\.\d+\.\d+", r"\1-%s" % (version,), contents
    )

    return contents


class Dev(object):
    def set_version(self, version):
        """
        Sets a new version for robocorp-logging in all the needed files.
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
        update_version(version, os.path.join(".", "src", "robo_log", "__init__.py"))

    def get_tag(self):
        import subprocess

        # i.e.: Gets the last tagged version
        cmd = "git describe --tags --abbrev=0 --match robocorp-logging*".split()
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        stdout, stderr = popen.communicate()

        # Something as: b'robocorp-logging-0.0.1'
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

        if robo_log.__version__ == version:
            sys.stderr.write("Version matches (%s) (exit(0))\n" % (version,))
            sys.exit(0)
        else:
            sys.stderr.write(
                "Version does not match (robocorp-logging: %s != repo tag: %s).\nTags:%s\n(exit(1))\n"
                % (robo_log.__version__, version, self.get_all_tags())
            )
            sys.exit(1)

    def check_no_git_changes(self):
        output = (
            subprocess.check_output(["git", "status", "-s"])
            .decode("utf-8", "replace")
            .strip()
        )
        if output:
            sys.stderr.write(f"Expected no changes in git. Found:\n{output}\n")
            subprocess.call(["git", "diff"])
            sys.exit(1)

    def build_output_view(self, dev=False, version=None):
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
                    "robo_log",
                    f"index{vtag}.py",
                )
            )

            file_contents = {}

            dist_dirname = os.path.dirname(index_in_dist)
            for filename in os.listdir(dist_dirname):
                with open(
                    os.path.join(dist_dirname, filename), encoding="utf-8"
                ) as stream:
                    file_contents[filename] = stream.read()

            assert "index.html" in file_contents

            with open(index_in_src, "w", encoding="utf-8") as stream:
                stream.write(
                    f"""# coding: utf-8
# Note: autogenerated file.
# To regenerate this file use: python -m dev build-output-view.

# The FILE_CONTENTS contains the contents of the files with
# html/javascript code which can be used to visualize the contents of the
# output generated by robocorp-logging (i.e.: the .robolog files).

FILE_CONTENTS = {repr(file_contents)}
"""
                )


def test_lines():
    """
    Check that the replace matches what we expect.

    Things we must match:

        version="0.0.1"
        "version": "0.0.1",
        __version__ = "0.0.1"
        https://github.com/robocorp/robotframework-lsp/blob/robotframework-lsp-0.1.1/robotframework-ls/README.md
    """
    from robocorp_ls_core.unittest_tools.compare import compare_lines

    contents = _fix_contents_version(
        """
        version="0.0.198"
        version = "0.0.1"
        "version": "0.0.1",
        "version":"0.0.1",
        "version" :"0.0.1",
        __version__ = "0.0.1"
        https://github.com/robocorp/robotframework-lsp/blob/robotframework-lsp-0.1.1/robotframework-ls/README.md
        """,
        "3.7.1",
    )

    expected = """
        version="3.7.1"
        version = "3.7.1"
        "version": "3.7.1",
        "version":"3.7.1",
        "version" :"3.7.1",
        __version__ = "3.7.1"
        https://github.com/robocorp/robotframework-lsp/blob/robotframework-lsp-3.7.1/robotframework-ls/README.md
        """

    compare_lines(contents.splitlines(), expected.splitlines())


if __name__ == "__main__":
    TEST = False
    if TEST:
        test_lines()
    else:
        # Workaround so that fire always prints the output.
        # See: https://github.com/google/python-fire/issues/188
        def Display(lines, out):
            text = "\n".join(lines) + "\n"
            out.write(text)

        from fire import core

        core.Display = Display

        fire.Fire(Dev())
