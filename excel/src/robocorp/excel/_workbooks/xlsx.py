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
