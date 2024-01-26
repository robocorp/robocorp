import contextlib
import datetime
from io import BytesIO
from pathlib import Path

import pytest

from robocorp.excel import Table, create_workbook, open_workbook
from robocorp.excel._workbooks import _ensure_unique
from robocorp.excel.workbook import XlsWorkbook, XlsxWorkbook

from . import RESOURCES_DIR, RESULTS_DIR

EXCELS_DIR = RESOURCES_DIR / "excels"


@contextlib.contextmanager
def _workbook(excel_file):
    excel_path = EXCELS_DIR / excel_file
    workbook = open_workbook(excel_path)
    yield workbook
    workbook.close()


@pytest.fixture(params=["example.xlsx", "example.xls"])
def workbook(request):
    with _workbook(request.param) as wb:
        yield wb


@pytest.fixture(params=["one-row.xlsx", "one-row.xls", "empty.xlsx", "empty.xls"])
def library_empty(request):
    with _workbook(request.param) as wb:
        yield wb


@pytest.mark.parametrize(
    "fmt, instance", [("xlsx", XlsxWorkbook), ("xls", XlsWorkbook)]
)
def test_create_workbook(fmt, instance):
    workbook = create_workbook(fmt=fmt)
    assert isinstance(workbook.excel, instance)
    assert workbook.excel._book is not None
    assert workbook.excel.extension is None


@pytest.mark.parametrize("fmt", ["xlsx", "xls"])
def test_create_after_close(fmt):
    workbook = create_workbook(fmt=fmt)
    workbook.close()
    create_workbook(fmt=fmt)


@pytest.mark.parametrize("fmt", ["xlsx", "xls"])
def test_create_without_close(fmt):
    create_workbook(fmt=fmt)
    create_workbook(fmt=fmt)


@pytest.mark.parametrize("filename", ["not-a-file.xlsx", "not-a-file.xls"])
def test_open_missing(filename):
    with pytest.raises(FileNotFoundError):
        open_workbook(filename)


def test_wrong_extension_fallback_xlsx():
    # openpyxl does not support xls (actual format) but xlrd will succeed
    path = str(EXCELS_DIR / "wrong_extension.xlsx")
    workbook = open_workbook(path)
    assert workbook is not None


def test_wrong_extension_fallback_xls():
    # openpyxl will refuse to read wrong extension and xlrd does not support xlsx
    path = str(EXCELS_DIR / "wrong_extension.xls")
    workbook = None
    with pytest.raises(ValueError, match=".*wrong_extension.xls.*path.*extension.*"):
        workbook = open_workbook(path)
    assert workbook is None


def test_extension_property(workbook):
    assert workbook.excel.extension == Path(workbook.excel.path).suffix


def test_save_workbook(workbook):
    path = RESULTS_DIR / workbook.excel.path.name
    workbook.save(str(path), overwrite=True)
    # Exact size is unclear because some formatting, meta-data, etc.
    # might get stripped out
    with open(path, "r+b") as fd:
        content = fd.read()
    assert len(content) > 1024
    with pytest.raises(FileExistsError):
        workbook.save(str(path), overwrite=False)


def test_list_worksheets(workbook):
    sheets = workbook.list_worksheets()
    assert sheets == ["First", "Second"]


def test_get_active_worksheet(workbook):
    active = workbook.excel.active
    assert active == "Second"


def test_set_active_worksheet_by_name(workbook):
    workbook.excel.active = "First"
    assert workbook.excel.active == "First"
    workbook.excel.active = "Second"
    assert workbook.excel.active == "Second"


def test_set_active_worksheet_by_index(workbook):
    workbook.excel.active = 0
    assert workbook.excel.active == "First"
    workbook.excel.active = 1
    assert workbook.excel.active == "Second"


def test_set_active_worksheet_unknown(workbook):
    with pytest.raises(ValueError):
        workbook.excel.active = "Third"
    assert workbook.excel.active != "Third"
    with pytest.raises(IndexError):
        workbook.excel.active = 2
    assert workbook.excel.active != "Third"


