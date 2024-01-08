import pytest


def test_ok():
    a = 1  # noqa
    print("worked")
    for i in range(50):
        j = "************" * i
        print(j)


def test_fail():
    assert False, "Something failed..."


@pytest.fixture
def fixture():
    raise RuntimeError("something bad in fixture")


def test_fixture_fail(fixture):
    pass
