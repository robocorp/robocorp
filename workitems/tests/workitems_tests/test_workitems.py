import os
import tempfile
from collections import OrderedDict
from contextlib import contextmanager
from pathlib import Path

import pytest

from robocorp.workitems import version_info
from robocorp.workitems._exceptions import BusinessException
from robocorp.workitems._types import ExceptionType, State
from robocorp.workitems._workitem import Input, Output

from .mocks import PAYLOAD_FIRST, PAYLOAD_SECOND


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


def is_same_path(lhs, rhs):
    lhs = Path(lhs).resolve()
    rhs = Path(rhs).resolve()
    return lhs == rhs


def test_inputs_first(inputs):
    assert inputs.current is not None
    assert isinstance(inputs.current, Input)


def test_inputs_reserve(inputs):
    first = inputs.current
    assert first.payload == PAYLOAD_FIRST
    assert first == inputs.current
    assert not first.released

    first.done()
    assert first.released

    with inputs.reserve() as second:
        assert second.payload == PAYLOAD_SECOND
        assert second == inputs.current
        assert not second.released
    assert second.released


def test_inputs_iter(inputs):
    items = []
    for item in inputs:
        assert isinstance(item, Input)
        items.append(item)

    assert len(items) == 2
    assert all(item.released for item in items)


def test_inputs_released(inputs):
    # Exhaust all items
    _ = list(inputs)

    assert len(inputs.released) == 2


def test_outputs_create(outputs, adapter):
    item = outputs.create(payload={"key": "value"})
    assert item.payload == {"key": "value"}
    adapter.validate(item, "key", "value")


def test_outputs_create_no_save(outputs, adapter):
    item = outputs.create(payload={"key": "value"}, save=False)
    assert item.payload == {"key": "value"}
    with pytest.raises(AssertionError):
        adapter.validate(item, "key", "value")


def test_outputs_create_no_current(outputs, context):
    context._inputs = []
    assert context.current_input is None

    with pytest.raises(RuntimeError):
        outputs.create()


def test_outputs_last(outputs):
    assert outputs.last is None
    item = outputs.create(payload={"key": "value"})
    assert outputs.last is item


def test_outputs_magic_methods(outputs):
    i = outputs.create(payload={"idx": 0})
    j = outputs.create(payload={"idx": 1})
    k = outputs.create(payload={"idx": 2})

    assert len(outputs) == 3
    assert outputs[1] == j
    assert list(outputs) == [i, j, k]
    assert list(reversed(outputs)) == [k, j, i]


def test_input_pass(inputs, adapter):
    item = inputs.current
    assert item.state is None
    assert item.exception is None
    assert len(adapter.releases) == 0

    item.done()
    assert item.state is State.DONE
    assert item.exception is None

    _, state, exc = adapter.releases[-1]
    assert state is State.DONE
    assert exc is None


def test_input_fail(inputs, adapter):
    item = inputs.current
    assert item.state is None
    assert item.exception is None
    assert len(adapter.releases) == 0

    exception = OrderedDict(
        type=ExceptionType.BUSINESS, code="MY_ERR_CODE", message="Something went oopsy"
    )

    item.fail(*exception.values())
    assert item.state is State.FAILED
    assert item.exception == exception

    _, state, exc = adapter.releases[-1]
    assert state is State.FAILED
    assert exc == exception


def test_input_create_output(inputs):
    item = inputs.current

    output = item.create_output()
    assert isinstance(output, Output)
    assert not output.saved
    assert item.outputs == [output]


def test_input_list_files(inputs):
    assert inputs.current.files == ["file1.txt", "file2.txt", "file3.png"]


def test_input_get_file(inputs):
    item = inputs.current

    with temp_filename() as path:
        result = item.get_file("file2.txt", path)
        assert is_same_path(result, path)
        assert result.read_text() == "data2"


def test_input_download_file_deprecated(inputs):
    assert version_info[0] < 2, "Should be removed"
    item = inputs.current

    with temp_filename() as path:
        result = item.download_file("file2.txt", path)
        assert is_same_path(result, path)
        assert result.read_text() == "data2"


def test_input_get_files(inputs):
    item = inputs.current

    with tempfile.TemporaryDirectory() as outdir:
        file1 = os.path.join(outdir, "file1.txt")
        file2 = os.path.join(outdir, "file2.txt")

        paths = item.get_files("*.txt", outdir)
        assert is_same_path(paths[0], file1)
        assert is_same_path(paths[1], file2)
        assert os.path.exists(file1)
        assert os.path.exists(file2)


def test_input_download_files_deprecated(inputs):
    assert version_info[0] < 2, "Should be removed"
    item = inputs.current

    with tempfile.TemporaryDirectory() as outdir:
        file1 = os.path.join(outdir, "file1.txt")
        file2 = os.path.join(outdir, "file2.txt")

        paths = item.download_files("*.txt", outdir)
        assert is_same_path(paths[0], file1)
        assert is_same_path(paths[1], file2)
        assert os.path.exists(file1)
        assert os.path.exists(file2)


def test_input_get_file_missing(inputs):
    item = inputs.current

    with pytest.raises(FileNotFoundError):
        item.get_file("file5.txt")


def test_input_get_files_missing(inputs):
    item = inputs.current

    with tempfile.TemporaryDirectory() as outdir:
        paths = item.get_files("*.pdf", outdir)
        assert len(paths) == 0


