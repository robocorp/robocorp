import os
import sys

import pytest


@pytest.fixture(scope="session")
def examples_dir():
    from pathlib import Path

    examples = Path(__file__).parent.parent.parent.parent / "examples"

    assert examples.exists()
    return examples


def robo_run(cmdline, returncode, cwd=None, additional_env=None):
    import subprocess

    cp = os.environ.copy()
    cp["PYTHONPATH"] = os.pathsep.join([x for x in sys.path if x])
    if additional_env:
        cp.update(additional_env)
    args = [sys.executable, "-m", "robocorp.tasks"] + cmdline
    result = subprocess.run(args, capture_output=True, env=cp, cwd=cwd)
    if result.returncode != returncode:
        env_str = "\n".join(str(x) for x in sorted(cp.items()))

        raise AssertionError(
            f"""Expected returncode: {returncode}. Found: {result.returncode}.
=== stdout:
{result.stdout.decode('utf-8')}

=== stderr:
{result.stderr.decode('utf-8')}

=== Env:
{env_str}

=== Args:
{args}

"""
        )
    return result


@pytest.fixture(scope="session")
def rcc_loc(tmpdir_factory):
    import subprocess
    from pathlib import Path

    dirname = tmpdir_factory.mktemp("rcc_dir")
    location = os.path.join(str(dirname), "rcc")

    if sys.platform == "win32":
        location += ".exe"

    _download_rcc(location, force=False)
    assert os.path.exists(location)

    # Disable tracking for tests
    subprocess.check_call([location] + "configure identity --do-not-track".split())
    return Path(location)


def _download_rcc(location: str, force: bool = False) -> None:
    """
    Downloads rcc to the given location. Note that we don't overwrite it if it
    already exists (unless force == True).

    :param location:
        The location to store the rcc executable in the filesystem.
    :param force:
        Whether we should overwrite an existing installation.
    """

    if not os.path.exists(location) or force:
        if not os.path.exists(location) or force:
            import platform
            import urllib.request

            machine = platform.machine()
            is_64 = not machine or "64" in machine

            if sys.platform == "win32":
                if is_64:
                    relative_path = "/windows64/rcc.exe"
                else:
                    relative_path = "/windows32/rcc.exe"

            elif sys.platform == "darwin":
                relative_path = "/macos64/rcc"

            else:
                if is_64:
                    relative_path = "/linux64/rcc"
                else:
                    relative_path = "/linux32/rcc"

            RCC_VERSION = "v13.5.5"
            prefix = f"https://downloads.robocorp.com/rcc/releases/{RCC_VERSION}"
            url = prefix + relative_path

            # log.info(f"Downloading rcc from: {url} to: {location}.")
            response = urllib.request.urlopen(url)

            # Put it all in memory before writing (i.e. just write it if
            # we know we downloaded everything).
            data = response.read()

            try:
                os.makedirs(os.path.dirname(location))
            except Exception:
                pass  # Error expected if the parent dir already exists.

            try:
                with open(location, "wb") as stream:
                    stream.write(data)
                os.chmod(location, 0x744)
            except Exception:
                sys.stderr.write(
                    f"Error writing to: {location}.\nParent dir exists: {os.path.exists(os.path.dirname(location))}\n"
                )
                raise
