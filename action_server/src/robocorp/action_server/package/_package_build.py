import fnmatch
import glob
import os
from logging import getLogger
from pathlib import Path
from typing import Iterator, List, Tuple

log = getLogger(__name__)


def _check_matches(patterns, paths):
    if not patterns and not paths:
        # Matched to the end.
        return True

    if (not patterns and paths) or (patterns and not paths):
        return False

    pattern = patterns[0]
    path = paths[0]

    if not glob.has_magic(pattern):
        if pattern != path:
            return False

    elif pattern == "**":
        if len(patterns) == 1:
            return True  # if ** is the last one it matches anything to the right.

        for i in range(len(paths)):
            # Recursively check the remaining patterns as the
            # current pattern could match any number of paths.
            if _check_matches(patterns[1:], paths[i:]):
                return True

    elif not fnmatch.fnmatch(path, pattern):
        # Current part doesn't match.
        return False

    return _check_matches(patterns[1:], paths[1:])


def _glob_matches_path(path, pattern, sep=os.sep, altsep=os.altsep):
    if altsep:
        pattern = pattern.replace(altsep, sep)
        path = path.replace(altsep, sep)

    patterns = pattern.split(sep)
    paths = path.split(sep)
    if paths:
        if paths[0] == "":
            paths = paths[1:]
    if patterns:
        if patterns[0] == "":
            patterns = patterns[1:]

    return _check_matches(patterns, paths)


def _collect_files_excluding_patterns(
    root_dir: Path, exclusion_patterns: List[str]
) -> Iterator[Tuple[Path, str]]:
    """
    Collects all files within a directory, excluding those that match any of the
    specified exclusion patterns.

    Args:
        root_dir (str): The root directory to traverse.
        exclusion_patterns (list): A list of fnmatch patterns to exclude.

    Returns:
        An iterator over the full paths and the relative paths (str) found.
    """

    for path in root_dir.rglob("*"):  # Use rglob for recursive iteration
        if path.is_file():
            relative_path_str = str(path.relative_to(root_dir))

            add = True
            for pattern in exclusion_patterns:
                if _glob_matches_path(relative_path_str, pattern):
                    add = False
                    break

            if add:
                yield path, relative_path_str


def build_package(
    input_dir: Path, output_dir: str, datadir: str, override: bool
) -> int:
    """
    Builds an action package.

    Note: The actions are imported in the datadir with :memory: database
        for validation (so it won't affect the real database but will still
        be able to use the environments from it).

    Args:
        input_dir: The working dir (where the package.yaml is located).
        output_dir: The output directory for the package.
        datadir: The datadir to be used.
        override: Whether an existing .zip can be overridden.

    Returns:
        The return code for the process (0 for success).
    """
    import yaml

    from robocorp.action_server._models import Action, create_db
    from robocorp.action_server._slugify import slugify
    from robocorp.action_server.cli import _main_retcode
    from robocorp.action_server.package._ask_user import ask_user_input_to_proceed

    from .._errors_action_server import ActionServerValidationError

    # We expect a package.yaml to be there (we don't support just conda.yaml for
    # this).
    package_yaml = input_dir / "package.yaml"
    if not package_yaml.exists():
        raise ActionServerValidationError("package.yaml required for build.")

    # Additional validations based on the package.yaml
    try:
        with open(package_yaml, "r", encoding="utf-8") as stream:
            package_yaml_contents = yaml.safe_load(stream)
    except Exception:
        raise ActionServerValidationError(
            f"Error loading file as yaml ({package_yaml})."
        )

    name = package_yaml_contents.get("name")
    version = package_yaml_contents.get("version")
    if not name:
        raise ActionServerValidationError(
            f"The 'name' of the action package must be specified in the package.yaml ({package_yaml})."
        )
    if not version:
        raise ActionServerValidationError(
            f"The 'version' of the action package must be specified in the package.yaml ({package_yaml})."
        )

    slugified_name = slugify(name)
    target_zip_name = f"{slugified_name}-{version}.zip"

    output_file = Path(output_dir) / target_zip_name
    if not override and output_file.exists():
        if not ask_user_input_to_proceed(
            f"It seems that {target_zip_name} already exists. Do you want to override it? (y/n)\n"
        ):
            return 1

    packaging: dict = {}

    # packaging:
    #   # By default all files and folders in this directory are packaged when uploaded.
    #   # Add exclusion rules below (expects glob format: https://docs.python.org/3/library/glob.html)
    #   exclude:
    #    - *.temp
    #    - .vscode/**

    if isinstance(package_yaml_contents, dict):
        found = package_yaml_contents.get("packaging", {})
        if found and not isinstance(found, dict):
            raise ActionServerValidationError(
                "Expected 'packaging' session in package.yaml to be a dict."
            )
        packaging = found

    exclude_list = packaging.get("exclude")
    exclude_patterns = []
    if exclude_list:
        if not isinstance(exclude_list, list):
            raise ActionServerValidationError(
                "Expected 'packaging.exclude' session in package.yaml to be a list[str]."
            )

        for pat in exclude_list:
            if not isinstance(pat, str):
                raise ActionServerValidationError(
                    f"Expected 'packaging.exclude' session in package.yaml to be a list[str]. Found: {pat} ({type(pat)})."
                )

            if pat.startswith("./"):
                # If the user did './b/c', we have to start the match from
                # the current path.
                pat = pat[2:]
            elif pat.startswith("/"):
                # If the user did '/b/c', we have to start the match from
                # the root.
                pat = pat[1:]
            elif not pat.startswith("**"):
                # If the user did not anchor the pattern, make it available to
                # be matched anywhere (i.e.: *.pyc must match .pyc files anywhere).
                pat = f"**/{pat}"

            exclude_patterns.append(pat)

    # Import in-memory contents (importing will validate everything and as it's
    # in-memory it should not affect existing data). We still need the system
    # mutex lock on the datadir due to environment updates that can't happen in
    # parallel.
    args = ["import", "--db-file", ":memory:"]
    if datadir:
        args.extend(["--datadir", datadir])

    with create_db(":memory:") as db:
        returncode = _main_retcode(args, is_subcommand=True, use_db=db)
        if returncode != 0:
            return returncode
        if not db.all(Action):
            raise ActionServerValidationError(f"No actions found in '{input_dir}'.")

    # Ok, it seems we're good to go. Package everything based on the
    # package.yaml exclude rules.
    # https://github.com/robocorp/robocorp/blob/master/action_server/docs/guides/01-package-yaml.md
    import zipfile

    with zipfile.ZipFile(output_file, "w") as zip_file:
        for path, relative_path in _collect_files_excluding_patterns(
            input_dir, exclude_patterns
        ):
            # Don't add the .zip itself.
            if os.path.samefile(path, output_file):
                continue
            zip_file.writestr(relative_path, path.read_bytes())

    log.info(f"Created {output_file}")
    return 0
