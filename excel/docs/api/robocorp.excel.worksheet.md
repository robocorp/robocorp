<!-- markdownlint-disable -->

# module `robocorp.excel.worksheet`
**Source:** [`worksheet.py:0`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L0)



## Variables
- **TYPE_CHECKING**



---

## class `Worksheet`
**Source:** [`worksheet.py:13`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L13)
Common class for worksheets to manage the worksheet's content.

### method `__init__`
**Source:** [`worksheet.py:16`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L16)

```python
__init__(workbook: 'Workbook', name: str)
```







---

### method `append_rows_to_worksheet`
**Source:** [`worksheet.py:22`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L22)

```python
append_rows_to_worksheet(
    content: Any,
    header: bool = False,
    start: Optional[int] = None,
    formatting_as_empty: Optional[bool] = False
) → Worksheet
```




---

### method `as_list`
**Source:** [`worksheet.py:64`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L64)

```python
as_list(header=False, start=None) → List[dict]
```




---

### method `as_table`
**Source:** [`worksheet.py:53`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L53)

```python
as_table(
    header: bool = False,
    trim: bool = True,
    start: Optional[int] = None
) → Table
```




---

### method `auto_size_columns`
**Source:** [`worksheet.py:80`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L80)

```python
auto_size_columns(start_column, end_column, width)
```




---

### method `clear_cell_range`
**Source:** [`worksheet.py:168`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L168)

```python
clear_cell_range()
```




---

### method `copy_cell_values`
**Source:** [`worksheet.py:164`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L164)

```python
copy_cell_values()
```




---

### method `delete_columns`
**Source:** [`worksheet.py:76`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L76)

```python
delete_columns(start, end)
```




---

### method `delete_rows`
**Source:** [`worksheet.py:101`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L101)

```python
delete_rows(start, end) → None
```




---

### method `find_empty_row`
**Source:** [`worksheet.py:105`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L105)

```python
find_empty_row() → int
```




---

### method `get_cell_value`
**Source:** [`worksheet.py:126`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L126)

```python
get_cell_value(row, column)
```




---

### method `get_value`
**Source:** [`get_value:130`](https://github.com/robocorp/robo/tree/master/excel/robocorp/excel/worksheet/get_value#L130)

```python
get_value(row, column) → Any
```




---

### method `hide_columns`
**Source:** [`worksheet.py:84`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L84)

```python
hide_columns(start_column, end_column)
```




---

### method `insert_columns_after`
**Source:** [`worksheet.py:88`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L88)

```python
insert_columns_after(column, amount)
```




---

### method `insert_columns_before`
**Source:** [`worksheet.py:92`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L92)

```python
insert_columns_before(column, amount) → None
```




---

### method `insert_image`
**Source:** [`worksheet.py:38`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L38)

```python
insert_image(
    row: int,
    column: Union[int, str],
    path: Union[str, Path],
    scale: float = 1.0
)
```




---

### method `insert_rows_after`
**Source:** [`worksheet.py:109`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L109)

```python
insert_rows_after(row, amount) → None
```




---

### method `insert_rows_before`
**Source:** [`worksheet.py:113`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L113)

```python
insert_rows_before(row, amount) → None
```




---

### method `move_range`
**Source:** [`worksheet.py:118`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L118)

```python
move_range(range_string, rows, columns, translate) → None
```




---

### method `rename`
**Source:** [`worksheet.py:69`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L69)

```python
rename(name)
```




---

### method `set_cell_format`
**Source:** [`worksheet.py:153`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L153)

```python
set_cell_format(row: int, column: Union[str, int], fmt: Optional[str, float])
```




---

### method `set_cell_formula`
**Source:** [`worksheet.py:160`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L160)

```python
set_cell_formula()
```




---

### method `set_cell_value`
**Source:** [`worksheet.py:136`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L136)

```python
set_cell_value(
    row: int,
    column: Union[str, int],
    value: Any,
    fmt: Optional[str, float] = None
)
```




---

### method `set_cell_values`
**Source:** [`worksheet.py:149`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L149)

```python
set_cell_values()
```




---

### method `set_styles`
**Source:** [`worksheet.py:122`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L122)

```python
set_styles(args) → None
```




---

### method `unhide_columns`
**Source:** [`worksheet.py:96`](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/worksheet.py#L96)

```python
unhide_columns(start_column, end_column) → None
```





