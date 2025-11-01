# ruff: noqa: E501
import copy
import importlib
import json
import logging
import os
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import pytest
from requests import HTTPError as _HTTPError

from robocorp.workitems._adapters import FileAdapter, RobocorpAdapter, create_adapter
from robocorp.workitems._adapters._docdb import DocumentDBAdapter
from robocorp.workitems._adapters._redis import RedisAdapter
from robocorp.workitems._adapters._sqlite import SQLiteAdapter
from robocorp.workitems._requests import DEBUG, HTTPError
from robocorp.workitems._types import TTL_WEEK_SECONDS, State

from .mocks import MOCK_FILES, PAYLOAD_FIRST, PAYLOAD_SECOND

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

        with (
            mock.patch("robocorp.workitems._requests.requests.get") as mock_get,
            mock.patch("robocorp.workitems._requests.requests.post") as mock_post,
            mock.patch("robocorp.workitems._requests.requests.put") as mock_put,
            mock.patch("robocorp.workitems._requests.requests.delete") as mock_delete,
            mock.patch("time.sleep", return_value=None) as mock_sleep,
        ):
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


class TestAdapterFactory:
    def test_create_adapter_with_sqlite_alias(self, monkeypatch, tmp_path):
        db_path = tmp_path / "workitems.db"
        monkeypatch.setenv("RC_WORKITEM_ADAPTER", "sqlite")
        monkeypatch.setenv("RC_WORKITEM_DB_PATH", str(db_path))
        monkeypatch.setenv("RC_WORKITEM_QUEUE_NAME", "qa_forms")

        adapter = create_adapter()

        assert isinstance(adapter, SQLiteAdapter)

    def test_redis_adapter_requires_dependency(self, monkeypatch):
        module = importlib.import_module("robocorp.workitems._adapters._redis")
        monkeypatch.setattr(module, "_redis_lib", None)

        with pytest.raises(ImportError, match=r"robocorp-workitems\[redis\]"):
            RedisAdapter()

    def test_documentdb_adapter_requires_dependency(self, monkeypatch):
        module = importlib.import_module("robocorp.workitems._adapters._docdb")
        monkeypatch.setattr(module, "_pymongo_available", False)
        monkeypatch.setattr(module, "MongoClient", None)

        with pytest.raises(ImportError, match=r"robocorp-workitems\[docdb\]"):
            DocumentDBAdapter()


