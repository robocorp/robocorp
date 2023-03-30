import pathlib
from typing import Literal, Optional, Union

from robo.libs._types import PathType

from robo.libs.excel._workbooks import XlsWorkbook, XlsxWorkbook, _load_workbook
from robo.libs.excel.workbook import Workbook


def create_workbook(
    fmt: Literal["xlsx", "xls"] = "xlsx",
    sheet_name: Optional[str] = None,
) -> Workbook:
    # FIXME: add missing types from this docs page https://support.microsoft.com/en-us/office/file-formats-that-are-supported-in-excel-0943ff2c-6014-4e8d-aaea-b83d51d46247
    # check which of these our python lib behind scenes supports: xlsx, xls, xlsm, xltm, xltx, xlt, xlam, xlsb, xla, xlr, xlw, xll
    # removed path, as it is only used when saved
    # files.create_workbook()
    if fmt == "xlsx":
        workbook = XlsxWorkbook()
    elif fmt == "xls":
        workbook = XlsWorkbook()
    else:
        raise ValueError(f"Unknown format: {fmt}")

    workbook.create()
    if sheet_name is not None:
        workbook.rename_worksheet(sheet_name, workbook.active)

    return Workbook(workbook)


def open_workbook(
    path: PathType,
    data_only: bool = False,
    read_only: bool = False,
) -> Workbook:
    """Opens an existing workbook"""
    # files.open_workbook()
    return Workbook(_load_workbook(path, data_only, read_only))
