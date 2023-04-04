import logging
import pathlib
from typing import Any, List, Optional, Union
from typing_extensions import Literal

from robo.libs.excel._types import PathType
from robo.libs.excel._worksheet import Worksheet
from robo.libs.excel._workbooks import XlsWorkbook, XlsxWorkbook


class Workbook:
    def __init__(self, excel: Union[XlsWorkbook, XlsxWorkbook]):
        # Internal API, for users there is create_ and open_ workbook functions
        self.excel = excel

    def save(self, name: PathType):
        # files.save_workbook()
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
        if exist_ok:
            if name in self.list_worksheets():
                return Worksheet(self, name)

        self.excel.create_worksheet(name)
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


# these may be removed, replaced by handling worksheets yourself? or these will go to workbook!


# removed:
# files.get_active_worksheet()
# files.set_active_worksheet()
