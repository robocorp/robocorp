import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from subprocess import CalledProcessError, TimeoutExpired
from typing import Any, Generic, List, Optional, TypedDict, TypeVar, Protocol

log = logging.getLogger(__name__)

ACCOUNT_NAME = "devutils-tests"


def build_subprocess_kwargs(cwd, env, **kwargs) -> dict:
    startupinfo = None
    if sys.platform == "win32":
        # We don't want to show the shell on windows!
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        startupinfo = startupinfo

    if cwd:
        kwargs["cwd"] = cwd
    if env:
        kwargs["env"] = env
    kwargs["startupinfo"] = startupinfo
    return kwargs


_SENTINEL = object()

T = TypeVar("T")
Y = TypeVar("Y", covariant=True)


class AuthorizeTokenDict(TypedDict):
    token: str
    endpoint: str


class IRccWorkspace(Protocol):
    @property
    def workspace_id(self) -> str:
        pass

    @property
    def workspace_name(self) -> str:
        pass

    @property
    def organization_name(self) -> str:
        pass


class RccWorkspace(object):
    def __init__(self, workspace_id: str, workspace_name: str, organization_name: str):
        self._workspace_id = workspace_id
        self._workspace_name = workspace_name
        self._organization_name = organization_name

    @property
    def workspace_id(self) -> str:
        return self._workspace_id

    @property
    def workspace_name(self) -> str:
        return self._workspace_name

    @property
    def organization_name(self) -> str:
        return self._organization_name


@dataclass
class AccountInfo:
    account: str
    identifier: str
    email: str
    fullname: str


class ActionResultDict(TypedDict):
    success: bool
    message: Optional[
        str
    ]  # if success == False, this can be some message to show to the user
    result: Any


class ActionResult(Generic[T]):
    success: bool
    message: Optional[
        str
    ]  # if success == False, this can be some message to show to the user
    result: Optional[T]

    def __init__(
        self, success: bool, message: Optional[str] = None, result: Optional[T] = None
    ):
        self.success = success
        self.message = message
        self.result = result

    def as_dict(self) -> ActionResultDict:
        return {"success": self.success, "message": self.message, "result": self.result}

    def __str__(self):
        return f"ActionResult(success={self.success!r}, message={self.message!r}, result={self.result!r})"

    __repr__ = __str__


class RCCActionResult(ActionResult[str]):
    # A string-representation of the command line.
    command_line: str

    def __init__(
        self,
        command_line: str,
        success: bool,
        message: Optional[str] = None,
        result: Optional[str] = None,
    ):
        ActionResult.__init__(self, success, message, result)
        self.command_line = command_line


