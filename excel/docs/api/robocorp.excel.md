<!-- markdownlint-disable -->

# module `robocorp.excel`

Main module for doing Excel automation.

This library can be made available by pinning [![](https://img.shields.io/pypi/v/robocorp-excel?label=robocorp-excel)](https://pypi.org/project/robocorp-excel/) in your dependencies' configuration.

# Functions

______________________________________________________________________

## `create_workbook`

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

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/excel.py#L9)

```python
create_workbook(
    fmt: Literal['xlsx', 'xls'] = 'xlsx',
    sheet_name: Optional[str] = None
) → Workbook
```

______________________________________________________________________

## `open_workbook`

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

 [**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/excel.py#L50)

```python
open_workbook(
    path: Union[str, Path],
    data_only: bool = False,
    read_only: bool = False
) → Workbook
````

______________________________________________________________________

# Class `Table`

Container class for tabular data.

**Note:**

> Supported data formats:
>
> - empty: None values populated according to columns/index - list: list of data Rows - dict: Dictionary of columns as keys and Rows as values - table: An existing Table
>   Row: a namedtuple, dictionary, list or a tuple

### `__init__`

Creates a Table object.

**Args:**

- <b>`data`</b>:      Values for table,  see `Supported data formats`
- <b>`columns`</b>:   Names for columns, should match data dimensions

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L165)

```python
__init__(
    data: Optional[Dict[Union[int, str], Union[Dict, Sequence, Tuple, NamedTuple, set]], Sequence[Optional[Dict, Sequence, Tuple, NamedTuple, set]], ForwardRef('Table'), NoneType] = None,
    columns: Optional[List[str]] = None
)
```

## Properties

- `columns`

- `data`

- `dimensions`

- `index`

- `size`

## Methods

______________________________________________________________________

### `append_column`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L748)

```python
append_column(column=None, values=None)
```

______________________________________________________________________

### `append_row`

Append new row to table.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L739)

```python
append_row(row=None)
```

______________________________________________________________________

### `append_rows`

Append multiple rows to table.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L743)

```python
append_rows(rows)
```

______________________________________________________________________

### `append_table`

Append data from table to current data.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L781)

```python
append_table(table)
```

______________________________________________________________________

### `clear`

Remove all rows from this table.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L498)

```python
clear()
```

______________________________________________________________________

### `column_location`

Find location for column value.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L414)

```python
column_location(value)
```

______________________________________________________________________

### `copy`

Create a copy of this table.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L494)

```python
copy()
```

______________________________________________________________________

### `delete_columns`

Remove columns with matching names.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L766)

```python
delete_columns(columns)
```

______________________________________________________________________

### `delete_rows`

Remove rows with matching indexes.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L754)

```python
delete_rows(indexes: Union[int, str, List[Union[int, str]]])
```

______________________________________________________________________

### `filter_all`

Remove rows by evaluating `condition` for every row.

The filtering will be done in-place and all the rows evaluating as falsy through the provided condition will be removed.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L852)

```python
filter_all(
    condition: Callable[[Optional[int, str, Dict, Sequence, Tuple, NamedTuple, set]], bool]
)
```

______________________________________________________________________

### `filter_by_column`

Remove rows by evaluating `condition` for cells in `column`.

The filtering will be done in-place and all the rows where it evaluates to falsy are removed.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L868)

```python
filter_by_column(column: Union[int, str], condition: Callable[[Any], bool])
```

______________________________________________________________________

### `get`

Get values from table. Return type depends on input dimensions.

If `indexes` and `columns` are scalar, i.e. not lists: Returns single cell value

If either `indexes` or `columns` is a list: Returns matching row or column

If both `indexes` and `columns` are lists: Returns a new Table instance with matching cell values

**Args:**

- <b>`indexes`</b>:  List of indexes, or all if not given.
- <b>`columns`</b>:  List of columns, or all if not given.
- <b>`as_list`</b>:  Return as list, instead of dictionary.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L512)

```python
get(indexes=None, columns=None, as_list=False)
```

______________________________________________________________________

### `get_cell`

Get single cell value.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L541)

```python
get_cell(index, column)
```

______________________________________________________________________

### `get_column`

Get row values from column.

**Args:**

- <b>`column`</b>:  Name for column
- <b>`indexes`</b>:  Row indexes to include, or all if not given
- <b>`as_list`</b>:  Return column as dictionary, instead of list

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L576)

```python
get_column(column, indexes=None, as_list=False)
```

______________________________________________________________________

### `get_row`

Get column values from row.

**Args:**

- <b>`index`</b>:    Index for row.
- <b>`columns`</b>:  Column names to include, or all if not given.
- <b>`as_list`</b>:  Return row as list, instead of dictionary.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L548)

```python
get_row(
    index: Union[int, str],
    columns=None,
    as_list=False
) → Union[Dict[str, Union[Dict, Sequence, Tuple, NamedTuple, set, NoneType]], List[Union[Dict, Sequence, Tuple, NamedTuple, set, NoneType]]]
```

______________________________________________________________________

### `get_slice`

Get a new table from rows between start and end index.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L631)

```python
get_slice(start: Optional[int, str] = None, end: Optional[int, str] = None)
```

______________________________________________________________________

### `get_table`

Get a new table from all cells matching indexes and columns.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L612)

```python
get_table(
    indexes=None,
    columns=None,
    as_list=False
) → Union[List, ForwardRef('Table')]
```

______________________________________________________________________

### `group_by_column`

Group rows by column value and return as list of tables.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L831)

```python
group_by_column(column)
```

______________________________________________________________________

### `head`

Return first n rows of table.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L502)

```python
head(rows, as_list=False)
```

______________________________________________________________________

### `index_location`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L397)

```python
index_location(value: Union[int, str]) → int
```

______________________________________________________________________

### `iter_dicts`

Iterate rows with values as dicts.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L892)

```python
iter_dicts(
    with_index=True
) → Generator[Dict[Union[int, str], Any], NoneType, NoneType]
```

______________________________________________________________________

### `iter_lists`

Iterate rows with values as lists.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L884)

```python
iter_lists(with_index=True)
```

______________________________________________________________________

### `iter_tuples`

Iterate rows with values as namedtuples.

Converts column names to valid Python identifiers, e.g. "First Name" -> "First_Name"

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L900)

```python
iter_tuples(with_index=True, name='Row')
```

______________________________________________________________________

### `set`

Sets multiple cell values at a time.

Both `indexes` and `columns` can be scalar or list-like, which enables setting individual cells, rows/columns, or regions.

If `values` is scalar, all matching cells will be set to that value. Otherwise, the length should match the cell count defined by the other parameters.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L671)

```python
set(indexes=None, columns=None, values=None)
```

______________________________________________________________________

### `set_cell`

Set individual cell value.

If either index or column is missing, they are created.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L695)

```python
set_cell(index, column, value)
```

______________________________________________________________________

### `set_column`

Set values in column. If column is missing, it is created.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L724)

```python
set_column(column, values)
```

______________________________________________________________________

### `set_row`

Set values in row. If index is missing, it is created.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L712)

```python
set_row(index, values)
```

______________________________________________________________________

### `sort_by_column`

Sort table by columns.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L793)

```python
sort_by_column(columns, ascending=False)
```

______________________________________________________________________

### `tail`

Return last n rows of table.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L507)

```python
tail(rows, as_list=False)
```

______________________________________________________________________

### `to_dict`

Convert table to dict representation.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L930)

```python
to_dict(with_index=True)
```

______________________________________________________________________

### `to_list`

Convert table to list representation.

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L916)

```python
to_list(with_index=True)
```
