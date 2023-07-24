import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

import pytest

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

    assert len(items) == 3
    assert all(item.released for item in items)


def test_inputs_released(inputs):
    # Exhaust all items
    _ = list(inputs)

    assert len(inputs.released) == 3


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


def test_input_pass(inputs):
    item = inputs.current
    assert item.state is None
    assert len(item._adapter.releases) == 0

    item.done()
    assert item.state is State.DONE

    _, state, exc = item._adapter.releases[-1]
    assert state is State.DONE
    assert exc is None


def test_input_fail(inputs):
    item = inputs.current
    assert item.state is None
    assert len(item._adapter.releases) == 0

    item.fail(ExceptionType.BUSINESS, "MY_ERR_CODE", "Something went oopsy")
    assert item.state is State.FAILED

    _, state, exc = item._adapter.releases[-1]
    assert state is State.FAILED
    assert exc["type"] == "BUSINESS"
    assert exc["code"] == "MY_ERR_CODE"
    assert exc["message"] == "Something went oopsy"


def test_input_create_output(inputs):
    item = inputs.current

    output = item.create_output()
    assert isinstance(output, Output)
    assert not output.saved
    assert item.outputs == [output]


def test_input_list_files(inputs):
    assert inputs.current.files == ["file1.txt", "file2.txt", "file3.png"]


def test_input_download_file(inputs):
    item = inputs.current

    with temp_filename() as path:
        result = item.download_file("file2.txt", path)
        assert is_same_path(result, path)
        assert result.read_text() == "data2"


def test_input_download_file_missing(inputs):
    item = inputs.current

    with pytest.raises(KeyError):
        item.download_file("file5.txt")


def test_input_download_files(inputs):
    item = inputs.current

    with tempfile.TemporaryDirectory() as outdir:
        file1 = os.path.join(outdir, "file1.txt")
        file2 = os.path.join(outdir, "file2.txt")

        paths = item.download_files("*.txt", outdir)
        assert is_same_path(paths[0], file1)
        assert is_same_path(paths[1], file2)
        assert os.path.exists(file1)
        assert os.path.exists(file2)


def test_input_download_files_missing(inputs):
    item = inputs.current

    with tempfile.TemporaryDirectory() as outdir:
        paths = item.download_files("*.pdf", outdir)
        assert len(paths) == 0


def test_outputs_create_files(outputs, adapter):
    with (
        temp_filename(b"file-content-1", suffix="-1.txt") as path1,
        temp_filename(b"file-content-2", suffix="-2.txt") as path2,
    ):
        path1, path2 = Path(path1), Path(path2)
        item = outputs.create(files=[path1, path2])
        assert adapter.FILES[item.id][path1.name] == b"file-content-1"
        assert adapter.FILES[item.id][path2.name] == b"file-content-2"


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
def test_release_work_item_failed(inputs, fail_kwargs):
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
    assert item._adapter.releases == [("workitem-id-first", State.FAILED, exception)]


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


def test_inputs_throw_business_exception(inputs):
    inputs.current.done()

    with inputs.reserve():
        raise BusinessException(message="My message", code="SOME_CODE")

    _, state, exception = inputs.current._adapter.releases[-1]
    assert state is State.FAILED
    assert exception["type"] == "BUSINESS"
    assert exception["code"] == "SOME_CODE"
    assert exception["message"] == "My message"


def test_inputs_throw_unknown_exception(inputs):
    inputs.current.done()

    with pytest.raises(ValueError):
        with inputs.reserve():
            raise ValueError("Some value")

    _, state, exception = inputs.current._adapter.releases[-1]
    assert state is State.FAILED
    assert exception["type"] == "APPLICATION"
    assert exception["code"] is None
    assert exception["message"] == "Some value"


def test_iter_after_release(inputs):
    first = inputs.current
    first.done()

    rest = list(inputs)
    assert len(rest) == 2
    assert len(inputs.released) == 3
    assert rest[0] != first


def test_collect_inputs(inputs, outputs):
    adapter = inputs.current._adapter

    output = outputs.create(save=False)
    assert output.id is None
    assert adapter.releases == []

    summary = []
    for item in inputs:
        summary.append(item.payload)
    assert len(summary) == 3

    output.payload = summary
    output.save()
    assert adapter.DATA[output.id] == summary