def test_input_remove_file(inputs):
    item = inputs.current
    assert "file1.txt" in item.files

    item.remove_file("file1.txt")
    assert "file1.txt" in item.files

    item.save()
    assert "file1.txt" not in item.files


def test_input_remove_file_notexist(inputs):
    item = inputs.current
    with pytest.raises(FileNotFoundError):
        item.remove_file("not-exist")


def test_input_remove_files(inputs):
    item = inputs.current

    paths = item.remove_files("*.txt")
    assert paths == ["file1.txt", "file2.txt"]
    assert not item.saved

    item.save()
    assert item.files == ["file3.png"]
    assert item.saved


def test_input_modify_payload(inputs, adapter):
    item = inputs.current
    assert item.saved

    item.payload = {"modified": 123}
    assert not item.saved

    item.save()
    assert item.saved
    adapter.validate(item, "modified", 123)


def test_outputs_create_files(outputs, adapter):
    with (
        temp_filename(b"file-content-1", suffix="-1.txt") as path1,
        temp_filename(b"file-content-2", suffix="-2.txt") as path2,
    ):
        path1, path2 = Path(path1), Path(path2)
        item = outputs.create(files=[path1, path2])
        assert adapter.files[item.id][path1.name] == b"file-content-1"
        assert adapter.files[item.id][path2.name] == b"file-content-2"


@pytest.mark.parametrize(
    "fail_kwargs",
    [
        {},
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
            "code": "APPLICATION",
            "message": None,
        },
        {
            "code": "",
            "message": "Not empty",
        },
        {
            "exception_type": "application",
            "code": None,
            "message": " ",  # Discarded during API request
        },
    ],
)
def test_release_work_item_failed(inputs, adapter, fail_kwargs):
    item = inputs.current
    item.fail(**fail_kwargs)

    if type_ := fail_kwargs.get("exception_type"):
        exception_type = ExceptionType(type_.upper())
    else:
        exception_type = ExceptionType.APPLICATION

    exception = {
        "type": exception_type,
        "code": fail_kwargs.get("code"),
        "message": fail_kwargs.get("message"),
    }

    assert item.state == State.FAILED
    assert item.exception == exception
    assert adapter.releases == [("workitem-id-first", State.FAILED, exception)]


def test_duplicate_reserve(inputs):
    with pytest.raises(RuntimeError):
        inputs.reserve()

    inputs.current.done()
    inputs.reserve()

    with pytest.raises(RuntimeError):
        inputs.reserve()


def test_inputs_iter_explicit_release(inputs):
    # Should not raise / double release
    for item in inputs:
        item.done()


def test_inputs_context_raise(inputs, adapter):
    inputs.current.done()

    with inputs.reserve():
        raise BusinessException(message="My message", code="SOME_CODE")

    _, state, exception = adapter.releases[-1]
    assert state is State.FAILED
    assert exception["type"] == "BUSINESS"
    assert exception["code"] == "SOME_CODE"
    assert exception["message"] == "My message"


def test_inputs_raise_derived_class(inputs, adapter):
    class CustomException(BusinessException):
        def __init__(self):
            super().__init__(message="My Custom Exception!")

    with inputs.current:
        raise CustomException()

    _, state, exception = adapter.releases[-1]
    assert state is State.FAILED
    assert exception["type"] == "BUSINESS"
    assert exception["code"] is None
    assert exception["message"] == "My Custom Exception!"


def test_inputs_loop_raise(inputs, adapter):
    for inp in inputs:
        with inp:
            raise BusinessException(message="My message", code="SOME_CODE")

    assert len(adapter.releases) == 2
    for _, state, exception in adapter.releases:
        assert state is State.FAILED
        assert exception["type"] == "BUSINESS"
        assert exception["code"] == "SOME_CODE"
        assert exception["message"] == "My message"


def test_inputs_throw_unknown_exception(inputs, adapter):
    inputs.current.done()

    with pytest.raises(ValueError):
        with inputs.reserve():
            raise ValueError("Some value")

    _, state, exception = adapter.releases[-1]
    assert state is State.FAILED
    assert exception["type"] == "APPLICATION"
    assert exception["code"] is None
    assert exception["message"] == "Some value"


def test_iter_after_release(inputs):
    first = inputs.current
    first.done()

    rest = list(inputs)
    assert len(rest) == 1
    assert len(inputs.released) == 2
    assert rest[0] != first


def test_allow_multiple_saves(outputs, adapter):
    item = outputs.create(save=False)
    assert item.saved is False

    item.payload = {"key": "value"}
    assert item.saved is False

    item.save()
    assert item.saved is True
    adapter.validate(item, "key", "value")

    item.payload = {"key": "value2"}
    assert item.saved is False

    item.save()
    assert item.saved is True
    adapter.validate(item, "key", "value2")


def test_collect_inputs(inputs, outputs, adapter):
    output = outputs.create()
    assert adapter.releases == []

    summary = []
    for item in inputs:
        summary.append(item.payload)

    assert len(summary) == 3
    assert len(adapter.releases) == 3

    output.payload = summary
    output.save()
    assert adapter.data[output.id] == summary


def test_add_files_input(inputs, adapter):
    item = inputs.current
    with temp_filename(b"some-bytes") as path:
        item.add_file(path, name="name-of-file")
        item.save()
        assert adapter.files[item.id]["name-of-file"] == b"some-bytes"


def test_remove_files_input(inputs, adapter):
    item = inputs.current
    item.remove_files("file1.txt")
    item.save()
    assert sorted(item.files) == ["file2.txt", "file3.png"]
