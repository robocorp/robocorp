<!-- markdownlint-disable -->

# module `robocorp.excel.excel`

**Source:** [`excel.py:0`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/excel.py#L0)

______________________________________________________________________

## function `create_workbook`

**Source:** [`excel.py:9`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/excel.py#L9)

```python
create_workbook(
    fmt: Literal['xlsx', 'xls'] = 'xlsx',
    sheet_name: Optional[str] = None
) → Workbook
```

Create and open a new Excel workbook in memory.

Automatically also creates a new worksheet with the name `sheet_name`.

**Note:** Use the `save` method to store the workbook into file.

**Args:**

- <b>`fmt`</b>:  The file format for the workbook. Supported file formats: `xlsx`, `xls`.
- <b>`sheet_name`</b>:  The name for the initial sheet. If None, then set to `Sheet`.

**Returns:**

- <b>`Workbook`</b>:  The created Excel workbook object.

**Example:**
.. code-block:: python

workbook = create_workbook("xlsx", sheet_name="Sheet1")

______________________________________________________________________

## function `open_workbook`

**Source:** [`excel.py:50`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/excel.py#L50)

```python
open_workbook(
    path: Union[str, Path],
    data_only: bool = False,
    read_only: bool = False
) → Workbook
```

Open an existing Excel workbook.

Opens the workbook in memory. The file can be in either `.xlsx` or `.xls` format.

**Args:**

- <b>`path`</b>:  path to Excel file
- <b>`data_only`</b>:  controls whether cells with formulas have either the formula (default, False) or the value stored the last time Excel read the sheet (True). Affects only `.xlsx` files.

**Returns:**

- <b>`Workbook`</b>:  Workbook object

**Example:**

:

```

        # Open workbook with only path provided        workbook = open_workbook("path/to/file.xlsx")

        # Open workbook with path provided and reading formulas in cells        # as the value stored        # Note: Can only be used with XLSX workbooks        workbook = open_workbook("path/to/file.xlsx", data_only=True)


```
