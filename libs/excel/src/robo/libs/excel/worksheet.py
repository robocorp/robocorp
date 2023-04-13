from typing import TYPE_CHECKING, Any, List, Optional, Union
from typing_extensions import deprecated

from robo.libs.excel.tables import Table, Tables

if TYPE_CHECKING:
    from robo.libs.excel.workbook import Workbook


class Worksheet:
    """Common class for worksheets to manage the worksheet's content."""

    def __init__(self, workbook: "Workbook", name: str):
        self._workbook = workbook
        # TODO: name should be a property, with setter that also changes it in the excel
        self.name: str = name
        assert self.name

    def append_rows_to_worksheet(
        self,
        content: Any,
        header: bool = False,
        start: Optional[int] = None,
        formatting_as_empty: Optional[bool] = False,
    ) -> "Worksheet":
        # files.append_rows_to_worksheet()
        if self.name not in self._workbook.list_worksheets():
            self._workbook.create_worksheet(self.name)

        self._workbook.excel.append_worksheet(
            self.name, content, header, start, formatting_as_empty
        )
        return self

    def insert_image(self):
        # files.insert_image_to_worksheet()
        pass

    def as_table(
        self,
        header: bool = False,
        trim: bool = True,
        start: Optional[int] = None,
    ) -> Table:
        # files.read_worksheet_as_table()
        tables = Tables()
        sheet = self._workbook.excel.read_worksheet(self.name, header, start)
        return tables.create_table(sheet, trim)

    def read_worksheet(self) -> List[dict]:
        # files.read_worksheet()
        # FIXME: actually implement
        return self._workbook.excel.read_worksheet(self.name)

    def rename(self):
        # files.rename_worksheet()
        pass

    # Column operations
    def delete_columns(self, start, end):
        # files.delete_columns()
        return None

    def auto_size_columns(self, start_column, end_column, width):
        # files.auto_size_columns()
        pass

    def hide_columns(self, start_column, end_column):
        # files.hide_columns()
        pass

    def insert_columns_after(self, column, amount):
        # files.insert_columns_after()
        pass

    def insert_columns_before(self, column, amount) -> None:
        # files.insert_columns_before()
        pass

    def unhide_columns(self, start_column, end_column) -> None:
        # files.unhide_columns()
        pass

    # Row operations
    def delete_rows(self, start, end) -> None:
        # files.delete_rows()
        pass

    def find_empty_row(self, name) -> int:
        # files.find_empty_row()
        return 0

    def insert_rows_after(self, row, amount) -> None:
        # files.insert_rows_after()
        pass

    def insert_rows_before(self, row, amount) -> None:
        # files.insert_rows_before()
        pass

    # manipulate ranges of cells
    def move_range(self, range_string, rows, columns, translate) -> None:
        # files.move_range()
        pass

    def set_styles(self, args) -> None:
        # files.set_styles()
        pass

    def get_cell_value(self):
        # files.get_cell_value()
        pass

    @deprecated("Use get_cell_value instead")
    def get_value(self, row, column) -> Any:
        # files.get_worksheet_value()
        # This was actually an alias for get cell value
        return None

    def set_cell_value(self):
        # files.set_cell_value()
        pass

    @deprecated("Use set_cell_value instead")
    def set_value(self):
        # files.set_worksheet_value()
        # This was actually just an alias for set cell value
        pass

    def set_cell_values(self):
        # files.set_cell_values()
        pass

    def set_cell_format(self):
        # files.set_cell_format()
        pass

    def set_cell_formula(self):
        # files.set_cell_formula()
        pass

    def copy_cell_values(self):
        # files.copy_cell_values()
        pass

    def clear_cell_range(self):
        # files.clear_cell_range()
        pass
