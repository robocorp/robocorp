import importlib
from unittest import mock

import pytest

from robocorp.workitems import _requests


@pytest.fixture(autouse=True)
def _restore_default_timeout(monkeypatch):
    """`DEFAULT_TIMEOUT` is computed once at import time, so any test that
    changes `RC_API_REQUEST_TIMEOUT` must reload the module to pick it up,
    and this restores the module to its unpatched state afterwards.
    """
    yield
    monkeypatch.delenv("RC_API_REQUEST_TIMEOUT", raising=False)
    importlib.reload(_requests)


class TestRequestTimeout:
    def test_default_timeout_is_applied(self):
        with mock.patch(
            "robocorp.workitems._requests.requests.Session.get"
        ) as mock_get:
            mock_get.__name__ = "get"
            mock_get.return_value.status_code = 200
            mock_get.return_value.ok = True

            _requests.Requests().get("https://example.com")

        assert mock_get.call_args.kwargs["timeout"] == _requests.DEFAULT_TIMEOUT
        assert _requests.DEFAULT_TIMEOUT == 60.0

    def test_env_var_overrides_default_timeout(self, monkeypatch):
        monkeypatch.setenv("RC_API_REQUEST_TIMEOUT", "5")
        importlib.reload(_requests)

        with mock.patch(
            "robocorp.workitems._requests.requests.Session.get"
        ) as mock_get:
            mock_get.__name__ = "get"
            mock_get.return_value.status_code = 200
            mock_get.return_value.ok = True

            _requests.Requests().get("https://example.com")

        assert _requests.DEFAULT_TIMEOUT == 5.0
        assert mock_get.call_args.kwargs["timeout"] == 5.0

    def test_caller_supplied_timeout_is_not_overridden(self):
        with mock.patch(
            "robocorp.workitems._requests.requests.Session.get"
        ) as mock_get:
            mock_get.__name__ = "get"
            mock_get.return_value.status_code = 200
            mock_get.return_value.ok = True

            _requests.Requests().get("https://example.com", timeout=3.5)

        assert mock_get.call_args.kwargs["timeout"] == 3.5


class TestConnectionReuse:
    def test_requests_share_one_session(self):
        client = _requests.Requests()

        with mock.patch.object(client._session, "send") as mock_send:
            mock_send.return_value.status_code = 200
            mock_send.return_value.ok = True

            client.get("https://example.com/a")
            client.post("https://example.com/b", json={})

        assert mock_send.call_count == 2

    def test_module_level_requests_are_not_used(self):
        with (
            mock.patch("robocorp.workitems._requests.requests.get") as mock_get,
            mock.patch(
                "robocorp.workitems._requests.requests.Session.get"
            ) as mock_session_get,
        ):
            mock_session_get.__name__ = "get"
            mock_session_get.return_value.status_code = 200
            mock_session_get.return_value.ok = True

            _requests.Requests().get("https://example.com")

        mock_get.assert_not_called()
        mock_session_get.assert_called_once()
