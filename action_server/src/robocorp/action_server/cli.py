import argparse
import logging
import sys
from pathlib import Path
from typing import Union

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

    return base_parser


def main() -> None:
    from ._rcc import initialize_rcc

    parser = _create_parser()
    base_args = parser.parse_args()

    command = base_args.command
    if not command:
        parser.print_help()
        return

    if command == "version":
        print(__version__)
        return

    # if command == "schema":
    # This doesn't work at this point because we have to register the
    # actions first for it to work, so, the server needs
    # the routes to be registered
    #     file = base_args.file
    #     _write_schema(file)
    #     return

    if command == "download-rcc":
        from . import _download_rcc

        _download_rcc.download_rcc(target=base_args.file)
        return

    if command not in (
        "import",
        "start",
    ):
        raise RuntimeError(f"Unexpected command: {command}.")

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

    from ._models import initialize_db

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

    with initialize_db(db_path), initialize_rcc(rcc_location, robocorp_home):
        if command == "import":
            from . import _actions_import

            for action_package_dir in base_args.dir:
                _actions_import.import_action_package(
                    settings.datadir, action_package_dir
                )
            return

        if command == "start":
            from ._server import start_server

            settings.artifacts_dir.mkdir(parents=True, exist_ok=True)
            start_server()
            return


if __name__ == "__main__":
    main()