def test_create_worksheet(workbook):
    workbook.create_worksheet("New")
    assert workbook.list_worksheets() == ["First", "Second", "New"]


def test_create_worksheet_duplicate(workbook):
    workbook.create_worksheet("New")
    assert workbook.list_worksheets() == ["First", "Second", "New"]

    with pytest.raises(ValueError):
        workbook.create_worksheet("New")
    assert workbook.list_worksheets() == ["First", "Second", "New"]


def test_create_worksheet_content(workbook):
    table = Table({"one": [1, 2, 3], "two": ["a", "b", "c"]})

    worksheet_new = workbook.create_worksheet("New", table)
    data = worksheet_new.as_table()
    assert len(data) == 3
    assert data.get_column("A", as_list=True) == [1, 2, 3]

    worksheet_new2 = workbook.create_worksheet("New2", table, header=True)
    data = worksheet_new2.as_table(header=True)
    assert len(data) == 3
    assert data.get_column("one", as_list=True) == [1, 2, 3]


def test_read_worksheet_default(workbook):
    data = workbook.excel.read_worksheet()
    assert len(data) == 10
    assert data[5]["A"] == 5
    assert data[5]["C"] == 2468


def test_read_worksheet_by_index(workbook):
    data = workbook.worksheet(0).as_list()
    assert len(data) == 10
    assert data[2]["B"] == "Mara"
    assert data[2]["F"] == 25


def test_read_worksheet_by_name(workbook):
    data = workbook.worksheet("First").as_list()
    assert len(data) == 10
    assert data[2]["B"] == "Mara"
    assert data[2]["F"] == 25


def test_read_worksheet_header(workbook):
    data = workbook.worksheet("Second").as_list(header=True)
    assert len(data) == 9
    assert data[5]["Index"] == 6
    assert data[5]["Id"] == 2554


@pytest.mark.parametrize(
    "header, content",
    [
        (False, [{"A": "Single"}]),
        (True, []),
    ],
)
def test_read_worksheet_header_empty(library_empty, header, content):
    data = library_empty.worksheet("Sheet").as_list(header=header)
    excel_name = library_empty.excel.path.stem
    if "empty" in excel_name:
        content = []  # there's no content at all, no matter the header switch
    assert data == content


def test_read_worksheet_timestamp(workbook):
    data = workbook.worksheet("Second").as_list(header=True)
    assert data[5]["Date"] == datetime.datetime(2015, 5, 21)


def test_read_worksheet_as_table(workbook):
    table = workbook.worksheet("First").as_table()
    assert isinstance(table, Table)
    assert len(table) == 10
    assert table[2, 1] == "Mara"
    assert table[2, 2] == "Hashimoto"


def test_read_worksheet_as_table_start_offset(workbook):
    table = workbook.worksheet("First").as_table(start=3)
    assert len(table) == 8
    assert table[0, 1] == "Mara"
    assert table[0, 2] == "Hashimoto"


def test_read_worksheet_as_table_start_offset_and_header(workbook):
    table = workbook.worksheet("First").as_table(start=2, header=True)
    assert len(table) == 8
    assert table.columns == ["1", "Dulce", "Abril", "Female", "United States", "32"]
    assert table[0, 2] == "Hashimoto"


def test_read_worksheet_empty(workbook):
    worksheet_empty = workbook.create_worksheet("Empty")

    data = worksheet_empty.as_list(header=False)
    assert data == []

    data_header = worksheet_empty.as_list(header=True)
    assert data_header == []

    table = worksheet_empty.as_table(header=False)
    assert table.dimensions == (0, 0)

    table_header = worksheet_empty.as_table(header=True)
    assert table_header.dimensions == (0, 0)


