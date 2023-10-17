import pytest

from robocorp.windows.protocols import Locator


def check_tokenize(s, str_regression, basename):
    from robocorp.windows._match_tokenization import _Tokenizer

    contents = []
    for token in _Tokenizer(s).tokenize():
        contents.append(str(token))
    str_regression.check("\n".join(contents), basename=f"tok_{basename}")


def check_ast(locator: Locator, str_regression, basename=None, expected_exception=None):
    from robocorp.windows._match_ast import _build_locator_match

    if basename is None:
        basename = make_valid_filename(locator).lower()

    if expected_exception:
        with pytest.raises(expected_exception) as e:
            _build_locator_match(locator)
        str_regression.check(str(e.value), basename=f"err_ast_{basename}")
    else:
        built = _build_locator_match(locator)
        s = str(built)
        if built.warnings:
            s += "\nWARNINGS:\n"
            s += "\n".join(built.warnings)
        str_regression.check(s, basename=f"ast_{basename}")


def test_ast_flattened_conditions(str_regression):
    from robocorp.windows._errors import InvalidStrategyDuplicated

    check_ast(r"((name:y or name:z) and path:1) or name:w", str_regression)
    check_ast(r"((name:y or name:z) and path:1)", str_regression)
    check_ast(
        r"((name:y class:z) or name:w or (((name:h class:y) or name:j)))",
        str_regression,
    )
    check_ast(r"name:x or ((name:y class:z) and path:1)", str_regression)
    check_ast(r"name:x or (name:y class:z)", str_regression)
    check_ast(
        r"(name:b or path:1) name:c",
        str_regression,
        expected_exception=InvalidStrategyDuplicated,
    )

    check_ast(r"name:x or (name:y class:z)", str_regression)
    check_ast(r"name:x or ((name:y class:z) or name:w)", str_regression)
    check_ast(
        r"name:a or name:b or path:1 and name:c",
        str_regression,
    )

    check_ast(
        r"name:x or ((name:y class:z) name:w)",
        str_regression,
        expected_exception=InvalidStrategyDuplicated,
    )


def test_ast(str_regression):
    from robocorp.windows._errors import (
        InvalidLocatorError,
        InvalidStrategyDuplicated,
        ParseError,
    )

    check_ast(
        "desktop > name:y",
        str_regression,
    )
    check_ast(
        "name:y or name:z > ()",
        str_regression,
        expected_exception=InvalidLocatorError,
    )
    check_ast(
        "() > name:y or name:z",
        str_regression,
        expected_exception=InvalidLocatorError,
    )

    check_ast(
        "(name:y or name:z > bar)",
        str_regression,
        expected_exception=InvalidLocatorError,
    )
    check_ast(
        "(name:y or name:z",
        str_regression,
        expected_exception=InvalidLocatorError,
    )
    check_ast(
        "name:y or name:z)",
        str_regression,
        expected_exception=InvalidLocatorError,
    )
    check_ast(
        "name:",
        str_regression,
        expected_exception=InvalidLocatorError,
    )
    check_ast('name:"or"', str_regression)
    check_ast(
        "name: and",
        str_regression,
        expected_exception=InvalidLocatorError,
    )
    check_ast(
        "name:or",
        str_regression,
        expected_exception=InvalidLocatorError,
    )
    check_ast('"name:foo bar"', str_regression)
    check_ast('"name:"', str_regression)
    check_ast(
        r"name:x or ",  # Or requires continuation!
        str_regression,
        expected_exception=InvalidLocatorError,
    )
    check_ast(
        r"name:x or or name:y",  # Or requires continuation!
        str_regression,
        expected_exception=InvalidLocatorError,
    )

    check_ast(r"a or b", str_regression, "a_or_b")

    check_ast(
        "name:foo name:bar",
        str_regression,
        expected_exception=InvalidStrategyDuplicated,
    )
    check_ast(
        "name:foo depth:2 bar",
        str_regression,
        expected_exception=InvalidStrategyDuplicated,
    )
    check_ast(
        "foo depth:2 bar", str_regression, expected_exception=InvalidStrategyDuplicated
    )

    check_ast("Robocorp > File", str_regression)
    check_ast(r"a or b", str_regression, "a_or_b")
    check_ast(r"name:foo\"bar", str_regression, "name_slash_bar")
    check_ast(r"(a or b)", str_regression, "a_or_b_parens")
    check_ast(r"Robocorp", str_regression)
    check_ast(r"Robocorp Window", str_regression)
    check_ast(r"name:Robocorp Window", str_regression)
    check_ast(r'name:"Robocorp\'s Window"', str_regression)
    check_ast('name:"Robocorp\'s Window" class:"My Class"', str_regression)
    check_ast('name:"Robocorp > File"', str_regression)
    check_ast('class:"My Class" Test', str_regression)
    check_ast(
        '"Robocorp Window93" subname:Robocorp and class:"My Class" regex:Robo.+',
        str_regression,
    )
    check_ast("Robocorp_colon:Window:bar", str_regression)
    check_ast("Robocorp:Window class:Class", str_regression)
    check_ast("class:Class classx:Classx Test2", str_regression)
    check_ast("name:'my name'", str_regression)  # Warn about single quotes.
    check_ast('Robocorp" Window', str_regression, expected_exception=ParseError)
    check_ast(
        'name:Robocorp" Window class:"My Class"',
        str_regression,
        expected_exception=ParseError,
    )
    check_ast(
        'name:"Robocorp" Window" class:"My Class"',
        str_regression,
        expected_exception=InvalidStrategyDuplicated,
    )
    check_ast(
        "Robo and Corp",
        str_regression,
        expected_exception=InvalidStrategyDuplicated,
    )
    check_ast("> name:foo", str_regression, expected_exception=InvalidLocatorError)
    check_ast("name:foo >", str_regression, expected_exception=InvalidLocatorError)
    check_ast("", str_regression, expected_exception=InvalidLocatorError)


def test_tokenize(str_regression):
    check_tokenize(r"name:foo\"bar", str_regression, "name_slash_bar")
    check_tokenize(
        (
            '"Robocorp Window93" subname:Robocorp and class:"My Class" '
            "Test regex:Robo.+"
        ),
        str_regression,
        "robocorp_window_93",
    )
    check_tokenize(
        "Robocorp Window > path:2|3|2|8|2", str_regression, "robocorp_window_path"
    )
    check_tokenize('name:Foo or name:"some name"', str_regression, "name_foo_some_name")
    check_tokenize("Calculator > path:2|3|2|8|2", str_regression, "calc_path")
    check_tokenize(r" (a or b) ", str_regression, "a_or_b")
    check_tokenize(r"(a or b)", str_regression, "a_or_b")
    check_tokenize(r"( a or b )", str_regression, "a_or_b")

    check_tokenize(r'name:  "foo \" bar"', str_regression, "name_spaces_foo_slash_bar")
    check_tokenize(r'name:"foo \" bar"', str_regression, "name_foo_slash_bar")
    check_tokenize('name:"foo bar"', str_regression, "name_foo_bar")
    check_tokenize("name:foo", str_regression, "name_foo")
    check_tokenize("not_strategy:foo", str_regression, "not_strategy")


def make_valid_filename(basename: str) -> str:
    import re

    sanitized_basename = re.sub(r'[\'\\/:*?"<>|\s]', "_", basename)

    return sanitized_basename