class TestSQLiteAdapter:
    """Integration tests for SQLiteAdapter with real database operations.

    Note: SQLite tests require no external services and run on all platforms.
    """

    @pytest.fixture
    def adapter(self, tmp_path, monkeypatch):
        """Create a SQLiteAdapter with a temporary database."""
        db_path = tmp_path / "test_workitems.db"
        files_dir = tmp_path / "files"
        monkeypatch.setenv("RC_WORKITEM_ADAPTER", "sqlite")
        monkeypatch.setenv("RC_WORKITEM_DB_PATH", str(db_path))
        monkeypatch.setenv("RC_WORKITEM_FILES_DIR", str(files_dir))
        monkeypatch.setenv("RC_WORKITEM_QUEUE_NAME", "test_queue")

        adapter = SQLiteAdapter()
        yield adapter

        # Cleanup - close connections if they exist
        if hasattr(adapter, "_connections"):
            adapter._connections.close()
        if db_path.exists():
            db_path.unlink()
        # Files directory will be cleaned up automatically with tmp_path

    @pytest.fixture
    def workitems(self, adapter):
        """Create workitems context with SQLiteAdapter."""
        from unittest import mock

        from robocorp import workitems
        from robocorp.workitems._context import Context

        # Seed test data with files (matching FileAdapter pattern)
        item1_id = adapter.seed_input(copy.deepcopy(PAYLOAD_FIRST))
        for name, content in MOCK_FILES["workitem-id-first"].items():
            adapter.add_file(item1_id, name, content)

        adapter.seed_input(copy.deepcopy(PAYLOAD_SECOND))

        # Create context with our adapter
        ctx = Context(adapter=adapter)
        ctx.reserve_input()

        def _getter():
            return ctx

        with mock.patch("robocorp.workitems._ctx", _getter):
            yield workitems

    def test_database_initialization(self, adapter):
        """Test that the database initializes with proper schema."""
        with adapter._pool.acquire() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = {row[0] for row in cursor.fetchall()}

        assert "work_items" in tables
        assert "work_item_files" in tables
        assert "schema_version" in tables

    def test_reserve_and_release_workflow(self, adapter):
        """Test full reserve → process → release workflow."""
        # Create item using seed_input helper
        item_id = adapter.seed_input({"data": "test"})

        # Reserve it
        reserved_id = adapter.reserve_input()
        assert reserved_id == item_id

        # Should not reserve again (no more pending items)
        from robocorp.workitems._exceptions import EmptyQueue

        with pytest.raises(EmptyQueue):
            adapter.reserve_input()

        # Release as done
        adapter.release_input(reserved_id, State.DONE)

        # Verify state
        with adapter._pool.acquire() as conn:
            cursor = conn.execute(
                "SELECT state FROM work_items WHERE id = ?", (reserved_id,)
            )
            row = cursor.fetchone()
            assert row[0] == State.DONE.value

    def test_payload_operations(self, adapter):
        """Test payload save and load."""
        # create_output goes to OUTPUT queue - that's fine for this test
        item_id = adapter.create_output(None, {"key": "original"})

        # Update payload
        new_payload = {"key": "updated", "extra": [1, 2, 3]}
        adapter.save_payload(item_id, new_payload)

        # Load and verify
        loaded = adapter.load_payload(item_id)
        assert loaded == new_payload

    def test_file_operations(self, adapter):
        """Test file upload and download."""
        item_id = adapter.create_output(None, {})

        # Add files
        adapter.add_file(item_id, "test.txt", b"Hello World")
        adapter.add_file(item_id, "data.bin", b"\x00\x01\x02\x03")

        # List files
        files = adapter.list_files(item_id)
        assert set(files) == {"test.txt", "data.bin"}

        # Get file content
        content = adapter.get_file(item_id, "test.txt")
        assert content == b"Hello World"

        # Remove file
        adapter.remove_file(item_id, "data.bin")
        files = adapter.list_files(item_id)
        assert files == ["test.txt"]

    def test_fifo_ordering(self, adapter):
        """Test that work items are reserved in FIFO order."""

        # Create multiple items using seed_input
        ids = []
        for i in range(5):
            item_id = adapter.seed_input({"order": i})
            ids.append(item_id)
            time.sleep(0.01)  # Ensure different timestamps

        # Reserve them in order
        reserved = []
        for _ in range(5):
            reserved_id = adapter.reserve_input()
            assert reserved_id is not None
            reserved.append(reserved_id)

        # Should match creation order
        assert reserved == ids

    def test_failed_work_item_release(self, adapter):
        """Test releasing work items as failed."""
        # Create item using seed_input
        adapter.seed_input({"will": "fail"})

        reserved_id = adapter.reserve_input()

        # Release as failed with exception
        exception = {"type": "ValueError", "message": "Invalid data"}
        adapter.release_input(reserved_id, State.FAILED, exception=exception)

        # Verify state and exception stored
        with adapter._pool.acquire() as conn:
            cursor = conn.execute(
                "SELECT state, exception_message FROM work_items WHERE id = ?",
                (reserved_id,),
            )
            row = cursor.fetchone()
            assert row[0] == State.FAILED.value
            assert row[1] == exception["message"]

    def test_producer_consumer_workflow(self, workitems):
        """Test full producer-consumer workflow using workitems API."""
        results = []

        # Consumer: process inputs
        for item in workitems.inputs:
            with item:
                results.append(item.payload)

        # Verify we processed both items
        assert len(results) == 2
        assert any(r.get("username") == PAYLOAD_FIRST["username"] for r in results)
        assert any(r.get("username") == PAYLOAD_SECOND["username"] for r in results)

        # Producer: create outputs
        output = workitems.outputs.create()
        output.payload = {"processed": len(results), "results": results}
        output.save()

        # Verify output was created
        assert len(list(workitems.outputs)) == 1

    def test_work_item_with_files(self, adapter):
        """Test work item file handling at adapter level (consistent with FileAdapter tests)."""
        # Create input using seed_input
        item_id = adapter.seed_input({"has_attachment": True})

        # Test add_file
        adapter.add_file(item_id, "document.pdf", b"PDF content here")

        # Test list_files
        files = adapter.list_files(item_id)
        assert "document.pdf" in files

        # Test get_file - should return bytes like FileAdapter
        content = adapter.get_file(item_id, "document.pdf")
        assert content == b"PDF content here"

        # Test remove_file
        adapter.add_file(item_id, "temp.txt", b"temporary")
        adapter.remove_file(item_id, "temp.txt")
        files = adapter.list_files(item_id)
        assert "temp.txt" not in files
        assert "document.pdf" in files

    def test_error_handling_file_not_found(self, adapter):
        """Test FileNotFoundError for non-existent files."""
        item_id = adapter.seed_input({})

        with pytest.raises(FileNotFoundError):
            adapter.get_file(item_id, "nonexistent.txt")

        with pytest.raises(FileNotFoundError):
            adapter.remove_file(item_id, "nonexistent.txt")

    def test_error_handling_file_already_exists(self, adapter):
        """Test FileExistsError when adding duplicate files."""
        item_id = adapter.seed_input({})
        adapter.add_file(item_id, "test.txt", b"content")

        with pytest.raises(FileExistsError):
            adapter.add_file(item_id, "test.txt", b"different content")

    def test_error_handling_invalid_work_item(self, adapter):
        """Test operations on non-existent work items."""
        fake_id = "nonexistent-item-id"

        with pytest.raises(ValueError):
            adapter.load_payload(fake_id)


