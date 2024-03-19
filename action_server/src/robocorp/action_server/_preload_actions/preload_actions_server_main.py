"""
This module can be used to run the actions in a way that the actions are pre-loaded
(i.e.: imported) but no actions are actually run until requested by the action-server.

Important: this will run in the target environment and can't really import anything
from the action server.
"""
import argparse
import os
import sys
import traceback
from typing import Any, Dict

DEFAULT_TIMEOUT = 10
NO_TIMEOUT = None
USE_TIMEOUTS = True


class _DummyStdin(object):
    def __init__(self, original_stdin=sys.stdin, *args, **kwargs):
        try:
            self.encoding = sys.stdin.encoding
        except Exception:
            # Not sure if it's available in all Python versions...
            pass
        self.original_stdin = original_stdin

        try:
            self.errors = (
                sys.stdin.errors
            )  # Who knew? sys streams have an errors attribute!
        except Exception:
            # Not sure if it's available in all Python versions...
            pass

    def readline(self, *args, **kwargs):
        return "\n"

    def read(self, *args, **kwargs):
        return self.readline()

    def write(self, *args, **kwargs):
        pass

    def flush(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass


def binary_stdio():
    stdin, stdout = sys.stdin.buffer, sys.stdout.buffer

    # The original stdin cannot be used and anything written to stdout will
    # be put in the stderr.
    sys.stdin, sys.stdout = (_DummyStdin(), sys.stderr)

    return stdin, stdout


def socket_connect(host, port):
    import socket as socket_module

    s = socket_module.socket(socket_module.AF_INET, socket_module.SOCK_STREAM)

    #  Set TCP keepalive on an open socket.
    #  It activates after 1 second (TCP_KEEPIDLE,) of idleness,
    #  then sends a keepalive ping once every 3 seconds (TCP_KEEPINTVL),
    #  and closes the connection after 5 failed ping (TCP_KEEPCNT), or 15 seconds
    try:
        s.setsockopt(socket_module.SOL_SOCKET, socket_module.SO_KEEPALIVE, 1)
    except (AttributeError, OSError):
        pass  # May not be available everywhere.
    try:
        s.setsockopt(socket_module.IPPROTO_TCP, socket_module.TCP_KEEPIDLE, 1)
    except (AttributeError, OSError):
        pass  # May not be available everywhere.
    try:
        s.setsockopt(socket_module.IPPROTO_TCP, socket_module.TCP_KEEPINTVL, 3)
    except (AttributeError, OSError):
        pass  # May not be available everywhere.
    try:
        s.setsockopt(socket_module.IPPROTO_TCP, socket_module.TCP_KEEPCNT, 5)
    except (AttributeError, OSError):
        pass  # May not be available everywhere.

    try:
        # 10 seconds default timeout
        s.settimeout(DEFAULT_TIMEOUT if USE_TIMEOUTS else NO_TIMEOUT)
        s.connect((host, port))
        s.settimeout(None)  # no timeout after connected
    except Exception:
        raise RuntimeError("Could not connect to %s: %s", host, port)

    rfile = s.makefile("rb")
    wfile = s.makefile("wb")
    return rfile, wfile


def add_arguments(parser):
    parser.description = "Preload action-server actions"

    parser.add_argument(
        "--tcp", action="store_true", help="Use TCP server instead of stdio"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Bind to this address")
    parser.add_argument("--port", default=-1, type=int, help="Bind to this port")


class MessagesHandler:
    def __init__(self, read_stream, write_stream):
        try:
            from preload_actions_streams import (  # type: ignore
                JsonRpcStreamReaderThread,
                JsonRpcStreamWriter,
            )
        except ImportError:
            from .preload_actions_streams import (
                JsonRpcStreamReaderThread,
                JsonRpcStreamWriter,
            )

        from queue import Queue

        self._readqueue = Queue()
        self._jsonrpc_stream_reader = JsonRpcStreamReaderThread(
            read_stream, self._readqueue, self._on_message
        )
        self._jsonrpc_stream_writer = JsonRpcStreamWriter(write_stream)

    def start(self):
        self._jsonrpc_stream_reader.start()

        # Removed for now: this messes up the logging because
        # by the time the imports are done it's important that the
        # needed scaffolding to collect the log contents is in place.
        #
        # import io
        # from contextlib import redirect_stderr, redirect_stdout
        # Collect actions so that it's ready to go when requested.
        # s = io.StringIO()
        # try:
        #     from robocorp.actions import cli
        #
        #     with redirect_stdout(s), redirect_stderr(s):
        #         cli.main(["list"], exit=False)
        # except BaseException:
        #     print(s.getvalue())
        #     traceback.print_exc()

        while True:
            msg = self._readqueue.get()
            self._on_message(msg)

    def _on_message(self, message):
        # Original command line is something as:
        # python = get_python_exe_from_env(env)
        # cmdline: List[str] = [
        #     python,
        #     "-m",
        #     "robocorp.actions",
        #     "run",
        #     "--preload-module",
        #     "preload_actions",
        #     "-a",
        #     action.name,
        # ]
        #
        # cmdline.append(str(action.file))
        # cmdline.append(f"--json-input={input_json}")

        # Some things must be set in the environment for the run:
        #
        # env["ROBOT_ARTIFACTS"] = robot_artifacts
        # env["RC_ACTION_RESULT_LOCATION"] = result_json
        command = message.get("command")
        if command == "run_action":
            from robocorp.actions import cli

            returncode = 1
            try:
                action_name = message["action_name"]
                action_file = message["action_file"]
                input_json = message["input_json"]
                robot_artifacts = message["robot_artifacts"]
                result_json = message["result_json"]
                headers = message["headers"]
                cookies = message["cookies"]
                reuse_process = message["reuse_process"]

                os.environ["ROBOT_ARTIFACTS"] = robot_artifacts
                os.environ["RC_ACTION_RESULT_LOCATION"] = result_json

                if reuse_process:
                    # Setup is skipped (for callbacks which still haven't been
                    # executed)
                    os.environ["RC_TASKS_SKIP_SESSION_SETUP"] = "1"

                    # Teardown is skipped (for all callbacks).
                    os.environ["RC_TASKS_SKIP_SESSION_TEARDOWN"] = "1"
                else:
                    os.environ.pop("RC_TASKS_SKIP_SESSION_TEARDOWN", None)
                    os.environ.pop("RC_TASKS_SKIP_SESSION_SETUP", None)

                if headers:
                    for key, value in headers.items():
                        if key and value and key.upper() == "X_ACTION_TRACE":
                            os.environ[key.upper()] = value

                # The preloaded actions must be always in place.
                sys.modules.pop("preload_actions", None)
                args = [
                    "run",
                    "--preload-module",
                    "preload_actions",
                    "-a",
                    action_name,
                    action_file,
                    f"--json-input={input_json}",
                ]

                returncode = cli.main(
                    args,
                    exit=False,
                    **self._plugin_manager_kwargs(
                        {"request": {"headers": headers, "cookies": cookies}}
                    ),
                )
            except BaseException:
                traceback.print_exc()

            finally:
                self._jsonrpc_stream_writer.write({"returncode": returncode})

    def _plugin_manager_kwargs(self, managed_parameters) -> Dict[str, Any]:
        try:
            from robocorp.actions._managed_parameters import ManagedParameters
            from robocorp.actions._request import Request
            from robocorp.tasks._customization._extension_points import (
                EPManagedParameters,
            )
            from robocorp.tasks._customization._plugin_manager import PluginManager

        except ImportError:
            return {}

        # Ok, we're dealing with a newer version of robocorp.actions and
        # robocorp.tasks, so add the customization of parameters to
        # add the 'request' parameter.

        try:
            pm = getattr(self, "_pm")
        except AttributeError:
            pm = self._pm = PluginManager()
        pm.set_instance(
            EPManagedParameters,
            ManagedParameters(
                {"request": Request.model_validate(managed_parameters["request"])}
            ),
        )

        return {"plugin_manager": pm}


def main(args=None):
    original_args = args if args is not None else sys.argv[1:]

    parser = argparse.ArgumentParser()
    add_arguments(parser)

    args = parser.parse_args(args=original_args)

    if args.tcp:
        rfile, wfile = socket_connect(args.host, args.port)
    else:
        rfile, wfile = binary_stdio()

    server = MessagesHandler(rfile, wfile)
    server.start()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Critical error (the logging may not be set up properly).
        traceback.print_exc()
