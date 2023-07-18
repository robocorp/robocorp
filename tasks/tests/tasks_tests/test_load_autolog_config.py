def test_load_autolog_config(tmpdir, str_regression) -> None:
    from pathlib import Path
    from robocorp.log.pyproject_config import read_robocorp_auto_log_config
    from robocorp.log.pyproject_config import read_pyproject_toml

    target = tmpdir / "pyproject.toml"
    target.write_text(
        """
[tool.robocorp.log]

log_filter_rules = [
    {name = "RPA", kind = "log_on_project_call"},
    {name = "selenium", kind = "log_on_project_call"},
    {name = "SeleniumLibrary", kind = "log_on_project_call"},
]
""",
        "utf-8",
    )
    pyproject_info = read_pyproject_toml(Path(target))
    assert pyproject_info is not None

    class Ctx:
        def show_error(self, error):
            raise AssertionError(error)

    config = read_robocorp_auto_log_config(Ctx(), pyproject_info)

    str_regression.check(str(config))


def test_load_autolog_config_exclude_default(tmpdir, str_regression) -> None:
    from pathlib import Path
    from robocorp.log.pyproject_config import read_pyproject_toml
    from robocorp.log.pyproject_config import read_robocorp_auto_log_config

    target = tmpdir / "pyproject.toml"
    target.write_text(
        """
[tool.robocorp.log]

log_filter_rules = [
    {name = "RPA.*", kind = "log_on_project_call"},
]

default_library_filter_kind = "exclude"
""",
        "utf-8",
    )
    pyproject_info = read_pyproject_toml(Path(target))
    assert pyproject_info is not None

    class Ctx:
        def show_error(self, error):
            raise AssertionError(error)

    config = read_robocorp_auto_log_config(Ctx(), pyproject_info)
    str_regression.check(str(config))
