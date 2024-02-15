import json
import shutil
import sys
from pathlib import Path

import pytest

from robocorp.action_server._selftest import ActionServerClient, ActionServerProcess


@pytest.fixture
def wheel_path(tmpdir, datadir) -> Path:
    import subprocess

    create_wheel_dir = datadir / "create_wheel"
    # python3 setup.py bdist_wheel
    subprocess.run([sys.executable, "-m", "pip", "wheel", "."], cwd=create_wheel_dir)

    wheels_found = list(create_wheel_dir.glob("*.whl"))
    assert len(wheels_found) == 1, f"Expected one wheel. Found: {wheels_found}"
    return wheels_found[0]


def test_create_conda_from_package_yaml(
    tmpdir,
    datadir,
    data_regression,
    wheel_path,
    action_server_process: ActionServerProcess,
    client: ActionServerClient,
) -> None:
    """
    This is a "heavy" test because it bootstraps an rcc environment (to
    make sure that we can actually deal with a wheel).
    """
    import yaml

    from robocorp.action_server.vendored_deps.action_package_handling import (
        create_conda_from_package_yaml,
    )

    wheel_name = wheel_path.name

    tmppath = Path(tmpdir) / "check"
    tmppath.mkdir(exist_ok=True)
    package_yaml = tmppath / "package.yaml"

    run_post_install = tmppath / "run_post_install.py"
    package_yaml.write_text(
        f"""
dependencies:
  conda-forge: 
    # This section is required: at least the python version must be specified.
    - python=3.10.12
    - pip=24.0
    # If robocorp-truststore or truststore is here, - --use-feature=truststore
    # is added to pip.
    - robocorp-truststore=0.8.0

  pip:
    - robocorp-actions

  local-wheels:
    - ./wheels/{wheel_name}
    
post-install:
  # Note: relative paths won't work because we can't set the rcc
  # working dir at this point!
  - python {run_post_install.as_posix()}
"""
    )

    wheels_dir: Path = tmppath / "wheels"
    wheels_dir.mkdir()
    shutil.copy(wheel_path, wheels_dir / wheel_name)

    create_in_postinstall = tmpdir / "create-in-postinstall.txt"
    run_post_install.write_text(
        f"""
with open({str(create_in_postinstall)!r}, 'w') as stream:
    stream.write('Executed')
"""
    )
    assert not create_in_postinstall.exists()

    result_path = create_conda_from_package_yaml(Path(datadir), package_yaml)
    assert result_path.exists()
    dict_with_pip_entries = None
    with result_path.open() as stream:
        loaded = yaml.safe_load(stream)
        deps = loaded["dependencies"]
        for d in deps:
            if isinstance(d, dict):
                dict_with_pip_entries = d
                pip_entries = d["pip"]
                break
        else:
            raise RuntimeError("Unable to find pip entry.")
        new_pip_entries = [
            x.replace(str(tmppath.as_posix()), "...<path>...").replace("\\", "/")
            for x in pip_entries
        ]
        dict_with_pip_entries["pip"] = new_pip_entries
        post_install = loaded["rccPostInstall"]
        loaded["rccPostInstall"] = [
            x.replace(str(tmppath.as_posix()), "...<path>...").replace("\\", "/")
            for x in post_install
        ]

        data_regression.check(loaded)

    (tmppath / "my_action.py").write_text(
        """
from robocorp.actions import action

@action
def my_action() -> str:
    from my_wheel import my_module
    return my_module.in_my_module()
"""
    )

    action_server_process.start(
        db_file="server.db",
        cwd=tmppath,
        actions_sync=True,
        timeout=300,
    )

    assert create_in_postinstall.exists()

    result = client.post_get_str("api/actions/check/my-action/run", {})
    assert json.loads(result) == "in_my_module"


def test_package_update(tmpdir, data_regression):
    import io

    import yaml

    from robocorp.action_server.vendored_deps.action_package_handling import (
        update_package,
    )

    tmp = Path(tmpdir)
    conda_yaml = tmp / "conda.yaml"
    conda_yaml.write_text(
        """
channels:
  - conda-forge

dependencies:
  - python=3.10.12
  - pip=23.2.1
  - robocorp-truststore=0.8.0
  - foo>3
  - bar>=3
  - pip:
      - robocorp==1.4.0
      - robocorp-actions==0.0.7
      - playwright>1.1
      - pytz==2023.3
rccPostInstall:
  - python -m foobar
"""
    )
    stream = io.StringIO()
    update_package(tmp, dry_run=True, stream=stream)

    assert not (tmp / "package.yaml").exists()

    update_package(tmp, dry_run=False, backup=False, stream=stream)
    assert (tmp / "package.yaml").exists()
    with (tmp / "package.yaml").open() as stream:
        data_regression.check(yaml.safe_load(stream))
