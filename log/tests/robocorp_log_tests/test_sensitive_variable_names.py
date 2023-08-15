import pytest


def test_sensitive_variable_names_pattern_empty():
    from robocorp.log._sensitive_variable_names import SensitiveVariableNames

    sensitive_variable_names = SensitiveVariableNames(())
    assert not sensitive_variable_names.is_sensitive_variable_name("myab")

    with pytest.raises(ValueError):
        sensitive_variable_names.add_sensitive_variable_name_pattern("")
    assert not sensitive_variable_names.is_sensitive_variable_name("myab")


def test_sensitive_variable_names_pattern():
    from robocorp.log._sensitive_variable_names import SensitiveVariableNames

    sensitive_variable_names = SensitiveVariableNames(())
    import re

    sensitive_variable_names.add_sensitive_variable_name_pattern(
        re.compile(".*AB", re.IGNORECASE)
    )
    assert sensitive_variable_names.is_sensitive_variable_name("myab")
    assert not sensitive_variable_names.is_sensitive_variable_name("my")


def test_sensitive_variable_names():
    from robocorp.log._sensitive_variable_names import SensitiveVariableNames

    sensitive_variable_names = SensitiveVariableNames(("passwd",))
    assert sensitive_variable_names.is_sensitive_variable_name("passwd")
    assert sensitive_variable_names.is_sensitive_variable_name("some_passwd")
    assert not sensitive_variable_names.is_sensitive_variable_name("not")

    sensitive_variable_names.add_sensitive_variable_name("not")
    assert sensitive_variable_names.is_sensitive_variable_name("not")
    assert sensitive_variable_names.is_sensitive_variable_name("nothing")

    assert not sensitive_variable_names.is_sensitive_variable_name("some")
    sensitive_variable_names.add_sensitive_variable_name_pattern("so.*me")
    assert sensitive_variable_names.is_sensitive_variable_name("soaaaame")

    # Just add the name directly
    sensitive_variable_names.add_sensitive_variable_name("bar.*")
    assert not sensitive_variable_names.is_sensitive_variable_name("bar")
    assert sensitive_variable_names.is_sensitive_variable_name("bar.*")
