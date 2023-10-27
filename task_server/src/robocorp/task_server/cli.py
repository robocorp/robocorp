import argparse
import json
import logging
from pathlib import Path

from fastapi.openapi.utils import get_openapi
from rich.logging import RichHandler

from . import __version__
from ._app import get_app
from ._server import start_server
from ._settings import Settings, get_settings


def _write_schema(path: str):
    app = get_app()
    schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as file:
        json.dump(schema, file, indent=4)


def _create_parser():
    defaults = Settings.defaults()
    # fmt: off
    parser = argparse.ArgumentParser(
        description="Robocorp Task Server",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "tasks",
        nargs="?",
        default="tasks.py",
        help="tasks file (default: %(default)s)",
    )
    parser.add_argument(
        "-a", "--address",
        default=defaults["address"],
        help="server address (default: %(default)s)",
    )
    parser.add_argument(
        "-p", "--port",
        type=int,
        default=defaults["port"],
        help="server port (default: %(default)s)",
    )
    parser.add_argument(
        "-w", "--watch",
        action="store_true",
        default=False,
        help="hot-reload project code (default: %(default)s)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        default=False,
        help="be more talkative (default: %(default)s)",
    )
    parser.add_argument(
        "--schema",
        metavar="PATH",
        help="write schema to given file and exit",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="print the current version and exit"
    )
    # fmt: on
    return parser


def main():
    parser = _create_parser()
    args = parser.parse_args()

    if args.version:
        print(__version__)
        return

    settings = get_settings()
    settings.from_args(args)

    logging.basicConfig(
        level=logging.DEBUG if settings.verbose else logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    logging.getLogger("watchfiles").setLevel(logging.WARNING)

    if args.schema:
        _write_schema(args.schema)
        return

    start_server()


if __name__ == "__main__":
    main()
