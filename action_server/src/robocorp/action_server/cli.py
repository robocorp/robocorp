import argparse
import logging
import os.path
import sys
from pathlib import Path
from typing import Optional, Union

from robocorp.action_server._robo_utils.auth import generate_api_key

from . import __version__
from ._settings import Settings, get_settings

log = logging.getLogger(__name__)

CURDIR = Path(__file__).parent.absolute()


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
        default=defaults["datadir"],
        help=(
            "Directory to store the data for operating the actions server "
            "(default: %(default)s)"
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


def _create_parser():
    defaults = Settings.defaults()
    base_parser = argparse.ArgumentParser(
        description="Robocorp Action Server",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = base_parser.add_subparsers(dest="command")

    # Starts the server
    start_parser = subparsers.add_parser(
        "start",
        help="Starts the Robocorp Action Server",
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
        "--api-key",
        dest="api_key",
        help="""Adds authentication. Pass it as `{"Authorization": "Bearer <API_KEY>"}` header. 
        Pass `--api-key None` to disable authentication.""",
        default=generate_api_key(),
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


def main(args: Optional[list[str]] = None) -> int:
    from ._rcc import initialize_rcc
    from ._robo_utils.system_mutex import SystemMutex
    from ._runs_state_cache import use_runs_state_ctx

    if args is None:
        args = sys.argv[1:]
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
        from . import _download_rcc

        _download_rcc.download_rcc(target=base_args.file)
        return 0

    if command not in (
        "migrate",
        "import",
        "start",
    ):
        print(f"Unexpected command: {command}.", file=sys.stderr)
        return 1

    settings = get_settings()
    settings.from_args(base_args)

    settings.datadir.mkdir(parents=True, exist_ok=True)
    robocorp_home = settings.datadir / ".robocorp_home"
    robocorp_home.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG if settings.verbose else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
    )

    mutex = SystemMutex("action_server", base_dir=str(settings.datadir))
    if not mutex.get_mutex_aquired():
        print(
            f"An action server is already started in this datadir ({settings.datadir})."
            f"\nPlease exit it before starting a new one."
            f"\nInformation on mutex holder:\n"
            f"{mutex.mutex_creation_info}",
            file=sys.stderr,
        )
        return 1

    try:
        db_path: Union[Path, str]
        if settings.db_file != ":memory:":
            db_path = settings.datadir / settings.db_file
        else:
            db_path = settings.db_file

        if sys.platform == "win32":
            rcc_location = CURDIR / "bin" / "rcc.exe"
        else:
            rcc_location = CURDIR / "bin" / "rcc"

        if not rcc_location.exists():
            # Download RCC.
            log.info(f"RCC not available at: {rcc_location}. Downloading.")
            from . import _download_rcc  # noqa

            _download_rcc.download_rcc()

        from robocorp.action_server._models import create_db, load_db
        from robocorp.action_server.migrations import db_migration_pending, migrate_db

        is_new = db_path == ":memory:" or not os.path.exists(db_path)

        if is_new:
            log.info("Database file does not exist. Creating it at: %s", db_path)
            use_db_ctx = create_db
        else:
            use_db_ctx = load_db

        if command == "migrate":
            if db_path == ":memory:":
                print("Cannot do migration of in-memory databases", file=sys.stderr)
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

        with use_db_ctx(db_path) as db, initialize_rcc(rcc_location, robocorp_home):
            if command == "import":
                from . import _actions_import

                for action_package_dir in base_args.dir:
                    _actions_import.import_action_package(
                        settings.datadir, action_package_dir
                    )
                return 0

            elif command == "start":
                with use_runs_state_ctx(db):
                    from ._server import start_server

                    settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
                    start_server(expose=base_args.expose, api_key=base_args.api_key)
                    return 0

            else:
                print(f"Unexpected command: {command}.", file=sys.stderr)
                return 1
    finally:
        mutex.release_mutex()


if __name__ == "__main__":
    retcode = main()
    sys.exit(retcode)