def test_append_to_worksheet_headers(workbook):
    table = Table(
        [
            {"Index": 98, "Date": "today", "Id": "some_value"},
            {"Index": 99, "Date": "tomorrow", "Id": "another_value"},
        ]
    )
    worksheet = workbook.worksheet("Second")
    worksheet.append_rows_to_worksheet(table, header=True)

    result = worksheet.as_table(header=True)
    assert len(result) == 11
    assert result[-1] == [99, "tomorrow", "another_value"]


@pytest.mark.parametrize("fmt", ("xlsx", "xls"))
def test_append_to_worksheet_empty(fmt):
    table = Table(
        [
            {"Index": 98, "Date": "today", "Id": "some_value"},
            {"Index": 99, "Date": "tomorrow", "Id": "another_value"},
        ]
    )
    workbook = create_workbook(fmt=fmt)
    worksheet = workbook.worksheet(0).append_rows_to_worksheet(table)

    result = worksheet.as_table()
    assert len(result) == 2
    assert result[0] == [98, "today", "some_value"]


@pytest.mark.parametrize("fmt", ("xlsx", "xls"))
def test_append_to_worksheet_empty_with_headers(fmt):
    table = Table(
        [
            {"Index": 98, "Date": "today", "Id": "some_value"},
            {"Index": 99, "Date": "tomorrow", "Id": "another_value"},
        ]
    )
    workbook = create_workbook(fmt=fmt)
    worksheet = workbook.worksheet(0).append_rows_to_worksheet(table, header=True)

    result = worksheet.as_table()
    assert len(result) == 3
    assert result[0] == ["Index", "Date", "Id"]


def test_remove_worksheet(workbook):
    workbook.remove_worksheet("Second")
    assert workbook.list_worksheets() == ["First"]

    with pytest.raises(ValueError):
        workbook.remove_worksheet("First")


def test_rename_worksheet(workbook):
    worksheet = workbook.worksheet("Second")
    worksheet.rename("Toinen")
    assert workbook.list_worksheets() == ["First", "Toinen"]


def test_ensure_unique():
    result = _ensure_unique(["Banana", "Apple", "Lemon", "Apple", "Apple", "Banana"])
    assert result == ["Banana", "Apple", "Lemon", "Apple_2", "Apple_3", "Banana_2"]


def test_ensure_unique_nested():
    result = _ensure_unique(["Banana", "Apple", "Lemon", "Apple", "Apple_2", "Banana"])
    assert result == ["Banana", "Apple", "Lemon", "Apple_2", "Apple_2_2", "Banana_2"]


def test_find_empty_row(workbook):
    row = workbook.worksheet("First").find_empty_row()
    assert row == 11


def test_get_worksheet_value(workbook):
    worksheet_second = workbook.worksheet("Second")
    assert worksheet_second.get_cell_value(5, "A") == 4
    assert worksheet_second.get_cell_value(5, "C") == 3549
    assert worksheet_second.get_cell_value(3, 3) == 1582
    worksheet_first = workbook.worksheet("First")
    assert worksheet_first.get_cell_value(9, "E") == "United States"


def test_set_worksheet_value(workbook):
    worksheet = workbook.worksheet("Second")

    worksheet.set_cell_value(11, "A", "First")
    worksheet.set_cell_value(11, 2, "Second")
    worksheet.set_cell_value(11, "3", "Third")

    data = worksheet.as_list()

    row = data[-1]
    assert row["A"] == "First"
    assert row["B"] == "Second"
    assert row["C"] == "Third"


