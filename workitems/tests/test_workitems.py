import copy
import json
import logging
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

try:
    from contextlib import nullcontext
except ImportError:
    from contextlib import suppress as nullcontext

import pytest
from requests import HTTPError

from robocorp.workitems import inputs as _inputs
from robocorp.workitems import outputs as _outputs
from robocorp.workitems._adapters import (
    BaseAdapter,
    FileAdapter,
    RobocorpAdapter,
)
from robocorp.workitems._context import Context
from robocorp.workitems._requests import DEBUG, RequestsHTTPError
from robocorp.workitems._exceptions import EmptyQueue
from robocorp.workitems._types import State, ExceptionType

from . import RESOURCES_DIR, RESULTS_DIR

VARIABLES_FIRST = {"username": "testguy", "address": "guy@company.com"}
VARIABLES_SECOND = {"username": "another", "address": "dude@company.com"}
IN_OUT_ID = "workitem-id-out"
VALID_DATA = {
    "workitem-id-first": VARIABLES_FIRST,
    "workitem-id-second": VARIABLES_SECOND,
    IN_OUT_ID: [1, 2, 3],
}
VALID_FILES = {
    "workitem-id-first": {
        "file1.txt": b"data1",
        "file2.txt": b"data2",
        "file3.png": b"data3",
    },
    "workitem-id-second": {},
    IN_OUT_ID: {},
}
ITEMS_JSON = [{"payload": {"a-key": "a-value"}, "files": {"a-file": "file.txt"}}]
FAILURE_ATTRIBUTES = {"status": "FAIL", "message": "The task/suite has failed"}

OUTPUT_DIR = RESULTS_DIR / "output_dir"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


@contextmanager
def temp_filename(content=None, **kwargs):
    """Create temporary file and yield file relative path, then delete it afterwards.
    Needs to close file handle, since Windows won't allow multiple
    open handles to the same file.
    """
    with tempfile.NamedTemporaryFile(delete=False, **kwargs) as fd:
        path = fd.name
        if content:
            fd.write(content)

    try:
        yield path
    finally:
        os.unlink(path)


def is_equal_files(lhs, rhs):
    lhs = Path(lhs).resolve()
    rhs = Path(rhs).resolve()
    return lhs == rhs


class MockAdapter(BaseAdapter):
    DATA = {}
    FILES = {}
    INDEX = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._data_keys = []
        self.releases = []

    @classmethod
    def validate(cls, item, key, val):
        data = cls.DATA.get(item.id)
        assert data is not None
        assert data[key] == val

    @property
    def data_keys(self):
        if not self._data_keys:
            self._data_keys = list(self.DATA.keys())
        return self._data_keys

    def reserve_input(self) -> str:
        if self.INDEX >= len(self.data_keys):
            raise EmptyQueue("No work items in the input queue")

        try:
            return self.data_keys[self.INDEX]
        finally:
            self.INDEX += 1

    def release_input(self, item_id: str, state: State, exception: dict = None):
        self.releases.append((item_id, state, exception))  # purely for testing purposes

    def create_output(self, parent_id, payload=None) -> str:
        self.save_payload(IN_OUT_ID, payload)
        return IN_OUT_ID

    def load_payload(self, item_id):
        return self.DATA[item_id]

    def save_payload(self, item_id, payload):
        self.DATA[item_id] = payload

    def list_files(self, item_id):
        return self.FILES[item_id]

    def get_file(self, item_id, name):
        return self.FILES[item_id][name]

    def add_file(self, item_id, name, *, original_name, content):
        self.FILES[item_id][name] = content

    def remove_file(self, item_id, name):
        del self.FILES[item_id][name]


