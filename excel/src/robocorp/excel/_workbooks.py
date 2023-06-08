import logging
import pathlib
from collections import defaultdict
from contextlib import contextmanager
from io import BytesIO
from typing import Any, List, Optional, Union

import openpyxl
import xlrd
import xlwt
from openpyxl.utils import get_column_letter
from openpyxl.utils.exceptions import InvalidFileException
from xlutils.copy import copy as xlutils_copy

from robocorp.excel._types import PathType
from robocorp.excel.tables import Table
from robocorp.excel.worksheet import Worksheet


def _get_column_index(column: str) -> int:
    """Get column index from name, e.g. A -> 1, D -> 4, AC -> 29.

    Reverse of `get_column_letter()`
    """
    column = str(column).lower()

    col = 0
    for digit, char in enumerate(column[::-1]):
        value = ord(char) - 96
        col += (26**digit) * value

    return col


def _ensure_unique(values: Any) -> List[Any]:
    """Ensures that each string value in the list is unique.

    Adds a suffix to each value that has duplicates,
    e.g. [Banana, Apple, Lemon, Apple] -> [Banana, Apple, Lemon, Apple_2]
    """

    def to_unique(values: Any) -> List[Any]:
        output = []
        seen = defaultdict(int)
        for value in values:
            if seen[value] and isinstance(value, str):
                output.append("%s_%d" % (value, seen[value] + 1))
            else:
                output.append(value)
            seen[value] += 1
        return output

    # Repeat process until each column is unique
    output = to_unique(values)
    while True:
        verify = to_unique(output)
        if output == verify:
            break
        output = verify

    return output


def _load_workbook(
    path: PathType, data_only: bool, read_only: bool
) -> Union["XlsWorkbook", "XlsxWorkbook"]:
    # pylint: disable=broad-except
    parsed_path = pathlib.Path(path).resolve(strict=True)

    try:
        book = XlsxWorkbook()
        book.open(parsed_path, data_only=data_only, read_only=read_only)
        return book
    except InvalidFileException as exc:
        logging.debug(exc)  # Unsupported extension, silently try xlrd
    except Exception as exc:
        logging.info("Failed to open as Office Open XML (.xlsx) format: %s", exc)

    if data_only or read_only:
        raise ValueError("Xls workbooks don't support data_only or read_only options")

    try:
        book = XlsWorkbook(parsed_path)
        book.open(parsed_path)
        return book
    except Exception as exc:
        logging.info("Failed to open as Excel Binary Format (.xls): %s", exc)

    raise ValueError(
        f'Failed to open Excel file ("{path}"), '
        "verify that the path and extension are correct"
    )


class BaseWorkbook:
    """Common logic for both .xls and .xlsx files management."""

    def __init__(self, path: Optional[PathType] = None):
        self.logger = logging.getLogger(__name__)
        # TODO: type hint these
        self.path = path
        self._book = None
        self._extension = None
        self._active = None

    @property
    def book(self):
        return self._book

    def open(self, path, read_only=False, write_only=False, data_only=False):
        self.path = path

    def worksheet(self, name: str) -> Worksheet:
        return Worksheet(self, name)

    def _validate_content(self, props_obj: Any):
        # Strips leading/trailing whitespace in Excel properties.
        public_props = [prop for prop in dir(props_obj) if not prop.startswith("_")]
        for prop in public_props:
            value = getattr(props_obj, prop)
            if value and isinstance(value, str):
                setattr(props_obj, prop, value.strip())


