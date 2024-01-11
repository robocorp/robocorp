import argparse
import logging
import os.path
import sys
from pathlib import Path
from typing import Optional, Union

from robocorp.action_server._robo_utils.auth import generate_api_key

from . import __version__

log = logging.getLogger(__name__)


# def _write_schema(path: Optional[str]):
#     from fastapi.openapi.utils import get_openapi
#     from ._app import get_app
#     app = get_app()
#     schema = get_openapi(
#         title=app.title,
#         version=app.version,
#         openapi_version=app.openapi_version,
#         description=app.description,
#         routes=app.routes,
#     )
#
#     if path is None:
#         print(json.dumps(schema, indent=4))
#     else:
#         output = Path(path)
#         output.parent.mkdir(parents=True, exist_ok=True)
#         with open(output, "w", encoding="utf-8") as file:
#             json.dump(schema, file, indent=4)


def _add_data_args(parser, defaults):
    parser.add_argument(
        "-d",
        "--datadir",
        metavar="PATH",
        default="",
        help=(
            "Directory to store the data for operating the actions server "
            "(by default a datadir will be generated based on the current directory)."
        ),
    )
    parser.add_argument(
        "--db-file",
        help=(
            "The name of the database file, relative to the datadir "
            "(default: %(default)s)"
        ),
        default=defaults["db_file"],
    )


def _add_verbose_args(parser, defaults):
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Be more talkative (default: %(default)s)",
    )


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def _create_parser():
    from ._settings import Settings

    defaults = Settings.defaults()
    base_parser = argparse.ArgumentParser(
        prog="action-server",
        description="Robocorp Action Server",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = base_parser.add_subparsers(dest="command")

    # Starts the server
    start_parser = subparsers.add_parser(
        "start",
        help=(
            "Starts the Robocorp Action Server (importing the actions in the "
            "current directory by default)."
        ),
    )

    start_parser.add_argument(
        "-a",
        "--address",
        default=defaults["address"],
        help="Server address (default: %(default)s)",
    )
    start_parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=defaults["port"],
        help="Server port (default: %(default)s)",
    )
    start_parser.add_argument(
        "--expose",
        action="store_true",
        help="Expose the server to the world",
    )
    start_parser.add_argument(
        "--expose-allow-reuse",
        dest="expose_allow_reuse",
        action="store_true",
        help="Always answer yes to expose reuse confirmation",
    )
    start_parser.add_argument(
        "--api-key",
        dest="api_key",
        help=(
            'Adds authentication. Pass it as `{"Authorization": "Bearer <API_KEY>"}` '
            "header. Pass `--api-key None` to disable authentication."
        ),
        default=None,
    )
    start_parser.add_argument(
        "--actions-sync",
        type=str2bool,
        help=(
            "By default the actions will be synchronized (added/removed) given the "
            "directories provided (if not specified the current directory is used). To "
            "start without synchronizing it's possible to use `--actions-sync=false`"
        ),
        default=True,
    )
    start_parser.add_argument(
        "--dir",
        metavar="PATH",
        help="By default, when starting, actions will be collected from the current "
        "directory to serve, but it's also possible to use `--dir` to load actions "
        "from a different directory",
        action="append",
    )

    _add_data_args(start_parser, defaults)
    _add_verbose_args(start_parser, defaults)

    # Import
    import_parser = subparsers.add_parser(
        "import",
        help="Imports an Action Package and exits",
    )

    import_parser.add_argument(
        "--dir",
        metavar="PATH",
        help="Can be used to import an action package from the local filesystem",
        action="append",
    )

    _add_data_args(import_parser, defaults)
    _add_verbose_args(import_parser, defaults)

    # Download RCC
    rcc_parser = subparsers.add_parser(
        "download-rcc",
        help=(
            "Downloads RCC (by default to the location required by the "
            "Robocorp Action Server)"
        ),
    )

    rcc_parser.add_argument(
        "--file",
        metavar="PATH",
        help="Target file to where RCC should be downloaded",
        nargs="?",
    )

    # New project from template
    new_parser = subparsers.add_parser(
        "new",
        help="Bootstrap new project from template",
    )
    new_parser.add_argument(
        "--name",
        help="Name for the project",
    )
    _add_data_args(new_parser, defaults)
    _add_verbose_args(new_parser, defaults)

    # Schema
    # schema_parser = subparsers.add_parser(
    #     "schema",
    #     help="Prints the schema and exits",
    # )
    #
    # schema_parser.add_argument(
    #     "--file",
    #     metavar="PATH",
    #     help=(
    #         "Write openapi.json schema and exit (if path is given the schema "
    #         "is written to that file instead of stdout)"
    #     ),
    #     nargs="?",
    # )

    # Version
    subparsers.add_parser(
        "version",
        help="Prints the version and exits",
    )

    # Migration
    migration_parser = subparsers.add_parser(
        "migrate",
        help="Makes a database migration (if needed) and exits",
    )
    _add_data_args(migration_parser, defaults)
    _add_verbose_args(migration_parser, defaults)

    return base_parser