class TestLibrary:

    @staticmethod
    @pytest.fixture
    def adapter():
        MockAdapter.DATA = copy.deepcopy(VALID_DATA)
        MockAdapter.FILES = copy.deepcopy(VALID_FILES)
        try:
            yield MockAdapter
        finally:
            MockAdapter.DATA = {}
            MockAdapter.FILES = {}
            MockAdapter.INDEX = 0

    @staticmethod
    @pytest.fixture
    def context(adapter):
        ctx = Context(default_adapter=adapter)

        def _getter():
            return ctx

        with mock.patch('robocorp.workitems._context', _getter):
            yield ctx

    @staticmethod
    @pytest.fixture
    def inputs(context):
        _inputs._ctx = context
        yield _inputs

    @staticmethod
    @pytest.fixture
    def outputs(context):
        _outputs._ctx = context
        yield _outputs

    @staticmethod
    def _get_resource_data(name, binary=False):
        path = RESOURCES_DIR / "work-items" / name
        if binary:
            return path.read_bytes()
        else:
            return path.read_text(encoding="utf-8")

    @classmethod
    @pytest.fixture(
        params=[
            ("mail-text.txt", "A message from e-mail"),
            ("mail-json.txt", {"message": "from email"}),
            ("mail-yaml.txt", {"message": "from email", "extra": {"value": 1}}),
        ]
    )
    def raw_email_data(cls, request):
        filename, expected_body = request
        content = cls._get_resource_data(filename)
        return content, expected_body

    @classmethod
    @pytest.fixture(
        params=[
            ("email.text", False, "A message from e-mail"),
            ("__mail.html", True, "from email"),
        ]
    )
    def parsed_email_data(cls, request):
        key, is_attachment, expected_body = request
        content = None
        if is_attachment:
            content = cls._get_resource_data(key, binary=True)
        return key, content, expected_body

    def test_inputs_reserve(self, inputs):
        with inputs.reserve() as first:
            assert first.payload == VARIABLES_FIRST
            assert first == inputs.current
            assert not first.released
        assert first.released

        second = inputs.reserve()
        assert second.payload == VARIABLES_SECOND
        assert second == inputs.current
        assert not second.released

    def test_inputs_iter(self, inputs):
        items = []
        for item in inputs:
            items.append(item)

        assert len(items) == 3
        assert all(item.released for item in items)

    def test_inputs_released(self, inputs):
        # Exhaust all items
        _ = list(inputs)

        assert len(inputs.released) == 3

    def test_keyword_save_work_item(self, library):
        item = library.get_input_work_item()
        for key, value in VARIABLES_FIRST.items():
            MockAdapter.validate(item, key, value)

        modified = {"username": "changed", "address": "dude@company.com"}
        item.payload = modified

        library.save_work_item()
        for key, value in modified.items():
            MockAdapter.validate(item, key, value)

    def test_no_active_item(self):
        library = WorkItems(default_adapter=MockAdapter)
        with pytest.raises(RuntimeError) as err:
            library.save_work_item()

        assert str(err.value) == "No active work item"

    def test_list_variables(self, library):
        library.get_input_work_item()

        names = library.list_work_item_variables()

        assert len(names) == 2
        assert "username" in names
        assert "address" in names

    def test_get_variables(self, library):
        library.get_input_work_item()

        value = library.get_work_item_variable("username")
        assert value == "testguy"

        with pytest.raises(KeyError):
            library.get_work_item_variable("notexist")

    def test_get_variables_default(self, library):
        library.get_input_work_item()

        value = library.get_work_item_variable("username", default="doesntmatter")
        assert value == "testguy"

        value = library.get_work_item_variable("notexist", default="doesmatter")
        assert value == "doesmatter"

    def test_delete_variables(self, library):
        library.get_input_work_item()
        assert "username" in library.list_work_item_variables()

        library.delete_work_item_variables("username")
        assert "username" not in library.list_work_item_variables()

        library.delete_work_item_variables("doesntexist")

        with pytest.raises(KeyError):
            library.delete_work_item_variables("doesntexist", force=False)

    def test_delete_variables_single(self, library):
        library.get_input_work_item()

        assert "username" in library.list_work_item_variables()
        assert len(library.current.payload) == 2

        library.delete_work_item_variables("username")

        assert "username" not in library.list_work_item_variables()
        assert len(library.current.payload) == 1

    def test_delete_variables_multiple(self, library):
        library.get_input_work_item()

        names = library.list_work_item_variables()
        assert "username" in names
        assert "address" in names
        assert len(names) == 2

        library.delete_work_item_variables("username", "address")

        names = library.list_work_item_variables()
        assert "username" not in names
        assert "username" not in names
        assert len(names) == 0

    def test_delete_variables_unknown(self, library):
        library.get_input_work_item()
        assert len(library.list_work_item_variables()) == 2

        library.delete_work_item_variables("unknown-variable")
        assert len(library.list_work_item_variables()) == 2

        with pytest.raises(KeyError):
            library.delete_work_item_variables("unknown-variable", force=False)
        assert len(library.list_work_item_variables()) == 2

    def test_raw_payload(self, library):
        _ = library.get_input_work_item()
        _ = library.get_input_work_item()
        item = library.get_input_work_item()

        payload = library.get_work_item_payload()
        assert payload == [1, 2, 3]

        library.set_work_item_payload({"output": 0xBEEF})
        library.save_work_item()
        MockAdapter.validate(item, "output", 0xBEEF)

    def test_list_files(self, library):
        library.get_input_work_item()

        files = library.list_work_item_files()
        assert files == ["file1.txt", "file2.txt", "file3.png"]

    def test_get_file(self, library):
        library.get_input_work_item()

        with temp_filename() as path:
            result = library.get_work_item_file("file2.txt", path)
            with open(result) as fd:
                data = fd.read()

            assert is_equal_files(result, path)
            assert data == "data2"

    def test_get_file_notexist(self, library):
        library.get_input_work_item()

        with pytest.raises(FileNotFoundError):
            library.get_work_item_file("file5.txt")

    def test_add_file(self, library):
        item = library.get_input_work_item()

        with temp_filename(b"some-input-content") as path:
            library.add_work_item_file(path, "file4.txt")

            files = library.list_work_item_files()
            assert files == ["file1.txt", "file2.txt", "file3.png", "file4.txt"]
            assert "file4.txt" not in MockAdapter.FILES[item.id]

            library.save_work_item()
            assert MockAdapter.FILES[item.id]["file4.txt"] == b"some-input-content"

    def test_add_file_duplicate(self, library):
        item = library.get_input_work_item()

        def verify_files():
            files = library.list_work_item_files()
            assert files == ["file1.txt", "file2.txt", "file3.png", "file4.txt"]

        with temp_filename(b"some-input-content") as path:
            library.add_work_item_file(path, "file4.txt")
            assert "file4.txt" not in MockAdapter.FILES[item.id]
            verify_files()

            # Add duplicate for unsaved item
            library.add_work_item_file(path, "file4.txt")
            assert "file4.txt" not in MockAdapter.FILES[item.id]
            verify_files()

            library.save_work_item()
            assert MockAdapter.FILES[item.id]["file4.txt"] == b"some-input-content"
            verify_files()

            # Add duplicate for saved item
            library.add_work_item_file(path, "file4.txt")
            verify_files()

            library.save_work_item()
            verify_files()

    def test_add_file_notexist(self, library):
        library.get_input_work_item()

        with pytest.raises(FileNotFoundError):
            library.add_work_item_file("file5.txt", "doesnt-matter")

    def test_remove_file(self, library):
        item = library.get_input_work_item()

        library.remove_work_item_file("file2.txt")

        files = library.list_work_item_files()
        assert files == ["file1.txt", "file3.png"]
        assert "file2.txt" in MockAdapter.FILES[item.id]

        library.save_work_item()
        assert "file2.txt" not in MockAdapter.FILES[item.id]

    def test_remove_file_notexist(self, library):
        library.get_input_work_item()

        library.remove_work_item_file("file5.txt")

        with pytest.raises(FileNotFoundError):
            library.remove_work_item_file("file5.txt", missing_ok=False)

    def test_get_file_pattern(self, library):
        library.get_input_work_item()

        with tempfile.TemporaryDirectory() as outdir:
            file1 = os.path.join(outdir, "file1.txt")
            file2 = os.path.join(outdir, "file2.txt")

            paths = library.get_work_item_files("*.txt", outdir)
            assert is_equal_files(paths[0], file1)
            assert is_equal_files(paths[1], file2)
            assert os.path.exists(file1)
            assert os.path.exists(file2)

    def test_remove_file_pattern(self, library):
        item = library.get_input_work_item()

        library.remove_work_item_files("*.txt")

        files = library.list_work_item_files()
        assert files == ["file3.png"]
        assert list(MockAdapter.FILES[item.id]) == [
            "file1.txt",
            "file2.txt",
            "file3.png",
        ]

        library.save_work_item()

        files = library.list_work_item_files()
        assert files == ["file3.png"]
        assert list(MockAdapter.FILES[item.id]) == ["file3.png"]

    def test_clear_work_item(self, library):
        library.get_input_work_item()

        library.clear_work_item()
        library.save_work_item()

        assert library.get_work_item_payload() == {}
        assert library.list_work_item_files() == []

    def test_get_file_unsaved(self, library):
        library.get_input_work_item()

        with temp_filename(b"some-input-content") as path:
            library.add_work_item_file(path, "file4.txt")

            files = library.list_work_item_files()
            assert files == ["file1.txt", "file2.txt", "file3.png", "file4.txt"]
            assert "file4.txt" not in MockAdapter.FILES

            with tempfile.TemporaryDirectory() as outdir:
                names = ["file1.txt", "file2.txt", "file4.txt"]
                result = library.get_work_item_files("*.txt", outdir)
                expected = [os.path.join(outdir, name) for name in names]
                for lhs, rhs in zip(result, expected):
                    assert is_equal_files(lhs, rhs)
                with open(result[-1]) as fd:
                    assert fd.read() == "some-input-content"

    def test_get_file_unsaved_no_copy(self, library):
        library.get_input_work_item()

        with tempfile.TemporaryDirectory() as outdir:
            path = os.path.join(outdir, "nomove.txt")
            with open(path, "w") as fd:
                fd.write("my content")

            mtime = os.path.getmtime(path)
            library.add_work_item_file(path)

            files = library.list_work_item_files()
            assert files == ["file1.txt", "file2.txt", "file3.png", "nomove.txt"]

            paths = library.get_work_item_files("*.txt", outdir)
            assert is_equal_files(paths[-1], path)
            assert os.path.getmtime(path) == mtime

    def test_get_file_unsaved_relative(self, library):
        library.get_input_work_item()

        with tempfile.TemporaryDirectory() as outdir:
            curdir = os.getcwd()
            try:
                os.chdir(outdir)
                with open("nomove.txt", "w") as fd:
                    fd.write("my content")

                mtime = os.path.getmtime("nomove.txt")
                library.add_work_item_file(os.path.join(outdir, "nomove.txt"))

                files = library.list_work_item_files()
                assert files == ["file1.txt", "file2.txt", "file3.png", "nomove.txt"]

                paths = library.get_work_item_files("*.txt")
                assert is_equal_files(paths[-1], os.path.join(outdir, "nomove.txt"))
                assert os.path.getmtime("nomove.txt") == mtime
            finally:
                os.chdir(curdir)

    def test_get_file_no_matches(self, library):
        library.get_input_work_item()

        with tempfile.TemporaryDirectory() as outdir:
            paths = library.get_work_item_files("*.pdf", outdir)
            assert len(paths) == 0

    def test_create_output_work_item(self, library):
        input_item = library.get_input_work_item()
        output_item = library.create_output_work_item()

        assert output_item.id is None
        assert output_item.parent_id == input_item.id

    def test_create_output_work_item_no_input(self, library):
        with pytest.raises(RuntimeError):
            library.create_output_work_item()

    @staticmethod
    @pytest.fixture(
        params=[
            lambda *files: files,  # files provided as tuple
            lambda *files: list(files),  # as list of paths
            lambda *files: ", ".join(files),  # comma separated paths
        ]
    )
    def out_files(request):
        """Output work item files."""
        with temp_filename(b"out-content-1", suffix="-1.txt") as path1, temp_filename(
            b"out-content-2", suffix="-2.txt"
        ) as path2:
            func = request.param
            yield func(path1, path2)

    def test_create_output_work_item_variables_files(self, library, out_files):
        library.get_input_work_item()
        variables = {"my_var1": "value1", "my_var2": "value2"}
        out_item = library.create_output_work_item(
            variables=variables, files=out_files, save=True
        )

        assert out_item.payload["my_var1"] == "value1"
        assert out_item.payload["my_var2"] == "value2"

        # This actually "downloads" (creates) the files, so make sure we remove them
        #  afterwards.
        paths = out_item.get_files("*.txt", dirname=OUTPUT_DIR)
        try:
            assert len(paths) == 2
            for path in paths:
                with open(path) as stream:
                    content = stream.read()
                idx = Path(path).stem.split("-")[-1]
                assert content == f"out-content-{idx}"
        finally:
            for path in paths:
                os.remove(path)

    def test_custom_root(self, adapter):
        library = WorkItems(default_adapter=adapter, root="vars")
        item = library.get_input_work_item()

        variables = library.get_work_item_variables()
        assert variables == {}

        library.set_work_item_variables(cool="beans", yeah="boi")
        assert item.payload == {
            **VARIABLES_FIRST,
            "vars": {"cool": "beans", "yeah": "boi"},
        }

    @pytest.mark.parametrize("limit", [0, 1, 2, 3, 4])  # no, existing and over limit
    def test_iter_work_items(self, library, limit):
        usernames = []

        def func(a, b, r=3):
            assert a + b == r
            # Collects the "username" variable from the payload if provided and returns
            #   True if found, False otherwise.
            payload = library.get_work_item_payload()
            if not isinstance(payload, dict):
                return False

            username = payload.get("username")
            if username:
                usernames.append(username)

            return username is not None

        library.get_input_work_item()
        results = library.for_each_input_work_item(func, 1, 2, items_limit=limit, r=3)

        expected_usernames = ["testguy", "another"]
        expected_results = [True, True, False]
        if limit:
            expected_usernames = expected_usernames[:limit]
            expected_results = expected_results[:limit]
        assert usernames == expected_usernames
        assert results == expected_results

    def test_iter_work_items_limit_and_state(self, library):
        def func():
            return 1

        # Pick one single item and make sure its state is set implicitly.
        results = library.for_each_input_work_item(func, items_limit=1)
        assert len(results) == 1
        assert library.current.state is State.DONE

        def func2():
            library.release_input_work_item(State.FAILED)
            return 2

        # Pick-up the rest of the two inputs and set state explicitly.
        results = library.for_each_input_work_item(func2)
        assert len(results) == 2
        assert library.current.state is State.FAILED

    @pytest.mark.parametrize("return_results", [True, False])
    def test_iter_work_items_return_results(self, library, return_results):
        def func():
            return 1

        library.get_input_work_item()
        results = library.for_each_input_work_item(func, return_results=return_results)
        if return_results:
            assert results == [1] * 3
        else:
            assert results is None

    @pytest.mark.parametrize("processed_items", [0, 1, 2, 3])
    def test_successive_work_items_iteration(self, library, processed_items):
        for _ in range(processed_items):
            library.get_input_work_item()
            library.release_input_work_item(State.DONE)

        def func():
            pass

        # Checks if all remaining input work items are processed once.
        results = library.for_each_input_work_item(func)
        assert len(results) == 3 - processed_items

        # Checks if there's no double processing of the last already processed item.
        results = library.for_each_input_work_item(func)
        assert len(results) == 0

    @pytest.mark.parametrize("processed_items", [0, 1, 2, 3])
    def test_inputs_iteration(self, inputs, processed_items):
        for _ in range(processed_items):
            item = inputs.reserve()
            item.done()

        # Checks if all remaining input work items are processed once.
        count = 0
        for _ in inputs.iterate():
            count += 1
        assert count == 3 - processed_items

        # Checks if there's no double processing of the last already processed item.
        for _ in inputs.iterate():
            assert False, "We should not get here"

    @staticmethod
    @pytest.fixture(
        params=[
            None,
            {"exception_type": "BUSINESS"},
            {
                "exception_type": "APPLICATION",
                "code": "UNEXPECTED_ERROR",
                "message": "This is an unexpected error",
            },
            {
                "exception_type": "APPLICATION",
                "code": None,
                "message": "This is an unexpected error",
            },
            {
                "exception_type": "APPLICATION",
                "code": None,
                "message": None,
            },
            {
                "exception_type": None,
                "code": None,
                "message": None,
            },
            {
                "exception_type": None,
                "code": "APPLICATION",
                "message": None,
            },
            {
                "exception_type": None,
                "code": "",
                "message": "Not empty",
            },
            {
                "exception_type": "application",
                "code": None,
                "message": " ",  # gets discarded during API request
            },
        ]
    )
    def release_exception(request):
        exception = request.param or {}
        effect = nullcontext()
        success = True
        if not exception.get("exception_type") and any(
            map(lambda key: exception.get(key), ["code", "message"])
        ):
            effect = pytest.raises(RuntimeError)
            success = False
        return exception or None, effect, success

    def test_release_work_item_failed(self, library, release_exception):
        exception, effect, success = release_exception

        library.get_input_work_item()
        with effect:
            library.release_input_work_item(
                "FAILED", **(exception or {})
            )  # intentionally providing a string for the state
        if success:
            assert library.current.state == State.FAILED

        exception_type = (exception or {}).pop("exception_type", None)
        if exception_type:
            exception["type"] = Error(exception_type.upper()).value
            exception.setdefault("code", None)
            exception.setdefault("message", None)
        else:
            exception = None
        if success:
            assert library.adapter.releases == [
                ("workitem-id-first", State.FAILED, exception)
            ]

    @pytest.mark.parametrize("exception", [None, {"exception_type": ExceptionType.APPLICATION}])
    def test_release_work_item_done(self, library, exception):
        library.get_input_work_item()
        library.release_input_work_item(State.DONE, **(exception or {}))
        assert library.current.state is State.DONE
        assert library.adapter.releases == [
            # No exception sent for non failures.
            ("workitem-id-first", State.DONE, None)
        ]

    def test_auto_release_work_item(self, library):
        library.get_input_work_item()
        library.get_input_work_item()  # this automatically sets the state of the last

        assert library.current.state is None  # because the previous one has a state
        assert library.adapter.releases == [("workitem-id-first", State.DONE, None)]

    def test_parse_work_item_from_raw_email(self, library, raw_email_data):
        raw_email, expected_body = raw_email_data
        library.adapter.DATA["workitem-id-first"]["rawEmail"] = raw_email

        library.get_input_work_item()
        parsed_email = library.get_work_item_variable("parsedEmail")
        assert parsed_email["Body"] == expected_body

    def test_parse_work_item_from_parsed_email(self, library, parsed_email_data):
        email_var, parsed_email, expected_body = parsed_email_data
        if parsed_email:
            library.adapter.FILES["workitem-id-first"][email_var] = parsed_email
        else:
            payload = library.adapter.DATA["workitem-id-first"]
            payload["email"] = {}
            set_dot_value(payload, email_var, value=expected_body)

        library.get_input_work_item()
        parsed_email = library.get_work_item_variable("parsedEmail")
        email_parsed = library.get_work_item_variable("email")
        assert parsed_email["Body"] == email_parsed["body"]
        assert expected_body in parsed_email["Body"]
        assert expected_body in email_parsed["body"]

    def test_parse_work_item_from_email_missing_content(self, library):
        library.get_input_work_item()
        for payload_var in ("rawEmail", "parsedEmail", "email"):
            with pytest.raises(KeyError):
                library.get_work_item_variable(payload_var)

    @pytest.mark.parametrize(
        "source_var, value",
        [
            ("email", "no e-mail here"),
            ("email", {}),
            ("email", {"field": "something"}),
        ],
    )
    def test_email_var_no_parse(self, library, source_var, value):
        library.adapter.DATA["workitem-id-first"][source_var] = value

        library.get_input_work_item()  # auto-parsing should pass without errors
        assert library.get_work_item_variable(source_var) == value  # left untouched