class XlsxWorkbook(BaseWorkbook):
    """Container for manipulating modern Excel files (.xlsx)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._read_only = False

    @staticmethod
    def is_sheet_empty(sheet):
        # Maximum rows/columns are always 1 or more, even when the sheet doesn't
        #  contain cells at all. (https://stackoverflow.com/a/37673211/4766178)
        # _cells does not exist for the ReadOnlyWorksheet, no way of knowing
        # is there data or not
        # pylint: disable=protected-access
        is_readonly = isinstance(sheet, openpyxl.worksheet._read_only.ReadOnlyWorksheet)
        return (
            False if is_readonly else not sheet._cells
        )  # there's no public API for this

    @property
    def sheetnames(self):
        return list(self._book.sheetnames)

    @property
    def active(self):
        if not self._active:
            self._active = self._book.active.title

        return self._active

    @active.setter
    def active(self, value):
        if isinstance(value, int):
            value = self.sheetnames[value]
        elif value not in self.sheetnames:
            raise ValueError(f"Unknown worksheet: {value}")

        self._book.active = self.sheetnames.index(value)
        self._active = value

    @property
    def extension(self):
        return self._extension

    @property
    def read_only(self):
        return self._read_only

    def _get_sheetname(self, name=None):
        if not self.sheetnames:
            raise ValueError("No worksheets in file")

        if name is None:
            name = self.active
        elif isinstance(name, int):
            name = self.sheetnames[name]

        return name

    def _get_cellname(self, row, column):
        row = int(row)
        try:
            column = int(column)
            column = get_column_letter(column)
        except ValueError:
            pass
        return "%s%s" % (column, row)

    def _to_index(self, value):
        value = int(value) if value is not None else 1
        if value < 1:
            raise ValueError("Invalid row index")
        return value

    def create(self):
        self._book = openpyxl.Workbook()
        self._extension = None

    def open(self, path, read_only=False, write_only=False, data_only=False):
        self._read_only = read_only
        if not path:
            raise ValueError("No path defined for workbook")

        try:
            extension = pathlib.Path(path).suffix
        except TypeError:
            extension = None

        options = {"filename": path, "data_only": data_only}

        # Only set mode arguments if truthy, otherwise openpyxl complains
        if read_only and write_only:
            raise ValueError("Unable to use both write_only and read_only mode")
        elif read_only:
            options["read_only"] = True
        elif write_only:
            options["write_only"] = True

        if extension in (".xlsm", ".xltm"):
            options["keep_vba"] = True

        self._book = openpyxl.load_workbook(**options)
        self._extension = extension
        super().open(path, read_only, write_only, data_only)

    def close(self):
        self._book.close()
        self._book = None
        self._extension = None
        self._active = None

    def validate_content(self):
        self._validate_content(self._book.properties)

    def save(self, path: Union[PathType, BytesIO]):
        if not isinstance(path, BytesIO):
            path = str(pathlib.Path(path))
        if not path:
            raise ValueError("No path defined for workbook")

        self._book.save(filename=path)

    def create_worksheet(self, name):
        self._book.create_sheet(title=name)
        self.active = name

    def read_worksheet(self, name=None, header=False, start=None) -> List[dict]:
        name = self._get_sheetname(name)
        sheet = self._book[name]
        start = self._to_index(start)

        if start > sheet.max_row or self.is_sheet_empty(sheet):
            return []

        if header:
            columns = [cell.value for cell in sheet[start]]
            start += 1
        else:
            columns = [get_column_letter(i + 1) for i in range(sheet.max_column)]

        columns = [str(value) if value is not None else value for value in columns]
        columns = _ensure_unique(columns)

        data = []
        for cells in sheet.iter_rows(min_row=start):
            row = {}
            for c, acell in enumerate(cells):
                column = columns[c]
                if column is not None:
                    row[column] = acell.value
            data.append(row)

        self.active = name
        return data

    def append_worksheet(
        self,
        name=None,
        content=None,
        header=False,
        start=None,
        formatting_as_empty=False,
    ):
        content = Table(content)
        if not content:
            return

        sheet_name = self._get_sheetname(name)
        sheet = self._book[sheet_name]
        start = self._to_index(start)
        is_empty = self.is_sheet_empty(sheet)

        if header and not is_empty:
            columns = [cell.value for cell in sheet[start]]
        else:
            columns = content.columns

        if header and is_empty:
            sheet.append(columns)

        if formatting_as_empty:
            self._append_on_first_empty_based_on_values(content, columns, sheet)
        else:
            self._default_append_rows(content, columns, sheet)

        self.active = sheet_name

    def _append_on_first_empty_based_on_values(self, content, columns, sheet):
        first_empty_row: Optional[int] = None
        for row_num in range(sheet.max_row, 0, -1):
            if all(cell.value is None for cell in sheet[row_num]):
                first_empty_row = row_num
            else:
                break
        first_empty_row: int = first_empty_row or sheet.max_row + 1
        for row_idx, row in enumerate(content):
            values = self._row_to_values(row, columns)
            for cell_idx, acell in enumerate(sheet[first_empty_row + row_idx]):
                try:
                    acell.value = values[cell_idx]
                except IndexError:
                    pass

    def _default_append_rows(self, content, columns, sheet):
        for row in content:
            values = self._row_to_values(row, columns)
            sheet.append(values)

    def _row_to_values(self, row, columns):
        values = [""] * len(columns)
        for column, value in row.items():
            try:
                index = columns.index(column)
                values[index] = value
            except ValueError:
                pass
        return values

    def remove_worksheet(self, name=None):
        name = self._get_sheetname(name)
        others = [sheet for sheet in self.sheetnames if sheet != name]

        if not others:
            raise ValueError("Workbook must have at least one other worksheet")

        if name == self.active:
            self.active = others[0]

        sheet = self._book[name]
        self._book.remove(sheet)

    def rename_worksheet(self, title, name=None):
        title = str(title)
        name = self._get_sheetname(name)
        sheet = self._book[name]

        sheet.title = title
        self.active = title

    def find_empty_row(self, name=None):
        name = self._get_sheetname(name)
        sheet = self._book[name]

        for idx in reversed(range(sheet.max_row)):
            idx += 1  # Convert to 1-based indexing
            if any(value for value in sheet[idx]):
                return idx + 1  # Return first empty row

        return 1

    def get_cell_value(self, row, column, name=None):
        name = self._get_sheetname(name)
        sheet = self._book[name]
        cell = self._get_cellname(row, column)

        return sheet[cell].value

    def set_cell_value(self, row, column, value, name=None):
        name = self._get_sheetname(name)
        sheet = self._book[name]
        cell = self._get_cellname(row, column)

        sheet[cell].value = value

    def set_cell_format(self, row, column, fmt, name=None):
        name = self._get_sheetname(name)
        sheet = self._book[name]
        cell = self._get_cellname(row, column)

        sheet[cell].number_format = str(fmt)

    def insert_image(self, row, column, image, name=None):
        name = self._get_sheetname(name)
        sheet = self._book[name]
        cell = self._get_cellname(row, column)

        # For compatibility with openpyxl
        stream = BytesIO()
        image.save(stream, format=image.format)
        image.fp = stream

        img = openpyxl.drawing.image.Image(image)
        img.anchor = cell
        sheet.add_image(img)


class XlsWorkbook(BaseWorkbook):
    """Container for manipulating legacy Excel files (.xls)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._images = []

    @staticmethod
    def is_sheet_empty(sheet):
        return not any([sheet.ncols, sheet.nrows])

    @property
    def sheetnames(self):
        return [sheet.name for sheet in self._book.sheets()]

    @property
    def active(self):
        if not self._active:
            for sheet in self._book.sheets():
                if sheet.sheet_visible:
                    self._active = sheet.name
                    break
            else:
                self._active = self.sheetnames[0]

        return self._active

    @active.setter
    def active(self, value):
        if isinstance(value, int):
            value = self.sheetnames[value]
        elif value not in self.sheetnames:
            raise ValueError(f"Unknown worksheet: {value}")

        for sheet in self._book.sheets():
            match = int(sheet.name == value)
            sheet.sheet_selected = match
            sheet.sheet_visible = match

        self._active = value

    @property
    def extension(self) -> Optional[str]:
        return self._extension

    def _get_sheetname(self, name):
        if self._book.nsheets == 0:
            raise ValueError("No worksheets in file")

        if name is None:
            name = self.active
        elif isinstance(name, int):
            name = self.sheetnames[name]
        elif name not in self.sheetnames:
            raise ValueError(f"Unknown worksheet: {name}")

        return name

    def _get_cell(self, row, column):
        row = int(row)
        try:
            column = int(column)
        except ValueError:
            column = _get_column_index(column)
        return row - 1, column - 1

    def _to_index(self, value):
        value = (int(value) - 1) if value is not None else 0
        if value < 0:
            raise ValueError("Invalid row index")
        return value

    def create(self, sheet="Sheet"):
        # TODO: make both this and the other create default to `Sheet1` or whatever is
        # excel default

        fd = BytesIO()
        try:
            book = xlwt.Workbook()
            book.add_sheet(sheet)
            book.save(fd)
            fd.seek(0)
            self.open(fd)
        finally:
            fd.close()

        self._extension = None

    def open(self, path, read_only=False, write_only=False, data_only=False):
        path = path
        if not path:
            raise ValueError("No path defined for workbook")

        try:
            extension = pathlib.Path(path).suffix
        except TypeError:
            extension = None

        options = {"on_demand": True, "formatting_info": True}

        if read_only or write_only or data_only:
            self.logger.info(
                "Modes read_only/write_only/data_only not supported with .xls"
            )

        if hasattr(path, "read"):
            options["file_contents"] = path.read()
        else:
            options["filename"] = path

        self._book = xlrd.open_workbook(**options)
        self._extension = extension
        self._images = []

    def close(self):
        self._book.release_resources()
        self._book = None
        self._extension = None
        self._active = None
        self._images = []

    @contextmanager
    def _book_write(self):
        book = xlutils_copy(self._book)
        yield book

        fd = BytesIO()
        try:
            book.save(fd)
            fd.seek(0)
            self.close()
            self.open(fd)
        finally:
            fd.close()

    def validate_content(self):
        self._validate_content(self._book)

    def save(self, path: Union[PathType, BytesIO]):
        if not isinstance(path, BytesIO):
            path = str(pathlib.Path(path))
        if not path:
            raise ValueError("No path defined for workbook")

        book = xlutils_copy(self._book)
        self._insert_images(book)
        book.save(path)

    def create_worksheet(self, name):
        with self._book_write() as book:
            book.add_sheet(name)

        self.active = name

    def read_worksheet(self, name=None, header=False, start=None) -> List[dict]:
        name = self._get_sheetname(name)
        sheet = self._book.sheet_by_name(name)
        start = self._to_index(start)

        if start >= sheet.nrows:
            return []

        if header:
            columns = [self._parse_type(cell) for cell in sheet.row(start)]
            start += 1
        else:
            columns = [get_column_letter(i + 1) for i in range(sheet.ncols)]

        columns = [value if value != "" else None for value in columns]
        columns = [str(value) if value is not None else value for value in columns]
        columns = _ensure_unique(columns)

        data = []
        for r in range(start, sheet.nrows):
            row = {}
            for c in range(sheet.ncols):
                column = columns[c]
                if column is not None:
                    cell = sheet.cell(r, c)
                    row[column] = self._parse_type(cell)
            data.append(row)

        self.active = name
        return data

    def _parse_type(self, cell):
        value = cell.value

        if cell.ctype == xlrd.XL_CELL_DATE:
            value = xlrd.xldate_as_datetime(value, self._book.datemode)
        elif cell.ctype == xlrd.XL_CELL_BOOLEAN:
            value = bool(value)
        elif cell.ctype == xlrd.XL_CELL_ERROR:
            value = xlrd.biffh.error_text_from_code.get(value, "#ERROR")
        elif cell.ctype == xlrd.XL_CELL_NUMBER and value.is_integer():
            value = int(value)

        return value

    def append_worksheet(
        self,
        name=None,
        content=None,
        header=False,
        start=None,
        formatting_as_empty=False,
    ):
        content = Table(content)
        if not content:
            return

        name = self._get_sheetname(name)
        sheet_read = self._book.sheet_by_name(name)
        start = self._to_index(start)
        is_empty = self.is_sheet_empty(sheet_read)

        if header and not is_empty:
            columns = [cell.value for cell in sheet_read.row(start)]
        else:
            columns = content.columns

        with self._book_write() as book:
            sheet_write = book.get_sheet(name)
            # TODO. target worksheet cell formatting is overwritten.
            # It would be preferable to preserve formatting in the
            # target worksheet.
            if formatting_as_empty:
                start_row = self._return_first_empty_row(sheet_read)
            else:
                start_row = sheet_read.nrows
            if header and is_empty:
                for column, value in enumerate(columns):
                    sheet_write.write(0, column, value)
                start_row += 1

            for r, row in enumerate(content, start_row):
                for column, value in row.items():
                    sheet_write.write(r, columns.index(column), value)

        self.active = name

    def _return_first_empty_row(self, sheet):
        first_empty_row: Optional[int] = None
        for row_num in range(sheet.nrows - 1, 0, -1):
            if all(cell.value == "" for cell in sheet[row_num]):
                first_empty_row = row_num
            else:
                break
        first_empty_row: int = first_empty_row or sheet.nrows
        return first_empty_row

    def remove_worksheet(self, name=None):
        name = self._get_sheetname(name)
        others = [sheet for sheet in self.sheetnames if sheet != name]

        if not others:
            raise ValueError("Workbook must have at least one other worksheet")

        if name == self.active:
            self.active = others[0]

        with self._book_write() as book:
            # This is pretty ugly, but there seems to be no other way to
            # remove sheets from the xlwt.Workbook instance
            # pylint: disable=protected-access
            book._Workbook__worksheets = [
                sheet for sheet in book._Workbook__worksheets if sheet.name != name
            ]
            book._Workbook__active_sheet = next(
                idx
                for idx, sheet in enumerate(book._Workbook__worksheets)
                if sheet.name == self.active
            )

    def rename_worksheet(self, title, name=None):
        title = str(title)
        name = self._get_sheetname(name)

        with self._book_write() as book:
            sheet = book.get_sheet(name)
            sheet.name = title

        self.active = title

    def find_empty_row(self, name=None):
        name = self._get_sheetname(name)
        sheet = self._book.sheet_by_name(name)

        for row in reversed(range(sheet.nrows)):
            if any(cell.value for cell in sheet.row(row)):
                # Convert to 1-based indexing and
                # return first empty row
                return row + 2

        return 1

    def get_cell_value(self, row, column, name=None):
        name = self._get_sheetname(name)
        sheet = self._book.sheet_by_name(name)
        row, column = self._get_cell(row, column)

        return sheet.cell_value(row, column)

    def set_cell_value(self, row, column, value, name=None):
        name = self._get_sheetname(name)
        row, column = self._get_cell(row, column)

        with self._book_write() as book:
            sheet = book.get_sheet(name)
            sheet.write(row, column, value)

    def set_cell_format(self, row, column, fmt, name=None):
        name = self._get_sheetname(name)
        sheet = self._book.sheet_by_name(name)
        row, column = self._get_cell(row, column)

        value = sheet.cell_value(row, column)
        style = xlwt.XFStyle()
        style.num_format_str = str(fmt)

        with self._book_write() as book:
            sheet = book.get_sheet(name)
            sheet.write(row, column, value, style)

    def insert_image(self, row, column, image, name=None):
        name = self._get_sheetname(name)
        row, column = self._get_cell(row, column)
        self._images.append((name, row, column, image))

    def _insert_images(self, book):
        for name, row, column, image in self._images:
            stream = BytesIO()
            image.save(stream, format="BMP")
            bitmap = stream.getvalue()

            sheet = book.get_sheet(name)
            sheet.insert_bitmap_data(bitmap, row, column)
