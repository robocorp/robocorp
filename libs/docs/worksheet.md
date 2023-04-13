<!-- markdownlint-disable -->

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `worksheet`




**Global Variables**
---------------
- **TYPE_CHECKING**


---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L10"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Worksheet`
Common class for worksheets to manage the worksheet's content. 

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L13"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(workbook: 'Workbook', name: str)
```








---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

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

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L39"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `as_table`

```python
as_table(
    header: bool = False,
    trim: bool = True,
    start: Optional[int] = None
) → Table
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L64"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `auto_size_columns`

```python
auto_size_columns(start_column, end_column, width)
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L146"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `clear_cell_range`

```python
clear_cell_range()
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L142"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `copy_cell_values`

```python
copy_cell_values()
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L60"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_columns`

```python
delete_columns(start, end)
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L85"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `delete_rows`

```python
delete_rows(start, end) → None
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L89"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_empty_row`

```python
find_empty_row(name) → int
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L110"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_cell_value`

```python
get_cell_value()
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\.venv\lib\site-packages\typing_extensions.py#L114"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_value`

```python
get_value(row, column) → Any
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L68"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `hide_columns`

```python
hide_columns(start_column, end_column)
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L72"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert_columns_after`

```python
insert_columns_after(column, amount)
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L76"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert_columns_before`

```python
insert_columns_before(column, amount) → None
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L35"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert_image`

```python
insert_image()
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L93"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert_rows_after`

```python
insert_rows_after(row, amount) → None
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L97"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `insert_rows_before`

```python
insert_rows_before(row, amount) → None
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L102"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `move_range`

```python
move_range(range_string, rows, columns, translate) → None
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `read_worksheet`

```python
read_worksheet() → List[dict]
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `rename`

```python
rename()
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L134"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_cell_format`

```python
set_cell_format()
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L138"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_cell_formula`

```python
set_cell_formula()
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L120"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_cell_value`

```python
set_cell_value()
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L130"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_cell_values`

```python
set_cell_values()
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L106"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_styles`

```python
set_styles(args) → None
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\.venv\lib\site-packages\typing_extensions.py#L124"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `set_value`

```python
set_value()
```





---

<a href="https://github.com/robocorp/draft-python-framework/tree/master/libs\excel\src\robo\libs\excel\worksheet.py#L80"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `unhide_columns`

```python
unhide_columns(start_column, end_column) → None
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