def main(args: Optional[list[str]] = None, *, exit=True) -> int:
    if args is None:
        args = sys.argv[1:]

    if not args:
        if os.environ.get(
            "RC_ACTION_SERVER_FORCE_DOWNLOAD_RCC", ""
        ).strip().lower() in (
            "1",
            "true",
        ):
            print(
                "As RC_ACTION_SERVER_FORCE_DOWNLOAD_RCC is set and no arguments were "
                "passed, rcc will be downloaded."
            )

            from robocorp.action_server._download_rcc import download_rcc

            download_rcc(force=True)

        if os.environ.get("RC_ACTION_SERVER_DO_SELFTEST", "").strip().lower() in (
            "1",
            "true",
        ):
            from . import _selftest

            print(
                "As RC_ACTION_SERVER_DO_SELFTEST is set and no arguments were passed, "
                "a selftest will be run."
            )

            sys.exit(_selftest.do_selftest())

    retcode = _main_retcode(args, exit=exit)
    if exit:
        sys.exit(retcode)
    return retcode


def _setup_stdout_logging(log_level):
    from logging import StreamHandler

    stream_handler = StreamHandler()
    stream_handler.setLevel(log_level)
    if log_level == logging.DEBUG:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="[%Y-%m-%d %H:%M:%S]"
        )
    else:
        formatter = logging.Formatter("%(message)s", datefmt="[%X]")

    stream_handler.setFormatter(formatter)
    logger = logging.root
    logger.addHandler(stream_handler)


def _setup_logging(datadir: Path, log_level):
    from logging.handlers import RotatingFileHandler

    log_file = str(datadir / "server_log.txt")
    log.info(f"Logs may be found at: {log_file}.")
    rotating_handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    rotating_handler.setLevel(log_level)
    rotating_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s", datefmt="[%Y-%m-%d %H:%M:%S]"
        )
    )
    logger = logging.root
    logger.addHandler(rotating_handler)


