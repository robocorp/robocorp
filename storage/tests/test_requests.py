import importlib
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

import pytest

from robocorp.storage import _requests


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
        with mock.patch("robocorp.storage._requests.requests.Session.get") as mock_get:
            mock_get.__name__ = "get"
            mock_get.return_value.status_code = 200
            mock_get.return_value.ok = True

            _requests.Requests().get("https://example.com")

        assert mock_get.call_args.kwargs["timeout"] == _requests.DEFAULT_TIMEOUT
        assert _requests.DEFAULT_TIMEOUT == 60.0

    def test_env_var_overrides_default_timeout(self, monkeypatch):
        monkeypatch.setenv("RC_API_REQUEST_TIMEOUT", "5")
        importlib.reload(_requests)

        with mock.patch("robocorp.storage._requests.requests.Session.get") as mock_get:
            mock_get.__name__ = "get"
            mock_get.return_value.status_code = 200
            mock_get.return_value.ok = True

            _requests.Requests().get("https://example.com")

        assert _requests.DEFAULT_TIMEOUT == 5.0
        assert mock_get.call_args.kwargs["timeout"] == 5.0

    def test_caller_supplied_timeout_is_not_overridden(self):
        with mock.patch("robocorp.storage._requests.requests.Session.get") as mock_get:
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
            mock.patch("robocorp.storage._requests.requests.get") as mock_get,
            mock.patch(
                "robocorp.storage._requests.requests.Session.get"
            ) as mock_session_get,
        ):
            mock_session_get.__name__ = "get"
            mock_session_get.return_value.status_code = 200
            mock_session_get.return_value.ok = True

            _requests.Requests().get("https://example.com")

        mock_get.assert_not_called()
        mock_session_get.assert_called_once()


@pytest.fixture
def local_server():
    """A real HTTP/1.1 server that counts the connections it accepts."""
    state: dict = {"connections": 0, "hits": []}

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        timeout = 1  # close a keep-alive connection that is idle for 1 s

        def setup(self):
            state["connections"] += 1
            super().setup()

        def _ok(self):
            self.rfile.read(int(self.headers.get("Content-Length") or 0))
            state["hits"].append(f"{self.command} {self.path}")
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")

        do_GET = do_POST = _ok

        def log_message(self, *args):
            pass

    httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    state["url"] = f"http://127.0.0.1:{httpd.server_port}/"
    yield state
    httpd.shutdown()
    httpd.server_close()


class TestConnectionReuseOverRealSocket:
    def test_calls_reuse_one_connection(self, local_server):
        client = _requests.Requests(local_server["url"])

        client.post("reserve")
        client.get("payload")
        client.get("files")
        client.post("output", json={})
        client.post("release", json={})

        assert len(local_server["hits"]) == 5
        assert local_server["connections"] == 1

    def test_recovers_when_server_closed_the_idle_connection(self, local_server):
        client = _requests.Requests(local_server["url"])

        client.post("reserve")
        time.sleep(1.6)
        start = time.monotonic()
        client.post("release", json={})

        assert time.monotonic() - start < 1, "no retry back-off expected"
        assert local_server["hits"].count("POST /release") == 1
        assert local_server["connections"] == 2

    def test_connection_idle_past_the_limit_is_not_reused(
        self, local_server, monkeypatch
    ):
        monkeypatch.setattr(_requests, "MAX_IDLE", 0.2)
        client = _requests.Requests(local_server["url"])

        client.post("reserve")
        client.post("output", json={})
        assert local_server["connections"] == 1

        time.sleep(0.3)
        client.post("release", json={})

        assert local_server["connections"] == 2
        assert local_server["hits"].count("POST /release") == 1
