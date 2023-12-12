import json
import logging
import os
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path
from subprocess import CalledProcessError, TimeoutExpired
from typing import Dict, Iterator, List, Optional

from robocorp.action_server._protocols import ActionResult, RCCActionResult, Sentinel
from robocorp.action_server._robo_utils.constants import NULL

log = logging.getLogger(__name__)


def create_hash(contents: str) -> str:
    import hashlib

    sha256_hash = hashlib.sha256()
    sha256_hash.update(contents.encode("utf-8"))
    return sha256_hash.hexdigest()


RCC_CLOUD_ROBOT_MUTEX_NAME = "rcc_cloud_activity"
RCC_CREDENTIALS_MUTEX_NAME = "rcc_credentials"


class EnvInfo(object):
    def __init__(self, env: Dict[str, str]):
        self.env = env


def as_str(s) -> str:
    if isinstance(s, bytes):
        return s.decode("utf-8", "replace")
    return str(s)


class Rcc(object):
    def __init__(self, rcc_location: Path, robocorp_home: Path):
        self._rcc_location = rcc_location
        self._robocorp_home = robocorp_home

    def _run_rcc(
        self,
        args: List[str],
        timeout: float = 35,
        error_msg: str = "",
        mutex_name=None,
        cwd: Optional[str] = None,
        log_errors=True,
        stderr=Sentinel.SENTINEL,
        show_interactive_output: bool = False,
        hide_in_log: Optional[str] = None,
    ) -> RCCActionResult:
        """
        Returns an ActionResult where the result is the stdout of the executed command.

        :param log_errors:
            If false, errors won't be logged (i.e.: should be false when errors
            are expected).

        :param stderr:
            If given sets the stderr redirection (by default it's subprocess.PIPE,
            but users could change it to something as subprocess.STDOUT).
        """
        from subprocess import check_output, list2cmdline

        from robocorp.action_server._robo_utils.process import (
            build_subprocess_kwargs,
            check_output_interactive,
        )

        if stderr is Sentinel.SENTINEL:
            stderr = subprocess.PIPE

        rcc_location = str(self._rcc_location)

        env = os.environ.copy()
        env.pop("PYTHONPATH", "")
        env.pop("PYTHONHOME", "")
        env.pop("VIRTUAL_ENV", "")
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"

        robocorp_home = env["ROBOCORP_HOME"] = str(self._robocorp_home)

        kwargs: dict = build_subprocess_kwargs(cwd, env, stderr=stderr)
        args = [rcc_location] + args + ["--controller", "ActionServer"]
        cmdline = list2cmdline([str(x) for x in args])

        try:
            if mutex_name:
                from ._robo_utils.system_mutex import timed_acquire_mutex
            else:
                timed_acquire_mutex = NULL
            with timed_acquire_mutex(mutex_name, timeout=15):
                if logging.root.level <= logging.DEBUG:
                    msg = f"Running: {cmdline}"
                    if hide_in_log:
                        msg = msg.replace(hide_in_log, "<HIDDEN_IN_LOG>")

                    log.debug(msg)

                curtime = time.monotonic()

                boutput: bytes
                # We have 2 main modes here: one in which we can print the output
                # interactively while the command is running and another where
                # we only print if some error happened.
                if not show_interactive_output:
                    boutput = check_output(args, timeout=timeout, **kwargs)
                else:

                    def on_output(content):
                        try:
                            sys.stderr.buffer.write(content)
                        except BaseException:
                            log.exception("Error reporting interactive output.")

                    boutput = check_output_interactive(
                        args,
                        timeout=timeout,
                        on_stderr=on_output,
                        on_stdout=on_output,
                        **kwargs,
                    )

        except CalledProcessError as e:
            stdout = as_str(e.stdout)
            stderr = as_str(e.stderr)
            msg = (
                f"Error running: {cmdline}.\nROBOCORP_HOME: {robocorp_home}\n\n"
                f"Stdout: {stdout}\nStderr: {stderr}"
            )
            if hide_in_log:
                msg = msg.replace(hide_in_log, "<HIDDEN_IN_LOG>")

            if log_errors:
                log.exception(msg)
            if not error_msg:
                return RCCActionResult(cmdline, success=False, message=msg)
            else:
                additional_info = [error_msg]
                if stdout or stderr:
                    if stdout and stderr:
                        additional_info.append("\nDetails: ")
                        additional_info.append("\nStdout")
                        additional_info.append(stdout)
                        additional_info.append("\nStderr")
                        additional_info.append(stderr)

                    elif stdout:
                        additional_info.append("\nDetails: ")
                        additional_info.append(stdout)

                    elif stderr:
                        additional_info.append("\nDetails: ")
                        additional_info.append(stderr)

                return RCCActionResult(
                    cmdline, success=False, message="".join(additional_info)
                )

        except TimeoutExpired:
            msg = f"Timed out ({timeout}s elapsed) when running: {cmdline}"
            log.exception(msg)
            return RCCActionResult(cmdline, success=False, message=msg)

        except Exception:
            msg = f"Error running: {cmdline}"
            log.exception(msg)
            return RCCActionResult(cmdline, success=False, message=msg)

        output = boutput.decode("utf-8", "replace")

        do_log_as_info = (
            log_errors and logging.root.level <= logging.INFO
        ) or logging.root.level <= logging.DEBUG

        if do_log_as_info:
            elapsed = time.monotonic() - curtime
            msg = f"Output from: {cmdline} (took: {elapsed:.2f}s): {output}"
            if hide_in_log:
                msg = msg.replace(hide_in_log, "<HIDDEN_IN_LOG>")
            log.info(msg)

        return RCCActionResult(cmdline, success=True, message=None, result=output)

    def create_env_and_get_vars(
        self, conda_yaml: Path, conda_hash: str
    ) -> ActionResult[EnvInfo]:
        args = [
            "holotree",
            "variables",
            "--space",
            conda_hash,
            str(conda_yaml),
        ]
        args.append("--json")
        timeout = 60 * 60  # Wait up to 1 hour for the env...
        ret = self._run_rcc(
            args,
            mutex_name=RCC_CLOUD_ROBOT_MUTEX_NAME,
            cwd=str(conda_yaml.parent),
            timeout=timeout,  # Creating the env may be really slow!
            show_interactive_output=True,
        )

        def return_failure(msg: Optional[str]) -> ActionResult[EnvInfo]:
            log.critical(
                (
                    "Unable to create environment from:\n%s\n"
                    "To recreate the environment, please change the related conda yaml"
                    "\nor restart VSCode to retry with the same conda yaml contents."
                ),
                conda_yaml,
            )

            if not msg:
                msg = "<unknown reason>"
            log.critical(msg)
            action_result: ActionResult[EnvInfo] = ActionResult(False, msg, None)
            return action_result

        if not ret.success:
            return return_failure(ret.message)

        contents: Optional[str] = ret.result
        if not contents:
            return return_failure("Unable to get output when getting environment.")

        environ = {}
        for entry in json.loads(contents):
            key = str(entry["key"])
            value = str(entry["value"])
            if key:
                environ[key] = value

        if "CONDA_PREFIX" not in environ:
            msg = f"Did not find CONDA_PREFIX in {environ}"
            return return_failure(msg)

        if "PYTHON_EXE" not in environ:
            msg = f"Did not find PYTHON_EXE in {environ}"
            return return_failure(msg)

        return ActionResult(True, None, EnvInfo(environ))

    def pull(self, url: str, directory: str) -> ActionResult[str]:
        args = ["pull", url, "--directory", directory]
        ret = self._run_rcc(args, mutex_name=RCC_CLOUD_ROBOT_MUTEX_NAME)
        if not ret.success:
            return ActionResult(False, ret.message, None)
        return ActionResult(True, None, ret.result)


_rcc: Optional["Rcc"] = None


@contextmanager
def initialize_rcc(rcc_location: Path, robocorp_home: Path) -> Iterator[Rcc]:
    global _rcc

    rcc = Rcc(rcc_location, robocorp_home)
    _rcc = rcc
    try:
        yield rcc
    finally:
        _rcc = None


def get_rcc() -> Rcc:
    assert _rcc is not None, "RCC not initialized"
    return _rcc
