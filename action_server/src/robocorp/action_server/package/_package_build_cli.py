import os
import sys
import typing
from logging import getLogger
from pathlib import Path

from robocorp.action_server._protocols import (
    ArgumentsNamespace,
    ArgumentsNamespacePackage,
    ArgumentsNamespacePackageBuild,
    ArgumentsNamespacePackageExtract,
    ArgumentsNamespacePackageMetadata,
    ArgumentsNamespacePackageUpdate,
)

log = getLogger(__name__)


def add_package_command(command_subparser, defaults):
    from robocorp.action_server._cli_helpers import add_data_args, add_verbose_args

    # Package handling
    package_parser = command_subparser.add_parser(
        "package",
        help="Utilities to manage the action package",
    )

    package_subparsers = package_parser.add_subparsers(dest="package_command")

    ### Update

    update_parser = package_subparsers.add_parser(
        "update",
        help="Updates the structure of a previous version of an action package to the latest version supported by the action server",
    )
    update_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="If passed, changes aren't actually done, they'll just be printed",
        default=False,
    )
    update_parser.add_argument(
        "--no-backup",
        action="store_true",
        help="If passed, file may be directly removed or overwritten, otherwise, a '.bak' file will be created prior to the operation",
        default=False,
    )
    add_verbose_args(update_parser, defaults)

    ### Build

    build_parser = package_subparsers.add_parser(
        "build",
        help="Creates a .zip with the contents of the action package so that it can be deployed",
    )
    build_parser.add_argument(
        "--output-dir",
        dest="output_dir",
        help="The output file for saving the action package built file",
        default=None,
    )
    build_parser.add_argument(
        "--override",
        action="store_true",
        help="If passed if the target .zip is already present it'll be overridden without asking",
        default=False,
    )
    add_data_args(build_parser, defaults)
    add_verbose_args(build_parser, defaults)

    ### Extract

    extract_parser = package_subparsers.add_parser(
        "extract",
        help="Extracts a .zip previously created with `action-server package build` to a folder",
    )
    extract_parser.add_argument(
        "--output-dir",
        dest="output_dir",
        help="The output file for saving the action package built file",
        default=".",
    )
    extract_parser.add_argument(
        "--override",
        action="store_true",
        help="If set, the contents will be extracted to a non-empty folder without prompting",
        default=False,
    )
    add_verbose_args(extract_parser, defaults)
    extract_parser.add_argument(
        "filename", help="The .zip file that should be extracted"
    )

    ### Metadata

    extract_parser = package_subparsers.add_parser(
        "metadata",
        help="Collects metadata from the action package in the current cwd and prints it to stdout",
    )
    add_data_args(extract_parser, defaults)
    add_verbose_args(extract_parser, defaults)


def handle_package_command(base_args: ArgumentsNamespace):
    from robocorp.action_server._errors_action_server import ActionServerValidationError
    from robocorp.action_server.vendored_deps.termcolors import bold_red

    package_args: ArgumentsNamespacePackage = typing.cast(
        ArgumentsNamespacePackage, base_args
    )
    package_command = package_args.package_command
    if not package_command:
        log.critical("Command for package operation not specified.")
        return 1

    if package_command == "update":
        package_update_args: ArgumentsNamespacePackageUpdate = typing.cast(
            ArgumentsNamespacePackageUpdate, base_args
        )

        from robocorp.action_server.vendored_deps.action_package_handling import (
            update_package,
        )

        update_package(
            Path(".").absolute(),
            dry_run=package_update_args.dry_run,
            backup=not package_update_args.no_backup,
        )
        return 0

    elif package_command == "build":
        from robocorp.action_server.package._package_build import build_package

        package_build_args: ArgumentsNamespacePackageBuild = typing.cast(
            ArgumentsNamespacePackageBuild, base_args
        )

        # action-server package build --output-dir=<zipfile> --datadir=<directory> <source-directory>:
        try:
            retcode = build_package(
                Path(".").absolute(),
                output_dir=package_build_args.output_dir,
                datadir=package_build_args.datadir,
                override=package_build_args.override,
            )
        except ActionServerValidationError as e:
            log.critical(
                bold_red(
                    f"\nUnable to build action package. Please fix the error below and retry.\n{e}",
                )
            )
            retcode = 1
        return retcode

    elif package_command == "extract":
        package_extract_args: ArgumentsNamespacePackageExtract = typing.cast(
            ArgumentsNamespacePackageExtract, base_args
        )

        zip_filename = package_extract_args.filename
        if not os.path.exists(zip_filename):
            log.critical(f"The target zip: {zip_filename} does not exist.")
            return 1

        target_dir = package_extract_args.output_dir
        if not package_extract_args.override:
            if os.path.exists(target_dir):
                if len(os.listdir(target_dir)) > 1:
                    # Check if we should override.
                    while c := input(
                        f"It seems that {target_dir} already exists and is not empty. Are you sure you want to extract to it? (y/n)"
                    ).lower() not in ("y", "n"):
                        continue
                    if c == "n":
                        return 1
                    # otherwise 'y', keep on going...

        import zipfile

        with zipfile.ZipFile(zip_filename, "r") as zip_ref:
            zip_ref.extractall(target_dir)
        return 0

    elif package_command == "metadata":
        from robocorp.action_server.package._package_metadata import (
            collect_package_metadata,
        )

        package_metadata_args: ArgumentsNamespacePackageMetadata = typing.cast(
            ArgumentsNamespacePackageBuild, base_args
        )

        # action-server package metadata --datadir=<directory>
        retcode = 0
        try:
            package_metadata_or_returncode: str | int = collect_package_metadata(
                Path(".").absolute(),
                datadir=package_metadata_args.datadir,
            )
            if isinstance(package_metadata_or_returncode, str):
                print(package_metadata_or_returncode)
                sys.stdout.flush()
            else:
                assert package_metadata_or_returncode != 0
                retcode = package_metadata_or_returncode

        except ActionServerValidationError as e:
            log.critical(
                bold_red(
                    f"\nUnable to collect package metadata. Please fix the error below and retry.\n{e}",
                )
            )
            retcode = 1
        return retcode

    log.critical(f"Invalid package command: {package_command}")
    return 1
