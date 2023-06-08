import pathlib
from io import BytesIO
from typing import Any, List, Optional, Union

from robocorp.excel._types import PathType
from robocorp.excel._workbooks import XlsWorkbook, XlsxWorkbook
from robocorp.excel.worksheet import Worksheet


class Workbook:
    """Manager class for both .xls and .xlsx Excel files."""

    def __init__(self, excel: Union[XlsWorkbook, XlsxWorkbook]):
        # Internal API, for users there is create_ and open_ workbook functions
        self.excel = excel

    def save(self, name: Union[PathType, BytesIO], overwrite=True):
        # files.save_workbook()
        if not isinstance(name, BytesIO):
            if not overwrite and pathlib.Path(name).exists():
                raise FileExistsError
        self.excel.validate_content()
        self.excel.save(name)

    def close(self):
        # Could also be a context manager and auto close
        # files.close_workbook()
        pass

    def worksheet(self, sheet: Union[str, int]) -> Worksheet:
        """If name is not provided take the first worksheet?"""
        if isinstance(sheet, int):
            name = self.list_worksheets()[sheet]
        else:
            sheets = self.list_worksheets()
            name = sheets[sheets.index(sheet)]

        return Worksheet(self, name)

    def create_worksheet(
        self,
        name: str,
        content: Optional[Any] = None,
        exist_ok: Optional[bool] = False,
        header: Optional[bool] = False,
    ):
        # files.create_worksheet()
        # TODO: original code: https://github.com/robocorp/rpaframework/blob/dec0053a3aa34da20232f63e1b26e21df98e59e8/packages/main/src/RPA/Excel/Files.py#L539
        # TODO: implement content and header
        if name in self.list_worksheets():
            if not exist_ok:
                raise ValueError(f"Duplicate worksheet name '{name}'")
            return Worksheet(self, name)

        self.excel.create_worksheet(name)
        if content:
            self.excel.append_worksheet(name, content, header)
        return Worksheet(self, name)

    # files.list_worksheets()
    def list_worksheets(self) -> List[str]:
        return self.excel.sheetnames

    def worksheet_exists(self, sheet: Union[str, int]) -> bool:
        # files.worksheet_exists()
        if isinstance(sheet, int):
            return len(self.list_worksheets()) > sheet
        else:
            return sheet in self.list_worksheets()

    def remove_worksheet(self, sheet: Union[str, int]):
        # files.remove_worksheet()
        if isinstance(sheet, int):
            name = self.list_worksheets()[sheet]
        else:
            name = sheet

        self.excel.remove_worksheet(name)
