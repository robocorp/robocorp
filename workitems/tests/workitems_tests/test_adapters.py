# ruff: noqa: E501
import json
import logging
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import pytest
from requests import HTTPError as _HTTPError

from robocorp.workitems._adapters import FileAdapter, RobocorpAdapter
from robocorp.workitems._requests import DEBUG, HTTPError
from robocorp.workitems._types import State

ITEMS_JSON = [{"payload": {"a-key": "a-value"}, "files": {"a-file": "file.txt"}}]


class TestFileAdapter:
    """Tests the local dev env `FileAdapter` on Work Items."""

    @contextmanager
    def _mock_work_items(self):
        with tempfile.TemporaryDirectory() as items_dir:
            items_dir = Path(items_dir)

            items_in = items_dir / "items.json"
            items_out = items_dir / "items.out.json"

            with open(items_in, "w") as fd:
                json.dump(ITEMS_JSON, fd)
            with open(os.path.join(items_dir, "file.txt"), "w") as fd:
                fd.write("some mock content")

            yield items_in, items_out

    @pytest.fixture(
        params=[
            ("RC_WORKITEM_INPUT_PATH", "RC_WORKITEM_OUTPUT_PATH"),
            ("RPA_INPUT_WORKITEM_PATH", "RPA_OUTPUT_WORKITEM_PATH"),
        ]
    )
    def adapter(self, monkeypatch, request):
        with self._mock_work_items() as (items_in, items_out):
            monkeypatch.setenv(request.param[0], str(items_in))
            monkeypatch.setenv(request.param[1], str(items_out))
            yield FileAdapter()

    @pytest.fixture
    def workitems(self, adapter):
        from robocorp import workitems

        ctx = workitems.Context(adapter=adapter)
        ctx.reserve_input()

        with mock.patch("robocorp.workitems._ctx", lambda: ctx):
            yield workitems

    def test_load_data(self, adapter):
        item_id = adapter.reserve_input()
        data = adapter.load_payload(item_id)
        assert data == {"a-key": "a-value"}

    def test_list_files(self, adapter):
        item_id = adapter.reserve_input()
        files = adapter.list_files(item_id)
        assert files == ["a-file"]

    def test_get_file(self, adapter):
        item_id = adapter.reserve_input()
        content = adapter.get_file(item_id, "a-file")
        assert content == b"some mock content"

    def test_add_file(self, adapter):
        item_id = adapter.create_output("0")
        adapter.add_file(
            item_id,
            "secondfile.txt",
            content=b"somedata",
        )
        assert adapter._outputs[0]["files"]["secondfile.txt"] == "secondfile.txt"
        assert os.path.isfile(Path(adapter._output_path).parent / "secondfile.txt")

    def test_save_data_input(self, adapter):
        item_id = adapter.reserve_input()
        adapter.save_payload(item_id, {"key": "value"})
        with open(adapter._input_path) as fd:
            data = json.load(fd)
            assert data == [
                {"payload": {"key": "value"}, "files": {"a-file": "file.txt"}}
            ]

    def test_save_data_output(self, adapter):
        item_id = adapter.create_output("0", {})
        adapter.save_payload(item_id, {"key": "value"})

        output = adapter._output_path
        assert os.path.isfile(output)
        with open(output) as fd:
            data = json.load(fd)
            assert data == [{"payload": {"key": "value"}, "files": {}}]

    def test_missing_file(self, monkeypatch):
        monkeypatch.setenv("RC_WORKITEM_INPUT_PATH", "not-exist.json")
        with pytest.raises(ValueError):
            FileAdapter()

    def test_empty_queue(self, monkeypatch):
        with tempfile.TemporaryDirectory() as items_dir:
            items = os.path.join(items_dir, "items.json")
            with open(items, "w") as fd:
                json.dump([], fd)

            monkeypatch.setenv("RC_WORKITEM_INPUT_PATH", items)
            with pytest.raises(ValueError):
                FileAdapter()

    def test_malformed_queue(self, monkeypatch):
        with tempfile.TemporaryDirectory() as items_dir:
            items = os.path.join(items_dir, "items.json")
            with open(items, "w") as fd:
                json.dump(["not-an-item"], fd)

            monkeypatch.setenv("RC_WORKITEM_INPUT_PATH", items)
            with pytest.raises(ValueError):
                FileAdapter()

    def test_missing_parent_directory(self, monkeypatch):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, "not-exist", "output.json")
            monkeypatch.setenv("RC_WORKITEM_OUTPUT_PATH", output_dir)

            # Should not raise
            adapter = FileAdapter()
            adapter.create_output("0", {"key": "value"})

    def test_invalid_reporter(self, workitems):
        results = []
        for work_item in workitems.inputs:
            with work_item:
                results.append(work_item.payload)

        with pytest.raises(ValueError):
            output = workitems.outputs.create()
            output.payload = {"results": results}
            output.save()

    def test_valid_reporter(self, workitems):
        output = workitems.outputs.create()

        results = []
        for work_item in workitems.inputs:
            with work_item:
                results.append(work_item.payload)

        output.payload = {"results": results}
        output.save()


