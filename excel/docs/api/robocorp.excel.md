<!-- markdownlint-disable -->

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/__init__.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

# <kbd>module</kbd> `robocorp.excel`





---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/excel.py#L9"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `create_workbook`

```python
create_workbook(
    fmt: Literal['xlsx', 'xls'] = 'xlsx',
    sheet_name: Optional[str] = None
) → Workbook
```

Create and open a new Excel workbook in memory. 

Automatically also creates a new worksheet with the name ``sheet_name``. 

**Note:** Use the ``save`` method to store the workbook into file. 



**Args:**

 - <b>`fmt`</b>:  The file format for the workbook. Supported file formats: ``xlsx``, ``xls``. 
 - <b>`sheet_name`</b>:  The name for the initial sheet. If None, then set to ``Sheet``. 



**Returns:**

 - <b>`Workbook`</b>:  The created Excel workbook object. 



**Example:**
.. code-block:: python 

workbook = create_workbook("xlsx", sheet_name="Sheet1") 


---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/excel.py#L50"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>function</kbd> `open_workbook`

```python
open_workbook(
    path: Union[str, Path],
    data_only: bool = False,
    read_only: bool = False
) → Workbook
```

Open an existing Excel workbook. 

Opens the workbook in memory. The file can be in either ``.xlsx`` or ``.xls`` format. 



**Args:**

 - <b>`path`</b>:  path to Excel file 
 - <b>`data_only`</b>:  controls whether cells with formulas have either  the formula (default, False) or the value stored the last time Excel  read the sheet (True). Affects only ``.xlsx`` files. 



**Returns:**

 - <b>`Workbook`</b>:  Workbook object 



**Example:**


:
``` 

        # Open workbook with only path provided         workbook = open_workbook("path/to/file.xlsx") 

        # Open workbook with path provided and reading formulas in cells         # as the value stored         # Note: Can only be used with XLSX workbooks         workbook = open_workbook("path/to/file.xlsx", data_only=True) 


---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L122"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

## <kbd>class</kbd> `Table`
Container class for tabular data. 



**Note:**

>Supported data formats:
>- empty: None values populated according to columns/index- list: list of data Rows- dict: Dictionary of columns as keys and Rows as values- table: An existing Table
>Row: a namedtuple, dictionary, list or a tuple

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L137"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    data: Optional[Dict[Union[int, str], Union[Dict, List, Tuple, NamedTuple, set]], List[Union[Dict, List, Tuple, NamedTuple, set]], ForwardRef('Table')] = None,
    columns: Optional[List[str]] = None
)
```

Creates a Table object. 



**Args:**

 - <b>`data`</b>:      Values for table,  see ``Supported data formats`` 
 - <b>`columns`</b>:   Names for columns, should match data dimensions 


---

#### <kbd>property</kbd> columns





---

#### <kbd>property</kbd> data





---

#### <kbd>property</kbd> dimensions





---

#### <kbd>property</kbd> index





---

#### <kbd>property</kbd> size







---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L702"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `append_column`

```python
append_column(column=None, values=None)
```





---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L693"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `append_row`

```python
append_row(row=None)
```

Append new row to table. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L697"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `append_rows`

```python
append_rows(rows)
```

Append multiple rows to table. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L735"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `append_table`

```python
append_table(table)
```

Append data from table to current data. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L468"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `clear`

```python
clear()
```

Remove all rows from this table. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L384"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `column_location`

```python
column_location(value)
```

Find location for column value. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L464"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `copy`

```python
copy()
```

Create a copy of this table. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L720"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `delete_columns`

```python
delete_columns(columns)
```

Remove columns with matching names. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L708"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `delete_rows`

```python
delete_rows(indexes: Union[int, str, List[Union[int, str]]])
```

Remove rows with matching indexes. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L806"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `filter_all`

```python
filter_all(
    condition: Callable[[Union[int, str, Dict, List, Tuple, NamedTuple, set]], bool]
)
```

Remove rows by evaluating `condition` for every row. 

The filtering will be done in-place and all the rows evaluating as falsy through the provided condition will be removed. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L819"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `filter_by_column`

```python
filter_by_column(column: Union[int, str], condition: Callable[[Any], bool])
```

Remove rows by evaluating `condition` for cells in `column`. 

The filtering will be done in-place and all the rows where it evaluates to falsy are removed. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L482"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `get`

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

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L511"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `get_cell`

```python
get_cell(index, column)
```

Get single cell value. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L542"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `get_column`

```python
get_column(column, indexes=None, as_list=False)
```

Get row values from column. 



**Args:**

 - <b>`column`</b>:  Name for column 
 - <b>`indexes`</b>:  Row indexes to include, or all if not given 
 - <b>`as_list`</b>:  Return column as dictionary, instead of list 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L518"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `get_row`

```python
get_row(index: Union[int, str], columns=None, as_list=False)
```

Get column values from row. 



**Args:**

 - <b>`index`</b>:    Index for row. 
 - <b>`columns`</b>:  Column names to include, or all if not given. 
 - <b>`as_list`</b>:  Return row as list, instead of dictionary. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L585"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `get_slice`

```python
get_slice(start: Optional[int, str] = None, end: Optional[int, str] = None)
```

Get a new table from rows between start and end index. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L566"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `get_table`

```python
get_table(
    indexes=None,
    columns=None,
    as_list=False
) → Union[List, ForwardRef('Table')]
```

Get a new table from all cells matching indexes and columns. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L785"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `group_by_column`

```python
group_by_column(column)
```

Group rows by column value and return as list of tables. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L472"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `head`

```python
head(rows, as_list=False)
```

Return first n rows of table. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L367"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `index_location`

```python
index_location(value: Union[int, str]) → int
```





---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L840"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `iter_dicts`

```python
iter_dicts(
    with_index=True
) → Generator[Dict[Union[int, str], Any], NoneType, NoneType]
```

Iterate rows with values as dicts. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L832"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `iter_lists`

```python
iter_lists(with_index=True)
```

Iterate rows with values as lists. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L848"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `iter_tuples`

```python
iter_tuples(with_index=True, name='Row')
```

Iterate rows with values as namedtuples. 

Converts column names to valid Python identifiers, e.g. "First Name" -> "First_Name" 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L625"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `set`

```python
set(indexes=None, columns=None, values=None)
```

Sets multiple cell values at a time. 

Both ``indexes`` and ``columns`` can be scalar or list-like, which enables setting individual cells, rows/columns, or regions. 

If ``values`` is scalar, all matching cells will be set to that value. Otherwise, the length should match the cell count defined by the other parameters. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L649"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `set_cell`

```python
set_cell(index, column, value)
```

Set individual cell value. 

If either index or column is missing, they are created. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L678"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `set_column`

```python
set_column(column, values)
```

Set values in column. If column is missing, it is created. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L666"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `set_row`

```python
set_row(index, values)
```

Set values in row. If index is missing, it is created. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L747"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `sort_by_column`

```python
sort_by_column(columns, ascending=False)
```

Sort table by columns. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L477"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `tail`

```python
tail(rows, as_list=False)
```

Return last n rows of table. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L878"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `to_dict`

```python
to_dict(with_index=True)
```

Convert table to dict representation. 

---

<a href="https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/tables.py#L864"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square" /></a>

### <kbd>method</kbd> `to_list`

```python
to_list(with_index=True)
```

Convert table to list representation. 


