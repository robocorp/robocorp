import json
import logging
import subprocess
import typing
from pathlib import Path
from typing import Optional

if typing.TYPE_CHECKING:
    from robocorp.action_server._models import ActionPackage

log = logging.getLogger(__name__)


class ActionPackageError(Exception):
    pass


def import_action_package(
    datadir: Path, action_package_dir: str, name: Optional[str] = None
):
    """
    Imports action packages based on directories given in the filesystem.

    Note that the action package is expected to be in the proper directory at
    this point (meaning that it should have been extracted under the /datadir
    if given as a .zip or a path in the filesystem in any other place when
    running in dev mode).

    Raises:
        ActionPackageError if it was not recognized as an action package.

    Note:
        This can be a slow operation as it may require building the RCC
        environment.
    """

    from robocorp.action_server._robo_utils.process import build_python_launch_env

    from ._gen_ids import gen_uuid
    from ._models import ActionPackage
    from ._rcc import create_hash, get_rcc

    log.info("Importing action package: %s", action_package_dir)

    datadir = datadir.absolute()
    import_path = Path(action_package_dir).absolute()
    if not import_path.exists():
        raise ActionPackageError(
            f"Unable to import action package from directory: {import_path} "
            "(directory does not exist).",
        )

    import yaml

    # Verify if it's actually a proper package (meaning that it has
    # the conda.yaml as well as actions we can run).
    conda_yaml = import_path / "conda.yaml"

    try:
        with open(conda_yaml, "r", encoding="utf-8") as stream:
            contents = yaml.safe_load(stream)
    except Exception:
        raise ActionPackageError(f"{conda_yaml} does not seem a valid yaml.")

    if not isinstance(contents, dict):
        raise ActionPackageError(f"{conda_yaml} has no dict as top-level.")

    if not contents.get("dependencies"):
        raise ActionPackageError(f"{conda_yaml} has no 'dependencies' specified.")

    action_package_id = gen_uuid("action_package")
    if not name:
        name = import_path.name

    # The hash is based only on the parsed contents, not on the file
    # contents per se (so, changing comments or spaces is ok).
    condahash = create_hash(repr(contents))

    log.info("Action package seems ok. Bootstrapping RCC environment.")
    rcc = get_rcc()
    env_info = rcc.create_env_and_get_vars(conda_yaml, condahash)
    if not env_info.success:
        raise ActionPackageError(
            f"It was not possible to bootstrap the RCC environment. "
            f"Error: {env_info.message}"
        )
    if not env_info.result:
        raise ActionPackageError(
            "It was not possible to get the environment when "
            "bootstrapping RCC environment."
        )

    # Ok, we bootstrapped, now, let's collect the actions.
    try:
        directory_path = import_path.relative_to(datadir)
        assert import_path.samefile(directory_path)
    except (AssertionError, ValueError):
        directory_path = import_path

    action_package = ActionPackage(
        id=action_package_id,
        name=name,
        directory=directory_path.as_posix(),
        conda_hash=condahash,
        env_json=json.dumps(env_info.result.env),
    )
    log.info(
        f"RCC environment bootstrapped for action package: {name}. Collecting actions."
    )

    env = build_python_launch_env(env_info.result.env)
    _add_actions_to_db(datadir, env, import_path, action_package)


def _add_actions_to_db(
    datadir: Path,
    env: dict,
    import_path: Path,
    action_package: "ActionPackage",
):
    from robocorp.action_server._gen_ids import gen_uuid
    from robocorp.action_server._models import Action, get_db

    cmdline = [env["PYTHON_EXE"], "-m", "robocorp.actions", "list"]
    popen = subprocess.Popen(
        cmdline,
        env=env,
        cwd=import_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False,
    )
    stdout, stderr = popen.communicate()
    if popen.poll() != 0:
        raise RuntimeError(
            f"It was not possible to list the actions.\n"
            f"cmdline: {subprocess.list2cmdline(cmdline)}\n"
            f"stdout:{stdout.decode('utf-8', 'replace')}\n"
            f"stderr:{stderr.decode('utf-8', 'replace')}"
        )
    try:
        loaded = json.loads(stdout)
    except json.JSONDecodeError:
        raise RuntimeError(
            f"It was not possible to load as json the contents >>{stdout!r}<<"
        )
    else:
        actions = []
        for action_fields in loaded:
            filepath = Path(action_fields["file"]).absolute()
            try:
                filepath = filepath.relative_to(import_path)
            except ValueError:
                pass

            actions.append(
                Action(
                    id=gen_uuid("action"),
                    action_package_id=action_package.id,
                    name=action_fields["name"],
                    docs=action_fields["docs"],
                    file=filepath.as_posix(),
                    lineno=action_fields["line"],
                    input_schema=json.dumps(action_fields["input_schema"]),
                    output_schema=json.dumps(action_fields["output_schema"]),
                )
            )

    db = get_db()
    with db.transaction():
        db.insert(action_package)
        for action in actions:
            db.insert(action)
