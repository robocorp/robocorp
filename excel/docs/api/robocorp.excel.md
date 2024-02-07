<!-- markdownlint-disable -->

# module `robocorp.excel`

**Source:** [`__init__.py:0`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/__init__.py#L0)

Main module for doing Excel automation.

This library can be made available by pinning ![](https://img.shields.io/pypi/v/robocorp-excel?label=robocorp-excel) in your dependencies' configuration.

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

````

        # Open workbook with only path provided        workbook = open_workbook("path/to/file.xlsx")

        # Open workbook with path provided and reading formulas in cells        # as the value stored        # Note: Can only be used with XLSX workbooks        workbook = open_workbook("path/to/file.xlsx", data_only=True)


---

## class `Table`

**Source:** [`tables.py:122`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L122)

Container class for tabular data.



**Note:**

>Supported data formats:
>- empty: None values populated according to columns/index - list: list of data Rows - dict: Dictionary of columns as keys and Rows as values - table: An existing Table
>Row: a namedtuple, dictionary, list or a tuple

### method `__init__`

**Source:** [`tables.py:137`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L137)


```python
__init__(
    data: Optional[Dict[Union[int, str], Union[Dict, List, Tuple, NamedTuple, set]], List[Union[Dict, List, Tuple, NamedTuple, set]], ForwardRef('Table')] = None,
    columns: Optional[List[str]] = None
)
````

Creates a Table object.

**Args:**

- <b>`data`</b>:      Values for table,  see `Supported data formats`
- <b>`columns`</b>:   Names for columns, should match data dimensions

#### property `columns`

#### property `data`

#### property `dimensions`

#### property `index`

#### property `size`

______________________________________________________________________

### method `append_column`

**Source:** [`tables.py:702`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L702)

```python
append_column(column=None, values=None)
```

______________________________________________________________________

### method `append_row`

**Source:** [`tables.py:693`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L693)

```python
append_row(row=None)
```

Append new row to table.

______________________________________________________________________

### method `append_rows`

**Source:** [`tables.py:697`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L697)

```python
append_rows(rows)
```

Append multiple rows to table.

______________________________________________________________________

### method `append_table`

**Source:** [`tables.py:735`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L735)

```python
append_table(table)
```

Append data from table to current data.

______________________________________________________________________

### method `clear`

**Source:** [`tables.py:468`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L468)

```python
clear()
```

Remove all rows from this table.

______________________________________________________________________

### method `column_location`

**Source:** [`tables.py:384`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L384)

```python
column_location(value)
```

Find location for column value.

______________________________________________________________________

### method `copy`

**Source:** [`tables.py:464`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L464)

```python
copy()
```

Create a copy of this table.

______________________________________________________________________

### method `delete_columns`

**Source:** [`tables.py:720`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L720)

```python
delete_columns(columns)
```

Remove columns with matching names.

______________________________________________________________________

### method `delete_rows`

**Source:** [`tables.py:708`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L708)

```python
delete_rows(indexes: Union[int, str, List[Union[int, str]]])
```

Remove rows with matching indexes.

______________________________________________________________________

### method `filter_all`

**Source:** [`tables.py:806`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L806)

```python
filter_all(
    condition: Callable[[Union[int, str, Dict, List, Tuple, NamedTuple, set]], bool]
)
```

Remove rows by evaluating `condition` for every row.

The filtering will be done in-place and all the rows evaluating as falsy through the provided condition will be removed.

______________________________________________________________________

### method `filter_by_column`

**Source:** [`tables.py:819`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L819)

```python
filter_by_column(column: Union[int, str], condition: Callable[[Any], bool])
```

Remove rows by evaluating `condition` for cells in `column`.

The filtering will be done in-place and all the rows where it evaluates to falsy are removed.

______________________________________________________________________

### method `get`

**Source:** [`tables.py:482`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L482)

```python
get(indexes=None, columns=None, as_list=False)
```

Get values from table. Return type depends on input dimensions.

If `indexes` and `columns` are scalar, i.e. not lists: Returns single cell value

If either `indexes` or `columns` is a list: Returns matching row or column

If both `indexes` and `columns` are lists: Returns a new Table instance with matching cell values

**Args:**

- <b>`indexes`</b>:  List of indexes, or all if not given.
- <b>`columns`</b>:  List of columns, or all if not given.
- <b>`as_list`</b>:  Return as list, instead of dictionary.

______________________________________________________________________

### method `get_cell`

**Source:** [`tables.py:511`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L511)

```python
get_cell(index, column)
```

Get single cell value.

______________________________________________________________________

### method `get_column`

**Source:** [`tables.py:542`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L542)

```python
get_column(column, indexes=None, as_list=False)
```

Get row values from column.

**Args:**

- <b>`column`</b>:  Name for column
- <b>`indexes`</b>:  Row indexes to include, or all if not given
- <b>`as_list`</b>:  Return column as dictionary, instead of list

______________________________________________________________________

### method `get_row`

**Source:** [`tables.py:518`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L518)

```python
get_row(index: Union[int, str], columns=None, as_list=False)
```

Get column values from row.

**Args:**

- <b>`index`</b>:    Index for row.
- <b>`columns`</b>:  Column names to include, or all if not given.
- <b>`as_list`</b>:  Return row as list, instead of dictionary.

______________________________________________________________________

### method `get_slice`

**Source:** [`tables.py:585`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L585)

```python
get_slice(start: Optional[int, str] = None, end: Optional[int, str] = None)
```

Get a new table from rows between start and end index.

______________________________________________________________________

### method `get_table`

**Source:** [`tables.py:566`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L566)

```python
get_table(
    indexes=None,
    columns=None,
    as_list=False
) → Union[List, ForwardRef('Table')]
```

Get a new table from all cells matching indexes and columns.

______________________________________________________________________

### method `group_by_column`

**Source:** [`tables.py:785`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L785)

```python
group_by_column(column)
```

Group rows by column value and return as list of tables.

______________________________________________________________________

### method `head`

**Source:** [`tables.py:472`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L472)

```python
head(rows, as_list=False)
```

Return first n rows of table.

______________________________________________________________________

### method `index_location`

**Source:** [`tables.py:367`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L367)

```python
index_location(value: Union[int, str]) → int
```

______________________________________________________________________

### method `iter_dicts`

**Source:** [`tables.py:840`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L840)

```python
iter_dicts(
    with_index=True
) → Generator[Dict[Union[int, str], Any], NoneType, NoneType]
```

Iterate rows with values as dicts.

______________________________________________________________________

### method `iter_lists`

**Source:** [`tables.py:832`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L832)

```python
iter_lists(with_index=True)
```

Iterate rows with values as lists.

______________________________________________________________________

### method `iter_tuples`

**Source:** [`tables.py:848`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L848)

```python
iter_tuples(with_index=True, name='Row')
```

Iterate rows with values as namedtuples.

Converts column names to valid Python identifiers, e.g. "First Name" -> "First_Name"

______________________________________________________________________

### method `set`

**Source:** [`tables.py:625`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L625)

```python
set(indexes=None, columns=None, values=None)
```

Sets multiple cell values at a time.

Both `indexes` and `columns` can be scalar or list-like, which enables setting individual cells, rows/columns, or regions.

If `values` is scalar, all matching cells will be set to that value. Otherwise, the length should match the cell count defined by the other parameters.

______________________________________________________________________

### method `set_cell`

**Source:** [`tables.py:649`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L649)

```python
set_cell(index, column, value)
```

Set individual cell value.

If either index or column is missing, they are created.

______________________________________________________________________

### method `set_column`

**Source:** [`tables.py:678`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L678)

```python
set_column(column, values)
```

Set values in column. If column is missing, it is created.

______________________________________________________________________

### method `set_row`

**Source:** [`tables.py:666`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L666)

```python
set_row(index, values)
```

Set values in row. If index is missing, it is created.

______________________________________________________________________

### method `sort_by_column`

**Source:** [`tables.py:747`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L747)

```python
sort_by_column(columns, ascending=False)
```

Sort table by columns.

______________________________________________________________________

### method `tail`

**Source:** [`tables.py:477`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L477)

```python
tail(rows, as_list=False)
```

Return last n rows of table.

______________________________________________________________________

### method `to_dict`

**Source:** [`tables.py:878`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L878)

```python
to_dict(with_index=True)
```

Convert table to dict representation.

______________________________________________________________________

### method `to_list`

**Source:** [`tables.py:864`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L864)

```python
to_list(with_index=True)
```

Convert table to list representation.
