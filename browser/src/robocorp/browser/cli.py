# ruff: noqa: E501
import argparse
import sys

from ._engines import install_browser
from ._types import BrowserEngine, InstallError


def main():
    parser = argparse.ArgumentParser(
        prog="robocorp.browser", description="Command-line tool for robocorp.browser"
    )
    subparsers = parser.add_subparsers(required=True)

    install_parser = subparsers.add_parser(
        "install",
        help="Download and install Playwright browsers",
    )
    install_parser.set_defaults(func=_install_command)
    install_parser.add_argument(
        "engine",
        nargs="+",
        type=BrowserEngine,
        choices=[e.value for e in BrowserEngine],
        help="Browser type to install",
    )
    install_parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force install, overwrites existing Chrome and Microsoft Edge installations",
    )
    install_parser.add_argument(
        "--isolated",
        action="store_true",
        help="Install into holotree for caching (should only be used during post-install)",
    )

    args = parser.parse_args()
    args.func(args)


def _install_command(args):
    try:
        for engine in args.engine:
            install_browser(
                engine,
                force=args.force,
                interactive=True,
                isolated=args.isolated,
            )
    except (KeyboardInterrupt, InstallError):
        sys.exit(1)
