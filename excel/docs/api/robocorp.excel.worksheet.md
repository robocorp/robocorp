<!-- markdownlint-disable -->

# module `robocorp.excel.worksheet`

# Variables

- **TYPE_CHECKING**

# Functions

______________________________________________________________________

# Class `Worksheet`

Common class for worksheets to manage the worksheet's content.

### `__init__`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L16)

```python
__init__(workbook: 'Workbook', name: str)
```

## Methods

______________________________________________________________________

### `append_rows_to_worksheet`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L22)

```python
append_rows_to_worksheet(
    content: Any,
    header: bool = False,
    start: Optional[int] = None,
    formatting_as_empty: Optional[bool] = False
) → Worksheet
```

______________________________________________________________________

### `as_list`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L64)

```python
as_list(header=False, start=None) → List[dict]
```

______________________________________________________________________

### `as_table`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L53)

```python
as_table(
    header: bool = False,
    trim: bool = True,
    start: Optional[int] = None
) → Table
```

______________________________________________________________________

### `auto_size_columns`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L80)

```python
auto_size_columns(start_column, end_column, width)
```

______________________________________________________________________

### `clear_cell_range`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L168)

```python
clear_cell_range()
```

______________________________________________________________________

### `copy_cell_values`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L164)

```python
copy_cell_values()
```

______________________________________________________________________

### `delete_columns`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L76)

```python
delete_columns(start, end)
```

______________________________________________________________________

### `delete_rows`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L101)

```python
delete_rows(start, end) → None
```

______________________________________________________________________

### `find_empty_row`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L105)

```python
find_empty_row() → int
```

______________________________________________________________________

### `get_cell_value`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L126)

```python
get_cell_value(row, column)
```

______________________________________________________________________

### `get_value`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/robocorp/excel/worksheet/get_value#L130)

```python
get_value(row, column) → Any
```

______________________________________________________________________

### `hide_columns`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L84)

```python
hide_columns(start_column, end_column)
```

______________________________________________________________________

### `insert_columns_after`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L88)

```python
insert_columns_after(column, amount)
```

______________________________________________________________________

### `insert_columns_before`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L92)

```python
insert_columns_before(column, amount) → None
```

______________________________________________________________________

### `insert_image`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L38)

```python
insert_image(
    row: int,
    column: Union[int, str],
    path: Union[str, Path],
    scale: float = 1.0
)
```

______________________________________________________________________

### `insert_rows_after`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L109)

```python
insert_rows_after(row, amount) → None
```

______________________________________________________________________

### `insert_rows_before`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L113)

```python
insert_rows_before(row, amount) → None
```

______________________________________________________________________

### `move_range`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L118)

```python
move_range(range_string, rows, columns, translate) → None
```

______________________________________________________________________

### `rename`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L69)

```python
rename(name)
```

______________________________________________________________________

### `set_cell_format`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L153)

```python
set_cell_format(row: int, column: Union[str, int], fmt: Optional[str, float])
```

______________________________________________________________________

### `set_cell_formula`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L160)

```python
set_cell_formula()
```

______________________________________________________________________

### `set_cell_value`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L136)

```python
set_cell_value(
    row: int,
    column: Union[str, int],
    value: Any,
    fmt: Optional[str, float] = None
)
```

______________________________________________________________________

### `set_cell_values`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L149)

```python
set_cell_values()
```

______________________________________________________________________

### `set_styles`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L122)

```python
set_styles(args) → None
```

______________________________________________________________________

### `unhide_columns`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/worksheet.py#L96)

```python
unhide_columns(start_column, end_column) → None
```