def _main_retcode(args: Optional[list[str]], exit) -> int:
    from ._download_rcc import download_rcc
    from ._rcc import initialize_rcc
    from ._robo_utils.system_mutex import SystemMutex
    from ._runs_state_cache import use_runs_state_ctx

    if args is None:
        args = sys.argv[1:]

    if args and args[0] == "server-expose":
        # The process is being called by to make the server expose.
        # Internal usage only, so, don't even do argument parsing
        # for it.
        from . import _server_expose

        _server_expose.main(*args[1:])
        return 0

    parser = _create_parser()
    base_args = parser.parse_args(args)

    command = base_args.command
    if not command:
        parser.print_help()
        return 0

    if command == "version":
        print(__version__)
        return 0

    # if command == "schema":
    # This doesn't work at this point because we have to register the
    # actions first for it to work.
    #     file = base_args.file
    #     _write_schema(file)
    #     return

    if command == "download-rcc":
        download_rcc(target=base_args.file, force=True)
        return 0

    if command not in (
        "migrate",
        "import",
        "start",
        "new",
    ):
        print(f"Unexpected command: {command}.", file=sys.stderr)
        return 1

    # Log to stdout.
    log_level = logging.DEBUG if base_args.verbose else logging.INFO

    logger = logging.root
    logger.setLevel(log_level)

    _setup_stdout_logging(log_level)

    from ._settings import setup_settings

    with setup_settings(base_args) as settings:
        settings.datadir.mkdir(parents=True, exist_ok=True)
        robocorp_home = settings.datadir / ".robocorp_home"
        robocorp_home.mkdir(parents=True, exist_ok=True)

        with initialize_rcc(download_rcc(force=False), robocorp_home):
            if command == "new":
                from ._new_project import create_new_project

                create_new_project(directory=base_args.name)
                return 0

            mutex = SystemMutex("action_server.lock", base_dir=str(settings.datadir))
            if not mutex.get_mutex_aquired():
                print(
                    f"An action server is already started in this datadir ({settings.datadir})."
                    f"\nPlease exit it before starting a new one."
                    f"\nInformation on mutex holder:\n"
                    f"{mutex.mutex_creation_info}",
                    file=sys.stderr,
                )
                return 1

            # Log to file in datadir, always in debug mode
            # (only after lock is in place as multiple loggers to the same
            # file would be troublesome).
            _setup_logging(settings.datadir, log_level)

            try:
                db_path: Union[Path, str]
                if settings.db_file != ":memory:":
                    db_path = settings.datadir / settings.db_file
                else:
                    db_path = settings.db_file

                from robocorp.action_server._models import create_db, load_db
                from robocorp.action_server.migrations import (
                    db_migration_pending,
                    migrate_db,
                )

                is_new = db_path == ":memory:" or not os.path.exists(db_path)

                if is_new:
                    log.info(
                        "Database file does not exist. Creating it at: %s", db_path
                    )
                    use_db_ctx = create_db
                else:
                    use_db_ctx = load_db

                if command == "migrate":
                    if db_path == ":memory:":
                        print(
                            "Cannot do migration of in-memory databases",
                            file=sys.stderr,
                        )
                        return 1
                    if not migrate_db(db_path):
                        return 1
                    return 0
                else:
                    if not is_new and db_migration_pending(db_path):
                        print(
                            f"""It was not possible to start the server because a 
database migration is required to use with this version of the
Robocorp Action Server.

Please run the command:

python -m robocorp.action_server migrate

To migrate the database to the current version
-- or start from scratch by erasing the file: 
{db_path}
"""
                        )
                        return 1

                with use_db_ctx(db_path) as db:
                    from . import _actions_import

                    if command == "import":
                        if not base_args.dir:
                            base_args.dir = ["."]

                        for action_package_dir in base_args.dir:
                            _actions_import.import_action_package(
                                settings.datadir, os.path.abspath(action_package_dir)
                            )
                        return 0

                    elif command == "start":
                        # start imports the current directory by default
                        # (unless --actions-sync=false is specified).
                        log.info("Synchronize actions: %s", base_args.actions_sync)

                        if base_args.actions_sync:
                            if not base_args.dir:
                                base_args.dir = ["."]

                            for action_package_dir in base_args.dir:
                                _actions_import.import_action_package(
                                    settings.datadir,
                                    os.path.abspath(action_package_dir),
                                    disable_not_imported=base_args.actions_sync,
                                )

                        with use_runs_state_ctx(db):
                            from ._server import start_server

                            settings.artifacts_dir.mkdir(parents=True, exist_ok=True)

                            expose_session = None
                            if base_args.expose:
                                from ._server_expose import read_expose_session_json

                                expose_session = read_expose_session_json(
                                    datadir=str(settings.datadir)
                                )
                                if expose_session and not base_args.expose_allow_reuse:
                                    confirm = input(
                                        f"Resume previous expose URL {expose_session.url} Y/N? [Y] "
                                    )
                                    if confirm.lower() == "y" or confirm == "":
                                        log.debug("Resuming previous expose session")
                                    else:
                                        expose_session = None

                            api_key = base_args.api_key
                            if api_key is None:
                                # reuse the previously exposed api key
                                if expose_session and expose_session.api_key:
                                    api_key = expose_session.api_key
                                else:
                                    api_key = generate_api_key()

                            start_server(
                                expose=base_args.expose,
                                api_key=api_key,
                                expose_session=expose_session.expose_session
                                if expose_session
                                else None,
                            )
                            return 0

                    else:
                        print(f"Unexpected command: {command}.", file=sys.stderr)
                        return 1
            finally:
                mutex.release_mutex()


if __name__ == "__main__":
    main()
