import argparse
import sys

from ._browser_engines import BrowserEngine, InstallError, install_browser


def main():
    parser = argparse.ArgumentParser(prog="robocorp.browser")
    subparsers = parser.add_subparsers(required=True)

    install_parser = subparsers.add_parser(
        "install",
        help="download and install Playwright browsers",
    )
    install_parser.set_defaults(func=_install_command)
    install_parser.add_argument(
        "engine", type=BrowserEngine, choices=[e.value for e in BrowserEngine]
    )
    install_parser.add_argument("force", action="store_true")

    args = parser.parse_args()
    args.func(args)


def _install_command(args):
    try:
        install_browser(args.engine, force=args.force, interactive=True)
    except (KeyboardInterrupt, InstallError):
        sys.exit(1)
