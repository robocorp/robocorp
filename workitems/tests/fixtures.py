from unittest import mock

import pytest

from robocorp.workitems import inputs as _inputs
from robocorp.workitems import outputs as _outputs
from robocorp.workitems._context import Context

from .mocks import MockAdapter


@pytest.fixture
def adapter():
    adapter = MockAdapter()
    adapter.reset()
    yield adapter


@pytest.fixture
def context(adapter):
    ctx = Context(adapter=adapter)
    ctx.reserve_input()

    def _getter():
        return ctx

    with mock.patch("robocorp.workitems._ctx", _getter):
        yield ctx


@pytest.fixture
def inputs(context):
    yield _inputs


@pytest.fixture
def outputs(context):
    yield _outputs
