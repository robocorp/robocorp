def test_action_description_from_docs():
    from robocorp.action_server._server import get_action_description_from_docs

    docs = """This is my docstring
    
Args:
    arg1: foo
"""

    desc = get_action_description_from_docs(docs)
    assert desc == "This is my docstring"


def test_action_description_from_docs_multiline():
    from robocorp.action_server._server import get_action_description_from_docs

    docs = """This is my docstring
It contains
Multiple lines
    
Args:
    arg1: foo
"""

    desc = get_action_description_from_docs(docs)
    assert desc == "This is my docstring\nIt contains\nMultiple lines"
