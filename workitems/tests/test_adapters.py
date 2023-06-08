# ruff: noqa: E501
import json
import logging
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import pytest
from requests import HTTPError

from robocorp.workitems._adapters import FileAdapter, RobocorpAdapter
from robocorp.workitems._requests import DEBUG, RequestsHTTPError
from robocorp.workitems._types import State

ITEMS_JSON = [{"payload": {"a-key": "a-value"}, "files": {"a-file": "file.txt"}}]


class TestFileAdapter:
    """Tests the local dev env `FileAdapter` on Work Items."""

    @contextmanager
    def _input_work_items(self):
        with tempfile.TemporaryDirectory() as datadir:
            items_in = os.path.join(datadir, "items.json")
            with open(items_in, "w") as fd:
                json.dump(ITEMS_JSON, fd)
            with open(os.path.join(datadir, "file.txt"), "w") as fd:
                fd.write("some mock content")

            output_dir = os.path.join(datadir, "output_dir")
            os.makedirs(output_dir)
            items_out = os.path.join(output_dir, "items-out.json")

            yield items_in, items_out

    @pytest.fixture(
        params=[
            ("RC_WORKITEM_INPUT_PATH", "RC_WORKITEM_OUTPUT_PATH"),
            ("RPA_INPUT_WORKITEM_PATH", "RPA_OUTPUT_WORKITEM_PATH"),
        ]
    )
    def adapter(self, monkeypatch, request):
        with self._input_work_items() as (items_in, items_out):
            monkeypatch.setenv(request.param[0], items_in)
            monkeypatch.setenv(request.param[1], items_out)
            yield FileAdapter()

    @staticmethod
    @pytest.fixture
    def empty_adapter():
        # No work items i/o files nor envs set.
        return FileAdapter()

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
        item_id = adapter.reserve_input()
        adapter.add_file(
            item_id,
            "secondfile.txt",
            original_name="secondfile2.txt",
            content=b"somedata",
        )
        assert adapter._inputs[0]["files"]["secondfile.txt"] == "secondfile2.txt"
        assert os.path.isfile(Path(adapter.input_path).parent / "secondfile2.txt")

    def test_save_data_input(self, adapter):
        item_id = adapter.reserve_input()
        adapter.save_payload(item_id, {"key": "value"})
        with open(adapter.input_path) as fd:
            data = json.load(fd)
            assert data == [
                {"payload": {"key": "value"}, "files": {"a-file": "file.txt"}}
            ]

    def test_save_data_output(self, adapter):
        item_id = adapter.create_output("0", {})
        adapter.save_payload(item_id, {"key": "value"})

        output = adapter.output_path
        assert os.path.isfile(output)
        with open(output) as fd:
            data = json.load(fd)
            assert data == [{"payload": {"key": "value"}, "files": {}}]

    def test_missing_file(self, monkeypatch):
        monkeypatch.setenv("RPA_WORKITEMS_PATH", "not-exist.json")
        adapter = FileAdapter()
        assert adapter._inputs == [{"payload": {}}]

    def test_empty_queue(self, monkeypatch):
        with tempfile.TemporaryDirectory() as datadir:
            items = os.path.join(datadir, "items.json")
            with open(items, "w") as fd:
                json.dump([], fd)

            monkeypatch.setenv("RPA_WORKITEMS_PATH", items)
            adapter = FileAdapter()
            assert adapter._inputs == [{"payload": {}}]

    def test_malformed_queue(self, monkeypatch):
        with tempfile.TemporaryDirectory() as datadir:
            items = os.path.join(datadir, "items.json")
            with open(items, "w") as fd:
                json.dump(["not-an-item"], fd)

            monkeypatch.setenv("RPA_WORKITEMS_PATH", items)
            adapter = FileAdapter()
            assert adapter._inputs == [{"payload": {}}]

    def test_without_items_paths(self, empty_adapter):
        assert empty_adapter._inputs == [{"payload": {}}]

        # Can't save inputs nor outputs since there's no path defined for them.
        with pytest.raises(RuntimeError):
            empty_adapter.save_payload("0", {"input": "value"})
        with pytest.raises(RuntimeError):
            _ = empty_adapter.output_path
        with pytest.raises(RuntimeError):
            empty_adapter.create_output("1", {"var": "some-value"})


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
        ) as mock_delete, mock.patch(
            "time.sleep", return_value=None
        ) as mock_sleep:
            self.mock_get = mock_get
            self.mock_post = mock_post
            self.mock_put = mock_put
            self.mock_delete = mock_delete

            self.mock_get.__name__ = "get"
            self.mock_post.__name__ = "post"
            self.mock_put.__name__ = "put"
            self.mock_delete.__name__ = "delete"

            self.mock_sleep = mock_sleep

            yield RobocorpAdapter()

    def test_reserve_input(self, adapter):
        initial_item_id = adapter.reserve_input()
        assert initial_item_id == self.ENV["RC_WORKITEM_ID"]

        self.mock_post.return_value.json.return_value = {"workItemId": "44"}
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
        resp.json.return_value = request.param[0]
        resp.raise_for_status.side_effect = request.param[1]
        return resp

    @pytest.fixture(
        params=[
            # Requests response attribute values for: `.json()`, `.raise_for_status()`
            ({}, None),
            (None, HTTPError()),
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

        with pytest.raises(RequestsHTTPError) as exc_info:
            adapter.list_files("4")
        assert exc_info.value.status_code == status_code
        assert self.mock_get.call_count == call_count  # tried once or 5 times in a row

    @pytest.fixture(
        params=[
            # Requests response attribute values for: `.json()`, `.raise_for_status()`
            ({"error": {"code": "UNEXPECTED_ERROR"}}, None),  # normal response
            ('{"error": {"code": "UNEXPECTED_ERROR"}}', None),  # double serialized
            (r'"{\"error\": {\"code\": \"UNEXPECTED_ERROR\"}}"', None),  # triple
            ('[{"some": "value"}]', HTTPError()),  # double serialized list
        ]
    )
    def failing_deserializing_response(self, request):
        return self._failing_response(request)

    def test_bad_response_payload(self, adapter, failing_deserializing_response):
        self.mock_get.return_value = failing_deserializing_response
        failing_deserializing_response.status_code = 429

        with pytest.raises(RequestsHTTPError) as exc_info:
            adapter.list_files("4")

        err = "UNEXPECTED_ERROR"
        call_count = 5
        if err not in str(failing_deserializing_response.json.return_value):
            err = "Error"  # default error message in the absence of it
        assert exc_info.value.status_code == 429
        assert exc_info.value.status_message == err
        assert self.mock_get.call_count == call_count

    def test_logging_and_sleeping(self, adapter, failing_response, caplog):
        assert DEBUG, 'This test should be ran with "RC_WORKITEM_DEBUG" on'

        # 1st call: raises 500 -> unexpected server crash, therefore needs retry
        #   (1 sleep)
        # 2nd call: now raises 429 -> rate limit hit, needs retry and sleeps extra
        #   (2 sleeps)
        # 3rd call: raises 400 -> malformed request, doesn't retry anymore and raises
        #   with last error, no sleeps performed
        status_code = mock.PropertyMock(side_effect=[500, 429, 400])
        type(failing_response).status_code = status_code
        failing_response.reason = "for no reason :)"
        self.mock_post.return_value = failing_response
        with pytest.raises(RequestsHTTPError) as exc_info:
            with caplog.at_level(logging.DEBUG):
                adapter.create_output("1")

        assert exc_info.value.status_code == 400  # last received server code
        assert self.mock_sleep.call_count == 3  # 1 sleep (500) + 2 sleeps (429)
        expected_logs = [
            "POST 'https://api.process.com/process-v1/workspaces/1/processes/5/work-items/1/output'",
            "API response: 500 'for no reason :)'",
            "API response: 429 'for no reason :)'",
            "API response: 400 'for no reason :)'",
        ]
        captured_logs = set(record.message for record in caplog.records)
        for expected_log in expected_logs:
            assert expected_log in captured_logs

    def test_add_get_file(self, adapter, success_response, caplog):
        """Uploads and retrieves files with AWS support.

        This way we check if sensitive information (like auth params) don't get
        exposed.
        """
        item_id = adapter.reserve_input()  # reserved initially from the env var
        file_name = "myfile.txt"
        file_content = b"some-data"

        # Behaviour for: adding a file (2x POST), getting the file (3x GET).
        #
        # POST #1: 201 - default error handling
        # POST #2: 201 - custom error handling -> status code retrieved
        # GET #1: 200 - default error handling
        # GET #2: 200 - default error handling
        # GET #3: 200 - custom error handling -> status code retrieved
        status_code = mock.PropertyMock(side_effect=[201, 200, 200])
        type(success_response).status_code = status_code
        # POST #1: JSON with file related data
        # POST #2: ignored response content
        # GET #1: JSON with all the file IDs
        # GET #2: JSON with the file URL corresponding to ID
        # GET #3: bytes response content (not ignored)
        post_data = {
            "url": "https://s3.eu-west-1.amazonaws.com/ci-4f23e-robocloud-td",
            "fields": {
                "dont": "care",
            },
        }
        get_files_data = [
            {
                "fileName": file_name,
                "fileId": "file-id",
            }
        ]
        get_file_data = {
            "url": "https://ci-4f23e-robocloud-td.s3.eu-west-1.amazonaws.com/files/ws_17/wi_0dd63f07-ba7b-414a-bf92-293080975d2f/file_eddfd9ac-143f-4eb9-888f-b9c378e67aec?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=secret-credentials",
        }
        success_response.json.side_effect = [post_data, get_files_data, get_file_data]
        success_response.content = file_content
        self.mock_post.return_value = self.mock_get.return_value = success_response

        # 2x POST (CR file entry, AWS file content)
        adapter.add_file(
            item_id,
            file_name,
            original_name="not-used.txt",
            content=file_content,
        )
        files = self.mock_post.call_args_list[-1][1]["files"]
        assert files == {"file": (file_name, file_content)}

        # 3x GET (all files, specific file, file content)
        content = adapter.get_file(item_id, file_name)
        assert content == file_content

        # Making sure sensitive info doesn't get exposed.
        exposed = any(
            "secret-credentials" in record.message for record in caplog.records
        )
        assert not exposed, "secret got exposed"
