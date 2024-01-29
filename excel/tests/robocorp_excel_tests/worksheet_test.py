import pytest

from robocorp.excel.excel import create_workbook


@pytest.fixture
def workbook():
    return create_workbook("xlsx")


def test_out_of_index_worksheet(workbook):
    # TODO: should there be a default 0th sheet, if you create an empty one
    with pytest.raises(IndexError):
        workbook.worksheet(1)