def _create_redis_input_item(adapter, payload):
    """Helper to create item directly in Redis INPUT queue for testing."""
    import json
    import uuid
    from datetime import datetime

    item_id = str(uuid.uuid4())
    payload_json = json.dumps(payload or {})

    # Create item in INPUT queue (not output)
    adapter._client.hset(
        adapter._key("payload", queue=adapter._config.queue, item_id=item_id),
        mapping={
            "payload": payload_json,
            "queue_name": adapter._config.queue,
            "state": "PENDING",
        },
    )
    now = datetime.utcnow().isoformat()
    adapter._client.hset(
        adapter._key("timestamps", queue=adapter._config.queue, item_id=item_id),
        mapping={"created_at": now},
    )
    adapter._client.lpush(adapter._key("pending", queue=adapter._config.queue), item_id)
    adapter._client.set(
        adapter._key("origin", item_id=item_id),
        adapter._config.queue,
        ex=TTL_WEEK_SECONDS,
    )

    return item_id


@pytest.mark.redis
class TestRedisAdapter:
    """Integration tests for RedisAdapter with real Redis instance."""

    @pytest.fixture
    def adapter(self, monkeypatch):
        """Create a RedisAdapter connected to test Redis."""
        import redis  # type: ignore[import-not-found]

        redis_url = os.getenv("RC_REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("RC_WORKITEM_ADAPTER", "redis")
        monkeypatch.setenv("RC_REDIS_URL", redis_url)
        monkeypatch.setenv("RC_WORKITEM_QUEUE_NAME", "test_queue")

        # Clean up any existing test data - match actual key pattern
        client = redis.from_url(redis_url)
        keys = list(client.scan_iter("test_queue*"))
        if keys:
            client.delete(*keys)

        adapter = RedisAdapter()
        yield adapter

        # Cleanup after tests - match actual key pattern
        keys = list(client.scan_iter("test_queue*"))
        if keys:
            client.delete(*keys)
        client.close()

    @pytest.fixture
    def workitems(self, adapter):
        """Create workitems context with RedisAdapter."""
        from unittest import mock

        from robocorp import workitems
        from robocorp.workitems._context import Context

        # Seed test data in INPUT queue with files
        item1_id = adapter.seed_input(copy.deepcopy(PAYLOAD_FIRST))
        for name, content in MOCK_FILES["workitem-id-first"].items():
            adapter.add_file(item1_id, name, content)

        adapter.seed_input(copy.deepcopy(PAYLOAD_SECOND))

        # Create context with our adapter
        ctx = Context(adapter=adapter)
        ctx.reserve_input()

        def _getter():
            return ctx

        with mock.patch("robocorp.workitems._ctx", _getter):
            yield workitems

    def test_redis_connection(self, adapter):
        """Test that Redis connection is established."""
        # Should be able to ping
        assert adapter._client.ping()

    def test_reserve_and_release_workflow(self, adapter):
        """Test full reserve → process → release workflow with Redis."""
        item_id = adapter.seed_input({"data": "test"})

        # Reserve
        reserved_id = adapter.reserve_input()
        assert reserved_id == item_id

        # Should not reserve again (already reserved - queue is empty)
        from robocorp.workitems._exceptions import EmptyQueue

        with pytest.raises(EmptyQueue):
            adapter.reserve_input()

        # Release as done
        adapter.release_input(reserved_id, State.DONE)

        # Verify it's marked as done
        payload = adapter.load_payload(reserved_id)
        assert payload["data"] == "test"

    def test_payload_persistence(self, adapter):
        """Test payload save and load with Redis."""
        item_id = adapter.seed_input({"initial": "value"})

        # Update payload
        new_payload = {"updated": "data", "complex": {"nested": [1, 2, 3]}}
        adapter.save_payload(item_id, new_payload)

        # Load and verify
        loaded = adapter.load_payload(item_id)
        assert loaded == new_payload

    def test_file_operations_inline(self, adapter):
        """Test file operations with inline storage."""
        item_id = adapter.seed_input({})

        # Add files
        adapter.add_file(item_id, "small.txt", b"Small file content")
        adapter.add_file(item_id, "data.json", b'{"key": "value"}')

        # List files
        files = adapter.list_files(item_id)
        assert set(files) == {"small.txt", "data.json"}

        # Get file
        content = adapter.get_file(item_id, "small.txt")
        assert content == b"Small file content"

        # Remove file
        adapter.remove_file(item_id, "data.json")
        assert adapter.list_files(item_id) == ["small.txt"]

    def test_fifo_ordering(self, adapter):
        """Test FIFO queue ordering in Redis."""
        # Create multiple items
        ids = []
        for i in range(5):
            item_id = adapter.seed_input({"order": i})
            ids.append(item_id)

        # Reserve in order
        reserved = []
        for _ in range(5):
            reserved_id = adapter.reserve_input()
            assert reserved_id is not None
            reserved.append(reserved_id)

        assert reserved == ids

    def test_concurrent_reservation(self, adapter):
        """Test that concurrent reservations don't conflict."""
        # Create items
        for i in range(3):
            adapter.seed_input({"item": i})

        # First reservation
        id1 = adapter.reserve_input()
        assert id1 is not None

        # Second reservation should get different item
        id2 = adapter.reserve_input()
        assert id2 is not None
        assert id2 != id1

    def test_producer_consumer_workflow(self, workitems):
        """Test full workflow using workitems API with Redis backend."""
        results = []

        # Consumer
        for item in workitems.inputs:
            with item:
                results.append(item.payload)

        assert len(results) == 2
        assert any(r.get("username") == PAYLOAD_FIRST["username"] for r in results)
        assert any(r.get("username") == PAYLOAD_SECOND["username"] for r in results)

        # Producer
        output = workitems.outputs.create()
        output.payload = {"results": results}
        output.save()

    def test_exception_handling(self, adapter):
        """Test failed item with exception data."""
        adapter.seed_input({"will": "fail"})
        reserved_id = adapter.reserve_input()

        exception = {"type": "RuntimeError", "message": "Something went wrong"}
        adapter.release_input(reserved_id, State.FAILED, exception=exception)

        # Payload should still be accessible
        payload = adapter.load_payload(reserved_id)
        assert payload["will"] == "fail"

    def test_error_handling_file_not_found(self, adapter):
        """Test FileNotFoundError for non-existent files."""
        item_id = adapter.seed_input({})

        with pytest.raises(FileNotFoundError):
            adapter.get_file(item_id, "nonexistent.txt")

        with pytest.raises(FileNotFoundError):
            adapter.remove_file(item_id, "nonexistent.txt")

    def test_error_handling_file_already_exists(self, adapter):
        """Test FileExistsError when adding duplicate files."""
        item_id = adapter.seed_input({})
        adapter.add_file(item_id, "test.txt", b"content")

        with pytest.raises(FileExistsError):
            adapter.add_file(item_id, "test.txt", b"different content")

    def test_error_handling_invalid_work_item(self, adapter):
        """Test operations on non-existent work items."""
        fake_id = "nonexistent-item-id"

        with pytest.raises(ValueError):
            adapter.load_payload(fake_id)

        with pytest.raises(ValueError):
            adapter.save_payload(fake_id, {"data": "value"})


@pytest.mark.integration
@pytest.mark.docdb
class TestDocumentDBAdapter:
    """Integration tests for DocumentDBAdapter with real MongoDB instance."""

    @pytest.fixture
    def adapter(self, monkeypatch, tmp_path):
        """Create a DocumentDBAdapter connected to test MongoDB."""
        from pymongo import MongoClient  # type: ignore[import-not-found]

        mongo_url = os.getenv("RC_MONGO_URL", "mongodb://localhost:27017")
        mongo_db = os.getenv("RC_MONGO_DB", "workitems_test")

        # Set DocumentDBAdapter environment variables
        monkeypatch.setenv("DOCDB_URI", mongo_url)
        monkeypatch.setenv("DOCDB_DATABASE", mongo_db)
        monkeypatch.setenv("RC_WORKITEM_QUEUE_NAME", "test_queue")
        monkeypatch.setenv("RC_WORKITEM_FILES_DIR", str(tmp_path / "files"))

        # Clean up test database
        client = MongoClient(mongo_url)
        db = client[mongo_db]
        for coll_name in db.list_collection_names():
            if coll_name.startswith("test_"):
                db[coll_name].drop()

        adapter = DocumentDBAdapter()
        yield adapter

        # Cleanup
        for coll_name in db.list_collection_names():
            if coll_name.startswith("test_"):
                db[coll_name].drop()
        client.close()

    @pytest.fixture
    def workitems(self, adapter):
        """Create workitems context with DocumentDBAdapter."""
        from unittest import mock

        from robocorp import workitems
        from robocorp.workitems._context import Context

        # Seed test data with files
        item1_id = adapter.seed_input(copy.deepcopy(PAYLOAD_FIRST))
        for name, content in MOCK_FILES["workitem-id-first"].items():
            adapter.add_file(item1_id, name, content)

        adapter.seed_input(copy.deepcopy(PAYLOAD_SECOND))

        # Create context with our adapter
        ctx = Context(adapter=adapter)
        ctx.reserve_input()

        def _getter():
            return ctx

        with mock.patch("robocorp.workitems._ctx", _getter):
            yield workitems

    def test_mongodb_connection(self, adapter):
        """Test MongoDB connection and database access."""
        # Should be able to ping
        result = adapter._client.admin.command("ping")
        assert result["ok"] == 1.0

    def test_reserve_and_release_workflow(self, adapter):
        """Test full workflow with DocumentDB."""
        from robocorp.workitems._exceptions import EmptyQueue

        item_id = adapter.seed_input({"data": "mongodb"})

        # Reserve
        reserved_id = adapter.reserve_input()
        assert reserved_id == item_id

        # Should raise EmptyQueue when no more items
        with pytest.raises(EmptyQueue):
            adapter.reserve_input()

        # Release
        adapter.release_input(reserved_id, State.DONE)

        # Verify in database
        coll = adapter._collection()
        doc = coll.find_one({"item_id": reserved_id})
        assert doc["state"] == State.DONE.value

    def test_payload_operations(self, adapter):
        """Test payload save/load with MongoDB."""
        item_id = adapter.seed_input({"initial": "data"})

        # Update with complex payload
        new_payload = {
            "updated": True,
            "nested": {"array": [1, 2, 3], "string": "value"},
            "number": 42.5,
        }
        adapter.save_payload(item_id, new_payload)

        # Load and verify
        loaded = adapter.load_payload(item_id)
        assert loaded == new_payload

    def test_file_operations_gridfs(self, adapter):
        """Test file operations using GridFS."""
        item_id = adapter.seed_input({})

        # Add files (will use GridFS for larger files)
        large_content = b"X" * 10000  # Force GridFS usage
        adapter.add_file(item_id, "large.bin", large_content)
        adapter.add_file(item_id, "small.txt", b"Small")

        # List files
        files = adapter.list_files(item_id)
        assert set(files) == {"large.bin", "small.txt"}

        # Get file from GridFS
        content = adapter.get_file(item_id, "large.bin")
        assert content == large_content

        # Remove file
        adapter.remove_file(item_id, "large.bin")
        files = adapter.list_files(item_id)
        assert files == ["small.txt"]

    def test_fifo_ordering(self, adapter):
        """Test FIFO ordering with MongoDB queries."""
        ids = []
        for i in range(5):
            item_id = adapter.seed_input({"order": i})
            ids.append(item_id)

        # Reserve in order
        reserved = []
        for _ in range(5):
            reserved_id = adapter.reserve_input()
            assert reserved_id is not None
            reserved.append(reserved_id)

        assert reserved == ids

    def test_atomic_reservation(self, adapter):
        """Test that find_one_and_update provides atomic reservations."""
        # Create items
        for i in range(3):
            adapter.seed_input({"item": i})

        # Multiple reservations should get unique items
        id1 = adapter.reserve_input()
        id2 = adapter.reserve_input()
        id3 = adapter.reserve_input()

        assert len({id1, id2, id3}) == 3  # All unique

    def test_producer_consumer_workflow(self, workitems):
        """Test full workflow using workitems API with DocumentDB backend."""
        results = []

        # Consumer
        for item in workitems.inputs:
            with item:
                results.append(item.payload)

        assert len(results) == 2
        assert any(r.get("username") == PAYLOAD_FIRST["username"] for r in results)
        assert any(r.get("username") == PAYLOAD_SECOND["username"] for r in results)

        # Producer
        output = workitems.outputs.create()
        output.payload = {"results": results, "count": len(results)}
        output.save()

        # Verify in database
        outputs = list(workitems.outputs)
        assert len(outputs) == 1
        assert outputs[0].payload["count"] == 2

    def test_exception_storage(self, adapter):
        """Test storing exception data in MongoDB."""
        adapter.seed_input({})
        reserved_id = adapter.reserve_input()

        exception = {
            "type": "Exception",
            "message": "Test error",
            "traceback": "line 1\nline 2\nline 3",
        }
        adapter.release_input(reserved_id, State.FAILED, exception=exception)

        # Verify exception stored
        coll = adapter._collection()
        doc = coll.find_one({"item_id": reserved_id})
        assert doc["state"] == State.FAILED.value
        assert "exception" in doc
        assert exception["message"] in str(doc["exception"])

    def test_error_handling_file_not_found(self, adapter):
        """Test FileNotFoundError for non-existent files."""
        item_id = adapter.seed_input({})

        with pytest.raises(FileNotFoundError):
            adapter.get_file(item_id, "nonexistent.txt")

        with pytest.raises(FileNotFoundError):
            adapter.remove_file(item_id, "nonexistent.txt")

    def test_error_handling_file_already_exists(self, adapter):
        """Test FileExistsError when adding duplicate files."""
        item_id = adapter.seed_input({})
        adapter.add_file(item_id, "test.txt", b"content")

        with pytest.raises(FileExistsError):
            adapter.add_file(item_id, "test.txt", b"different content")

    def test_error_handling_invalid_work_item(self, adapter):
        """Test operations on non-existent work items."""
        fake_id = "nonexistent-item-id"

        with pytest.raises(ValueError):
            adapter.load_payload(fake_id)

        with pytest.raises(ValueError):
            adapter.save_payload(fake_id, {"data": "value"})

    def test_missing_document_during_file_access(self, adapter):
        """Ensure cached queue entries still raise clean errors when docs vanish."""

        item_id = adapter.seed_input({"with": "files"})

        # Populate cache by listing files (forces queue resolution)
        adapter.list_files(item_id)

        # Remove the document directly to simulate an external deletion
        adapter._collection().delete_one({"item_id": item_id})

        with pytest.raises(ValueError):
            adapter.get_file(item_id, "ghost.txt")

        with pytest.raises(ValueError):
            adapter.remove_file(item_id, "ghost.txt")

    def test_file_size_threshold_inline_vs_gridfs(self, adapter):
        """Test that files are stored inline vs GridFS based on size threshold."""
        item_id = adapter.seed_input({})

        # Small file - should be inline (base64)
        small_content = b"Small file content"
        adapter.add_file(item_id, "small.txt", small_content)

        # Large file - should use GridFS (over 1MB threshold)
        large_content = b"X" * (adapter._config.file_threshold + 1000)
        adapter.add_file(item_id, "large.bin", large_content)

        # Both should be retrievable
        assert adapter.get_file(item_id, "small.txt") == small_content
        assert adapter.get_file(item_id, "large.bin") == large_content

        # Check storage method by inspecting document
        coll = adapter._collection()
        doc = coll.find_one({"item_id": item_id})

        # Small file should be base64 string
        assert isinstance(doc["files"]["small.txt"], str)

        # Large file should be GridFS reference
        assert isinstance(doc["files"]["large.bin"], dict)
        assert "gridfs_id" in doc["files"]["large.bin"]
