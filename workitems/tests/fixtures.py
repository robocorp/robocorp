from unittest import mock

import pytest

from robocorp.workitems import inputs as _inputs
from robocorp.workitems import outputs as _outputs
from robocorp.workitems._context import Context

from .mocks import MockAdapter


@pytest.fixture
def adapter():
    MockAdapter.reset()
    yield MockAdapter


@pytest.fixture
def context(adapter):
    ctx = Context(default_adapter=adapter)
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
