import pytest

from robocorp.excel.excel import create_workbook

# create workbook tests


def test_default_sheet_xlsx():
    workbook = create_workbook("xlsx")
    worksheet = workbook.worksheet(0)
    assert worksheet.name == "Sheet"


def test_default_sheet_xls():
    workbook = create_workbook("xls")
    worksheet = workbook.worksheet(0)
    assert worksheet.name == "Sheet"
    worksheet_by_name = workbook.worksheet("Sheet")
    assert worksheet.name == worksheet_by_name.name
    # TODO: these should perhaps be also same
    # assert worksheet == worksheet_by_name


def test_workbook_with_renamed_sheet():
    workbook = create_workbook("xlsx", "first")
    worksheet = workbook.worksheet("first")
    assert worksheet.name == "first"


def test_1_sheet_workbook():
    workbook = create_workbook("xlsx")
    workbook.create_worksheet("first sheet")
    # TODO: should there be a default 0th sheet, if you create an empty one
    sheet = workbook.worksheet(0)
    assert sheet


def test_create_worksheet():
    workbook = create_workbook("xlsx", "first sheet")
    sheet1 = workbook.worksheet("first sheet")
    sheet2 = workbook.create_worksheet("second sheet")
    assert sheet1.name == workbook.list_worksheets()[0]
    assert sheet2.name == workbook.list_worksheets()[1]


def test_worksheet_exists():
    workbook = create_workbook("xlsx", "first sheet")
    assert workbook.worksheet_exists(0)
    assert workbook.worksheet_exists("first sheet")
    workbook.create_worksheet("second sheet")
    assert workbook.worksheet_exists(1)
    assert workbook.worksheet_exists("second sheet")


def test_remove_last_worksheet():
    with pytest.raises(ValueError):
        workbook = create_workbook("xlsx", "first sheet")
        workbook.remove_worksheet(0)


def test_remove_worksheet_by_index():
    workbook = create_workbook("xlsx", "first sheet")
    workbook.create_worksheet("second sheet")
    assert len(workbook.list_worksheets()) == 2
    workbook.remove_worksheet(0)
    assert len(workbook.list_worksheets()) == 1
    assert workbook.list_worksheets()[0] == "second sheet"


def test_remove_worksheet_by_name():
    workbook = create_workbook("xlsx", "first sheet")
    workbook.create_worksheet("second sheet")
    assert len(workbook.list_worksheets()) == 2
    workbook.remove_worksheet("first sheet")
    assert len(workbook.list_worksheets()) == 1
    assert workbook.list_worksheets()[0] == "second sheet"