def test_cell_format(workbook):
    fmts = [
        "general",
        "0",
        "0.00",
        "#,##0",
        "#,##0.00",
        '"$"#,##0_);("$"#,##',
        '"$"#,##0_);[Red]("$"#,##',
        '"$"#,##0.00_);("$"#,##',
        '"$"#,##0.00_);[Red]("$"#,##',
        "0%",
        "0.00%",
        "0.00E+00",
        "# ?/?",
        "# ??/??",
        "M/D/YY",
        "D-MMM-YY",
        "D-MMM",
        "MMM-YY",
        "h:mm AM/PM",
        "h:mm:ss AM/PM",
        "h:mm",
        "h:mm:ss",
        "M/D/YY h:mm",
        "_(#,##0_);(#,##0)",
        "_(#,##0_);[Red](#,##0)",
        "_(#,##0.00_);(#,##0.00)",
        "_(#,##0.00_);[Red](#,##0.00)",
        '_("$"* #,##0_);_("$"* (#,##0);_("$"* "-"_);_(@_)',
        '_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)',
        '_("$"* #,##0.00_);_("$"* (#,##0.00);_("$"* "-"??_);_(@_)',
        '_(* #,##0.00_);_(* (#,##0.00);_(* "-"??_);_(@_)',
        "mm:ss",
        "[h]:mm:ss",
        "mm:ss.0",
        "##0.0E+0",
        "@",
        "BOOLEAN",
    ]

    value = -1278.9078
    worksheet = workbook.create_worksheet("Formats")

    for idx, fmt in enumerate(fmts, 1):
        worksheet.set_cell_value(idx, "A", fmt)
        worksheet.set_cell_value(idx, "B", value)
        worksheet.set_cell_format(idx, "B", fmt)


def test_insert_image_to_worksheet(workbook):
    path = str(RESOURCES_DIR / "faces.jpeg")
    worksheet = workbook.worksheet("Second")
    worksheet.insert_image(10, "B", path, scale=4)
    workbook.save(BytesIO())


@pytest.mark.parametrize("fmt", ("xlsx", "xls"))
def test_create_workbook_default_sheet(fmt):
    workbook = create_workbook(fmt=fmt)
    assert workbook.list_worksheets() == ["Sheet"]

    workbook.create_worksheet("Test")
    assert workbook.list_worksheets() == ["Sheet", "Test"]


@pytest.mark.parametrize(
    "excel_file, data_only",
    [
        ("formulas.xlsx", False),
        ("formulas.xls", False),
        ("formulas.xlsx", True),
    ],
)
def test_read_worksheet_with_formulas(excel_file, data_only):
    excel_path = EXCELS_DIR / excel_file
    workbook = open_workbook(excel_path, data_only=data_only)
    worksheet = workbook.worksheet("Sheet1")
    assert worksheet.get_cell_value(2, "A") == 1
    assert worksheet.get_cell_value(2, "B") == 3
    if workbook.excel.path.suffix == ".xlsx":
        assert worksheet.get_cell_value(2, "C") == 4 if data_only else "=A2+B2"
    else:
        assert worksheet.get_cell_value(2, "C") == 4
    workbook.close()


@pytest.mark.parametrize(
    "excel_file, data_only",
    [
        ("formulas.xls", True),
    ],
)
def test_read_xls_worksheet_with_formulas_data_only(excel_file, data_only):
    excel_path = EXCELS_DIR / excel_file
    with pytest.raises(ValueError):
        open_workbook(excel_path, data_only=data_only)


@pytest.mark.parametrize("name", ["spaces.xls", "spaces.xlsx"])
def test_invalid_whitespace_fix(name):
    if name.endswith("xlsx"):

        def get_user(book):
            return book.properties.lastModifiedBy

        expected_user = "cmin  "
    else:

        def get_user(book):
            return book.user_name

        expected_user = "cmin"

    workbook = open_workbook(EXCELS_DIR / name)
    assert get_user(workbook.excel.book) == expected_user

    workbook.save(RESULTS_DIR / name, overwrite=True)
    # Leading/trailing whitespace is stripped on save, thus not creating any unwanted
    #  `xml:space="preserve"` tag child under workbook properties. (which breaks
    #  validation with Microsoft)
    assert get_user(workbook.excel.book) == "cmin"


@pytest.mark.parametrize("fmt", ["xlsx", "xls"])
def test_create_with_sheet_name(fmt):
    name = "CustomName"
    workbook = create_workbook(fmt, name)
    assert name in workbook.list_worksheets()
