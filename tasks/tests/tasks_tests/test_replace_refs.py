import pytest


def test_replace_refs():
    from robocorp.tasks._remove_refs import replace_refs

    json = {
        "a": ["foobar"],
        "b": {"$ref": "#/a"},
        "c": {"$ref": "#/a"},
        "d": {"$ref": "#/c"},
    }
    result = replace_refs(json)
    assert result == {
        "a": ["foobar"],
        "b": ["foobar"],
        "c": ["foobar"],
        "d": ["foobar"],
    }


def test_replace_refs_later_ref():
    from robocorp.tasks._remove_refs import replace_refs

    json = {
        "b": {"$ref": "#/a"},
        "c": {"$ref": "#/a"},
        "d": {"$ref": "#/c"},
        "a": ["foobar"],
    }
    result = replace_refs(json)
    assert result == {
        "a": ["foobar"],
        "b": ["foobar"],
        "c": ["foobar"],
        "d": ["foobar"],
    }


def test_circular_ref():
    from robocorp.tasks._remove_refs import JsonRefError, replace_refs

    json = {
        "b": {"$ref": "#/c"},
        "c": {"$ref": "#/b"},
    }
    with pytest.raises(JsonRefError):
        replace_refs(json)


def test_list_ref():
    from robocorp.tasks._remove_refs import replace_refs

    json = {
        "a": [1],
        "b": {"$ref": "#/a"},
    }
    assert replace_refs(json) == {"a": [1], "b": [1]}


def test_deep_ref():
    from robocorp.tasks._remove_refs import replace_refs

    json = {
        "a": "string",
        "b": {"$ref": "#/a"},
        "e": {"$ref": "#/d"},
        "c": {"$ref": "#/b"},
        "d": {"$ref": "#/c"},
        "f": {"$ref": "#/e"},
    }
    assert replace_refs(json) == {
        "a": "string",
        "b": "string",
        "c": "string",
        "d": "string",
        "e": "string",
        "f": "string",
    }


def test_bad_ref():
    from robocorp.tasks._remove_refs import JsonRefError, replace_refs

    json = {
        "a": ["foobar"],
        "b": {"$ref": "#/a"},
        "c": {"$ref": "#/x"},
    }
    with pytest.raises(JsonRefError):
        replace_refs(json)
