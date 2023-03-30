import pathlib
from typing import Optional, Union

from robo.libs._types import PathType

from robo.libs.excel._workbooks import XlsWorkbook, XlsxWorkbook, load_workbook


def create_workbook(
    path: Optional[PathType] = None,
    fmt: Optional[str] = "xlsx",
    sheet_name: Optional[str] = None,
) -> Union["XlsWorkbook", "XlsxWorkbook"]:
    fmt = (
        str(fmt).lower().strip()
        if fmt
        else pathlib.Path(path).suffix.lower().lstrip(".")
    )
    if fmt == "xlsx":
        workbook = XlsxWorkbook(path)
    elif fmt == "xls":
        workbook = XlsWorkbook(path)
    else:
        raise ValueError(f"Unknown format: {fmt}")

    workbook.create()
    if sheet_name is not None:
        workbook.rename_worksheet(sheet_name, workbook.active)

    return workbook


def open_workbook(
    path: PathType,
    data_only: Optional[bool] = False,
    read_only: Optional[bool] = False,
) -> Union["XlsWorkbook", "XlsxWorkbook"]:
    return load_workbook(path, data_only, read_only)
