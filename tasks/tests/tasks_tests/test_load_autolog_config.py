def test_load_autolog_config(tmpdir, str_regression) -> None:
    from pathlib import Path
    from robocorp.tasks._toml_settings import read_pyproject_toml

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

    from robocorp.tasks._log_auto_setup import read_robocorp_log_config

    class Ctx:
        def show_error(self, error):
            raise AssertionError(error)

    config = read_robocorp_log_config(Ctx(), pyproject_info)
    str_regression.check(str(config))


def test_load_autolog_config_exclude_default(tmpdir, str_regression) -> None:
    from pathlib import Path
    from robocorp.tasks._toml_settings import read_pyproject_toml

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

    from robocorp.tasks._log_auto_setup import read_robocorp_log_config

    class Ctx:
        def show_error(self, error):
            raise AssertionError(error)

    config = read_robocorp_log_config(Ctx(), pyproject_info)
    str_regression.check(str(config))
