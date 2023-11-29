pytest_plugins = [
    "devutils.fixtures",
    "action_server_tests.fixtures",
]


def pytest_addoption(parser):
    # i.e.: add something as:
    # --path-to-store-json-db=c:/temp/action_test.json
    # in the command line
    parser.addoption("--path-to-store-json-db", action="store", default="")