class TestRobocorpAdapter:
    """Test control room API calls and retrying behaviour."""

    ENV = {
        "RC_WORKSPACE_ID": "1",
        "RC_PROCESS_RUN_ID": "2",
        "RC_ACTIVITY_RUN_ID": "3",
        "RC_WORKITEM_ID": "4",
        "RC_API_WORKITEM_HOST": "https://api.workitem.com",
        "RC_API_WORKITEM_TOKEN": "workitem-token",
        "RC_API_PROCESS_HOST": "https://api.process.com",
        "RC_API_PROCESS_TOKEN": "process-token",
        "RC_PROCESS_ID": "5",
    }

    HEADERS_WORKITEM = {
        "Authorization": f"Bearer {ENV['RC_API_WORKITEM_TOKEN']}",
        "Content-Type": "application/json",
    }
    HEADERS_PROCESS = {
        "Authorization": f"Bearer {ENV['RC_API_PROCESS_TOKEN']}",
        "Content-Type": "application/json",
    }

    @pytest.fixture
    def adapter(self, monkeypatch):
        for name, value in self.ENV.items():
            monkeypatch.setenv(name, value)

        with mock.patch(
            "robocorp.workitems._requests.requests.get"
        ) as mock_get, mock.patch(
            "robocorp.workitems._requests.requests.post"
        ) as mock_post, mock.patch(
            "robocorp.workitems._requests.requests.put"
        ) as mock_put, mock.patch(
            "robocorp.workitems._requests.requests.delete"
        ) as mock_delete, mock.patch("time.sleep", return_value=None) as mock_sleep:
            self.mock_get = mock_get
            self.mock_post = mock_post
            self.mock_put = mock_put
            self.mock_delete = mock_delete

            self.mock_get.__name__ = "get"
            self.mock_post.__name__ = "post"
            self.mock_put.__name__ = "put"
            self.mock_delete.__name__ = "delete"

            self.mock_get.return_value.status_code = 200
            self.mock_post.return_value.status_code = 200
            self.mock_put.return_value.status_code = 200
            self.mock_delete.return_value.status_code = 200

            self.mock_sleep = mock_sleep

            yield RobocorpAdapter()

    def test_reserve_input(self, adapter):
        initial_item_id = adapter.reserve_input()
        assert initial_item_id == self.ENV["RC_WORKITEM_ID"]

        response = self.mock_post.return_value
        response.status_code = 200
        response.json.return_value = {"workItemId": "44"}

        reserved_item_id = adapter.reserve_input()
        assert reserved_item_id == "44"

        url = "https://api.process.com/process-v1/workspaces/1/processes/5/runs/2/robotRuns/3/reserve-next-work-item"
        self.mock_post.assert_called_once_with(url, headers=self.HEADERS_PROCESS)

    @pytest.mark.parametrize(
        "exception",
        [None, {"type": "BUSINESS", "code": "INVALID_DATA", "message": None}],
    )
    def test_release_input(self, adapter, exception):
        item_id = "26"
        adapter.release_input(
            item_id,
            State.FAILED,
            exception=exception.copy() if exception else exception,
        )

        url = "https://api.process.com/process-v1/workspaces/1/processes/5/runs/2/robotRuns/3/release-work-item"
        body = {
            "workItemId": item_id,
            "state": State.FAILED.value,
        }
        if exception:
            body["exception"] = {
                key: value for (key, value) in exception.items() if value
            }
        self.mock_post.assert_called_once_with(
            url, headers=self.HEADERS_PROCESS, json=body
        )

    def test_load_payload(self, adapter):
        item_id = "4"
        expected_payload = {"name": "value"}
        self.mock_get.return_value.json.return_value = expected_payload
        payload = adapter.load_payload(item_id)
        assert payload == expected_payload

        response = self.mock_get.return_value
        response.ok = False
        response.status_code = 404
        payload = adapter.load_payload(item_id)
        assert payload == {}

    def test_save_payload(self, adapter):
        item_id = "1993"
        payload = {"Cosmin": "Poieana"}
        adapter.save_payload(item_id, payload)

        url = f"https://api.workitem.com/json-v1/workspaces/1/workitems/{item_id}/data"
        self.mock_put.assert_called_once_with(
            url, headers=self.HEADERS_WORKITEM, json=payload
        )

    def test_remove_file(self, adapter):
        item_id = "44"
        name = "procrastination.txt"
        file_id = "88"
        self.mock_get.return_value.json.return_value = [
            {"fileName": name, "fileId": file_id}
        ]
        adapter.remove_file(item_id, name)

        url = f"https://api.workitem.com/json-v1/workspaces/1/workitems/{item_id}/files/{file_id}"
        self.mock_delete.assert_called_once_with(url, headers=self.HEADERS_WORKITEM)

    def test_list_files(self, adapter):
        expected_files = ["just.py", "mark.robot", "it.txt"]
        self.mock_get.return_value.json.return_value = [
            {"fileName": expected_files[0], "fileId": "1"},
            {"fileName": expected_files[1], "fileId": "2"},
            {"fileName": expected_files[2], "fileId": "3"},
        ]
        files = adapter.list_files("4")
        assert files == expected_files

    @staticmethod
    def _failing_response(request):
        resp = mock.MagicMock()
        resp.ok = False
        resp.text = json.dumps(request.param[0])
        resp.json.return_value = request.param[0]
        resp.raise_for_status.side_effect = request.param[1]
        return resp

    @pytest.fixture(
        params=[
            # Requests response attribute values for: `.json()`, `.raise_for_status()`
            ({}, None),
            (None, _HTTPError()),
        ]
    )
    def failing_response(self, request):
        return self._failing_response(request)

    @staticmethod
    @pytest.fixture
    def success_response():
        resp = mock.MagicMock()
        resp.ok = True
        return resp

    @pytest.mark.parametrize(
        "status_code,call_count",
        [
            # Retrying enabled:
            (429, 5),
            (500, 5),
            # Retrying disabled:
            (400, 1),
            (401, 1),
            (403, 1),
            (409, 1),
        ],
    )
    def test_list_files_retrying(
        self, adapter, failing_response, status_code, call_count
    ):
        self.mock_get.return_value = failing_response
        failing_response.status_code = status_code

        with pytest.raises(HTTPError) as exc_info:
            adapter.list_files("4")
        assert exc_info.value.status_code == status_code
        assert self.mock_get.call_count == call_count  # tried once or 5 times in a row

    @pytest.fixture(
        params=[
            # Requests response attribute values for: `.json()`, `.raise_for_status()`
            ({"error": {"code": "UNEXPECTED_ERROR"}}, None),  # normal response
            ('{"error": {"code": "UNEXPECTED_ERROR"}}', None),  # double serialized
            (r'"{\"error\": {\"code\": \"UNEXPECTED_ERROR\"}}"', None),  # triple
            ('[{"some": "value"}]', _HTTPError()),  # double serialized list
        ]
    )
    def failing_deserializing_response(self, request):
        return self._failing_response(request)

    def test_bad_response_payload(self, adapter, failing_deserializing_response):
        self.mock_get.return_value = failing_deserializing_response
        failing_deserializing_response.status_code = 429

        with pytest.raises(HTTPError) as exc_info:
            adapter.list_files("4")

        assert exc_info.value.status_code == 429
        assert exc_info.value.message == failing_deserializing_response.text
        assert self.mock_get.call_count == 5

    def test_logging_and_sleeping(self, adapter, caplog):
        assert DEBUG, 'This test should be ran with "RC_DEBUG" on'

        def error_response(status_code):
            mm = mock.MagicMock()
            mm.ok = False
            mm.status_code = status_code
            mm.reason = "test reason"
            mm.text = "test reason"
            return mm

        # 1st call: raises 500 -> unexpected server crash, therefore needs retry
        #   (1 sleep)
        # 2nd call: now raises 429 -> rate limit hit, needs retry and sleeps extra
        #   (2 sleeps)
        # 3rd call: raises 400 -> malformed request, doesn't retry anymore and raises
        #   with last error, no sleeps performed
        self.mock_post.side_effect = [
            error_response(500),
            error_response(429),
            error_response(400),
        ]

        with pytest.raises(HTTPError) as exc_info:
            with caplog.at_level(logging.DEBUG):
                adapter.create_output("1")

        assert exc_info.value.status_code == 400  # last received server code
        assert self.mock_sleep.call_count == 3  # 1 sleep (500) + 2 sleeps (429)
        expected_logs = [
            "POST 'https://api.process.com/process-v1/workspaces/1/processes/5/work-items/1/output'",
            "Server error: 500 'test reason'",
            "Client error: 429 'test reason'",
            "Client error: 400 'test reason'",
        ]
        captured_logs = set(record.message for record in caplog.records)
        for expected_log in expected_logs:
            assert expected_log in captured_logs

    def test_add_get_file(self, adapter, caplog):
        """Uploads and retrieves files with AWS support.

        This way we check if sensitive information (like auth params) don't get
        exposed.
        """
        item_id = adapter.reserve_input()  # reserved initially from the env var
        file_name = "myfile.txt"
        file_content = b"some-data"

        def success_response(status_code, json_value, content=None):
            mm = mock.MagicMock()
            mm.ok = True
            mm.status_code = status_code
            mm.json.return_value = json_value
            mm.content = content
            return mm

        # Adding a file
        # POST #1: Response: JSON with file related data
        # POST #2: Response: Ignored
        self.mock_post.side_effect = [
            success_response(
                201,
                {
                    "url": "https://s3.eu-west-1.amazonaws.com/ci-4f23e-robocloud-td",
                    "fields": {
                        "dont": "care",
                    },
                },
            ),
            success_response(201, {}),
        ]

        adapter.add_file(item_id, file_name, content=file_content)
        files = self.mock_post.call_args_list[-1][1]["files"]
        assert files == {"file": (file_name, file_content)}

        # Reading a file
        # GET #1: Response: JSON with all the file IDs
        # GET #2: Response: JSON with the file URL corresponding to ID
        # GET #3: Response: Bytes response content
        self.mock_get.side_effect = [
            success_response(
                200,
                [
                    {
                        "fileName": file_name,
                        "fileId": "file-id",
                    }
                ],
            ),
            success_response(
                200,
                {
                    "url": "https://ci-4f23e-robocloud-td.s3.eu-west-1.amazonaws.com/files/ws_17/wi_0dd63f07-ba7b-414a-bf92-293080975d2f/file_eddfd9ac-143f-4eb9-888f-b9c378e67aec?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=secret-credentials",
                },
            ),
            success_response(200, {}, file_content),
        ]

        content = adapter.get_file(item_id, file_name)
        assert content == file_content

        # Making sure sensitive info doesn't get exposed.
        exposed = any(
            "secret-credentials" in record.message for record in caplog.records
        )
        assert not exposed, "secret got exposed"

    def test_no_explicit_verify(self, adapter):
        adapter.save_payload("some-id", {})
        call = self.mock_put.call_args

        assert "verify" not in call.kwargs

    @pytest.mark.parametrize(
        "value,disabled",
        [
            ("no", True),
            ("off", True),
            ("1", True),
            ("0", True),
            ("yes please I'd like to disable it", True),
            (" ", True),
            ("", False),
        ],
    )
    def test_disable_ssl_verify(self, adapter, value, disabled):
        with mock.patch.dict(os.environ, {"RC_DISABLE_SSL": value}):
            adapter.save_payload("some-id", {})
            call = self.mock_put.call_args

            if disabled:
                assert call.kwargs["verify"] is False
            else:
                assert "verify" not in call.kwargs
