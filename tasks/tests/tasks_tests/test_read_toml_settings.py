from pathlib import Path


def test_read_toml_settings():
    from robocorp.log.pyproject_config import PyProjectInfo
    from robocorp.log.pyproject_config import read_section_from_toml

    errors_shown = []

    class Context:
        def show_error(self, message):
            errors_shown.append(message)

    context = Context()
    toml_contents = {}
    assert (
        read_section_from_toml(
            PyProjectInfo(Path("pyproject.toml"), toml_contents), "my.path", context
        )
        is None
    )
    assert not errors_shown

    toml_contents = {}
    assert (
        read_section_from_toml(
            PyProjectInfo(Path("pyproject.toml"), toml_contents), "my", context
        )
        is None
    )
    assert not errors_shown

    toml_contents = {"my": 1}
    assert (
        read_section_from_toml(
            PyProjectInfo(Path("pyproject.toml"), toml_contents), "my", context
        )
        == 1
    )
    assert not errors_shown

    toml_contents = {"my": "foo"}
    assert (
        read_section_from_toml(
            PyProjectInfo(Path("pyproject.toml"), toml_contents), "my.foo", context
        )
        is None
    )
    assert errors_shown == ["Expected 'my' to be a dict in pyproject.toml."]
    errors_shown.clear()

    toml_contents = {"my": {"path": []}}
    assert (
        read_section_from_toml(
            PyProjectInfo(Path("pyproject.toml"), toml_contents), "my.path", context
        )
        == []
    )
    assert not errors_shown