class Rcc(object):
    """
    A wrapper (adapted from Robocorp Code) which can be used to manage RCC in tests.
    """

    def __init__(self, rcc_location: str, robocorp_home: str, endpoint: str) -> None:
        self.rcc_location = rcc_location
        self.robocorp_home = robocorp_home
        self.config_location = ""
        self.endpoint = endpoint
        self._last_verified_account_info: Optional[AccountInfo] = None

    def _run_rcc(
        self,
        args: List[str],
        timeout: float = 35,
        error_msg: str = "",
        cwd: Optional[str] = None,
        log_errors=True,
        stderr=_SENTINEL,
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
        from subprocess import check_output
        from subprocess import list2cmdline

        if stderr is _SENTINEL:
            stderr = subprocess.PIPE

        rcc_location = self.rcc_location

        env = os.environ.copy()
        env.pop("PYTHONPATH", "")
        env.pop("PYTHONHOME", "")
        env.pop("VIRTUAL_ENV", "")
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUNBUFFERED"] = "1"

        robocorp_home = self.robocorp_home
        if robocorp_home:
            env["ROBOCORP_HOME"] = robocorp_home

        kwargs: dict = build_subprocess_kwargs(cwd, env, stderr=stderr)
        args = [rcc_location] + args + ["--controller", "RobocorpDevutilsTests"]
        cmdline = list2cmdline([str(x) for x in args])

        try:
            msg = f"Running: {cmdline}"
            if hide_in_log:
                msg = msg.replace(hide_in_log, "<HIDDEN_IN_LOG>")

            log.debug(msg)

            curtime = time.time()
            boutput: bytes
            # We have 2 main modes here: one in which we can print the output
            # interactively while the command is running and another where
            # we only print if some error happened.
            boutput = check_output(args, timeout=timeout, **kwargs)

        except CalledProcessError as e:
            stdout = e.stdout.decode("utf-8", "replace")
            stderr = e.stderr.decode("utf-8", "replace")
            msg = f"Error running: {cmdline}.\nROBOCORP_HOME: {robocorp_home}\n\nStdout: {stdout}\nStderr: {stderr}"
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

        elapsed = time.time() - curtime
        msg = f"Output from: {cmdline} (took: {elapsed:.2f}s): {output}"
        if hide_in_log:
            msg = msg.replace(hide_in_log, "<HIDDEN_IN_LOG>")
        log.info(msg)

        return RCCActionResult(cmdline, success=True, message=None, result=output)

    def _add_config_to_args(self, args: List[str]) -> List[str]:
        config_location = self.config_location
        if config_location:
            args.append("--config")
            args.append(config_location)
        return args

    def add_credentials(self, credential: str) -> ActionResult:
        self._last_verified_account_info = None
        args = ["config", "credentials"]
        endpoint = self.endpoint
        if endpoint:
            args.append("--endpoint")
            args.append(endpoint)

        args = self._add_config_to_args(args)
        args.append("--account")
        args.append(ACCOUNT_NAME)

        args.append(credential)

        return self._run_rcc(args, hide_in_log=credential)

    def credentials_valid(self) -> bool:
        account = self.get_valid_account_info()
        return account is not None

    def get_valid_account_info(self) -> Optional[AccountInfo]:
        self._last_verified_account_info = None
        args = [
            "config",
            "credentials",
            "-j",
            "--verified",
            # Note: it doesn't really filter in this case, so, filter it
            # manually afterwards.
            # "--account",
            # ACCOUNT_NAME,
        ]
        endpoint = self.endpoint
        if endpoint:
            args.append("--endpoint")
            args.append(endpoint)

        args = self._add_config_to_args(args)

        result = self._run_rcc(args)
        if not result.success:
            msg = f"Error checking credentials: {result.message}"
            log.critical(msg)
            return None

        output = result.result
        if not output:
            msg = f"Error. Expected to get info on credentials (found no output)."
            log.critical(msg)
            return None

        try:
            credentials = json.loads(output)
            credentials = [
                credential
                for credential in credentials
                if credential.get("account", "").lower() == ACCOUNT_NAME
            ]

            for credential in credentials:
                timestamp = credential.get("verified")
                if timestamp and int(timestamp):
                    details = credential.get("details", {})
                    if not isinstance(details, dict):
                        email = "<Email:Unknown>"
                        fullname = "<Name: Unknown>"
                    else:
                        email = str(details.get("email", "<Email: Unknown>"))
                        fullname = (
                            f'{details.get("first_name")} {details.get("last_name")}'
                        )

                    account = self._last_verified_account_info = AccountInfo(
                        credential["account"], credential["identifier"], email, fullname
                    )

                    return account
        except:
            log.exception("Error loading credentials from: %s", output)

        # Found no valid credential
        return None

    def _add_account_to_args(self, args: List[str]) -> Optional[ActionResult]:
        """
        Adds the account to the args.

        Returns an error ActionResult if unable to get a valid account.
        """
        account_info = self._last_verified_account_info
        if account_info is None:
            account_info = self.get_valid_account_info()
            if account_info is None:
                return ActionResult(False, "Unable to get valid account for action.")

        args.append("--account")
        args.append(account_info.account)
        return None

    def cloud_authorize_token(
        self, workspace_id, timeout=15, graceperiod=15
    ) -> ActionResult[AuthorizeTokenDict]:
        args = ["cloud", "authorize"]

        args = self._add_config_to_args(args)

        args.append("--workspace")
        args.append(workspace_id)

        args.append("--minutes")
        args.append(f"{round(timeout)}")

        args.append("--graceperiod")
        args.append(f"{round(graceperiod)}")

        error_action_result = self._add_account_to_args(args)
        if error_action_result is not None:
            return error_action_result

        result = self._run_rcc(args, log_errors=False)

        if not result.success:
            return ActionResult(False, result.message)

        output = result.result
        if not output:
            return ActionResult(
                False, "Error in cloud authorize (output not available)."
            )

        try:
            as_dict = json.loads(output)
        except Exception:
            msg = "Unable to load json from cloud authorize."
            log.exception(msg)
            return ActionResult(False, msg)
        else:
            return ActionResult(
                True, None, {"token": as_dict["token"], "endpoint": as_dict["endpoint"]}
            )

    def cloud_list_workspaces(self) -> ActionResult[List[IRccWorkspace]]:
        ret: List[IRccWorkspace] = []
        args = ["cloud", "workspace"]
        args = self._add_config_to_args(args)
        error_action_result = self._add_account_to_args(args)
        if error_action_result is not None:
            return error_action_result

        result = self._run_rcc(args)

        if not result.success:
            return ActionResult(False, result.message)

        output = result.result
        if not output:
            return ActionResult(
                False, "Error listing Control Room workspaces (output not available)."
            )

        try:
            lst = json.loads(output)
        except Exception as e:
            log.exception(f"Error parsing json: {output}")
            return ActionResult(
                False,
                f"Error loading json obtained while listing Control Room workspaces.\n{e}",
            )
        for workspace_info in lst:
            permissions = workspace_info.get("permissions")
            if isinstance(permissions, dict):
                if not permissions.get("canReadRobots"):
                    log.info(
                        "Skipped workspace: %s (no canReadRobots permissions).",
                        workspace_info,
                    )
                    continue

            ret.append(
                RccWorkspace(
                    workspace_id=workspace_info["id"],
                    workspace_name=workspace_info["name"],
                    organization_name=workspace_info.get(
                        "orgName", "<Unable to get organization name>"
                    ),
                )
            )
        return ActionResult(True, None, ret)
