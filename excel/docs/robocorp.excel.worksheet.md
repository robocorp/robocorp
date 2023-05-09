<!-- markdownlint-disable -->

<a href="../../excel/src/robocorp/excel/worksheet.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `robocorp.excel.worksheet`




**Global Variables**
---------------
- **TYPE_CHECKING**


---

<a href="../../excel/src/robocorp/excel/worksheet.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Worksheet`
Common class for worksheets to manage the worksheet's content. 

<a href="../../excel/src/robocorp/excel/worksheet.py#L16"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(workbook: 'Workbook', name: str)
```








---

<a href="../../excel/src/robocorp/excel/worksheet.py#L22"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `append_rows_to_worksheet`

```python
append_rows_to_worksheet(
    content: Any,
    header: bool = False,
    start: Optional[int] = None,
    formatting_as_empty: Optional[bool] = False
) → Worksheet
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `as_list`

```python
as_list(header=False, start=None) → List[dict]
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L53"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `as_table`

```python
as_table(
    header: bool = False,
    trim: bool = True,
    start: Optional[int] = None
) → Table
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L80"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `auto_size_columns`

```python
auto_size_columns(start_column, end_column, width)
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L180"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `clear_cell_range`

```python
clear_cell_range()
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L176"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `copy_cell_values`

```python
copy_cell_values()
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_columns`

```python
delete_columns(start, end)
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_rows`

```python
delete_rows(start, end) → None
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L105"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_empty_row`

```python
find_empty_row() → int
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L126"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_cell_value`

```python
get_cell_value(row, column)
```





---

<a href="../../excel/robocorp/excel/worksheet/get_value#L130"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_value`

```python
get_value(row, column) → Any
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L84"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `hide_columns`

```python
hide_columns(start_column, end_column)
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L88"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert_columns_after`

```python
insert_columns_after(column, amount)
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L92"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert_columns_before`

```python
insert_columns_before(column, amount) → None
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L38"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert_image`

```python
insert_image(
    row: int,
    column: Union[int, str],
    path: Union[str, Path],
    scale: float = 1.0
)
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L109"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert_rows_after`

```python
insert_rows_after(row, amount) → None
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L113"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert_rows_before`

```python
insert_rows_before(row, amount) → None
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L118"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `move_range`

```python
move_range(range_string, rows, columns, translate) → None
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L69"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rename`

```python
rename(name)
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L165"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_cell_format`

```python
set_cell_format(row: int, column: Union[str, int], fmt: Optional[str, float])
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L172"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_cell_formula`

```python
set_cell_formula()
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L136"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_cell_value`

```python
set_cell_value(
    row: int,
    column: Union[str, int],
    value: Any,
    fmt: Optional[str, float] = None
)
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L161"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_cell_values`

```python
set_cell_values()
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_styles`

```python
set_styles(args) → None
```





---

<a href="../../excel/robocorp/excel/worksheet/set_value#L149"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_value`

```python
set_value(
    row: int,
    column: Union[str, int],
    value: Any,
    fmt: Optional[str, float] = None
)
```





---

<a href="../../excel/src/robocorp/excel/worksheet.py#L96"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `unhide_columns`

```python
unhide_columns(start_column, end_column) → None
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
