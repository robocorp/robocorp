<!-- markdownlint-disable -->

# module `robocorp.excel.tables`

**Source:** [`tables.py:0`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L0)

______________________________________________________________________

## function `return_table_as_raw_list`

**Source:** [`tables.py:35`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L35)

```python
return_table_as_raw_list(table, heading=False)
```

______________________________________________________________________

## function `to_list`

**Source:** [`tables.py:47`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L47)

```python
to_list(obj: Any, size: int = 1)
```

Convert (possibly scalar) value to list of `size`.

______________________________________________________________________

## function `to_identifier`

**Source:** [`tables.py:55`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L55)

```python
to_identifier(val: Any)
```

Convert string to valid identifier.

______________________________________________________________________

## function `to_condition`

**Source:** [`tables.py:71`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L71)

```python
to_condition(operator: str, value: Any) → Callable[[Any], bool]
```

Convert string operator into callable condition function.

______________________________________________________________________

## function `if_none`

**Source:** [`tables.py:95`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L95)

```python
if_none(value: Any, default: Any)
```

Return default if value is None.

______________________________________________________________________

## function `uniq`

**Source:** [`tables.py:100`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L100)

```python
uniq(seq: Iterable)
```

Return list of unique values while preserving order.

Values must be hashable.

______________________________________________________________________

## enum `Dialect`

**Source:** [`tables.py:114`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L114)

CSV dialect.

### Values

- **Excel** = excel
- **ExcelTab** = excel-tab
- **Unix** = unix

______________________________________________________________________

## class `Table`

**Source:** [`tables.py:122`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L122)

Container class for tabular data.

**Note:**

> Supported data formats:
>
> - empty: None values populated according to columns/index - list: list of data Rows - dict: Dictionary of columns as keys and Rows as values - table: An existing Table
>   Row: a namedtuple, dictionary, list or a tuple

### method `__init__`

**Source:** [`tables.py:137`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L137)

```python
__init__(
    data: Optional[Dict[Union[int, str], Union[Dict, List, Tuple, NamedTuple, set]], List[Union[Dict, List, Tuple, NamedTuple, set]], ForwardRef('Table')] = None,
    columns: Optional[List[str]] = None
)
```

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

______________________________________________________________________

## class `Tables`

**Source:** [`tables.py:896`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L896)

`Tables` is a library for manipulating tabular data.

It can import data from various sources and apply different operations to it. Common use-cases are reading and writing CSV files, inspecting files in directories, or running tasks using existing Excel data.

**Import types**

The data a table can be created from can be of two main types:

1. An iterable of individual rows, like a list of lists, or list of dictionaries 2. A dictionary of columns, where each dictionary value is a list of values

For instance, these two input values:

.. code-block:: python

data1 = \[{"name": "Mark", "age": 58},{"name": "John", "age": 22},{"name": "Adam", "age": 67},\]

data2 = {"name": \["Mark", "John", "Adam"\],"age":  \[    58,     22,     67\],}

Would both result in the following table:

+-------+------+-----+ | Index | Name | Age | +=======+======+=====+ | 0     | Mark | 58  | +-------+------+-----+ | 1     | John | 22  | +-------+------+-----+ | 2     | Adam | 67  | +-------+------+-----+

**Indexing columns and rows**

Columns can be referred to in two ways: either with a unique string name or their position as an integer. Columns can be named either when the table is created, or they can be (re)named dynamically with keywords. The integer position can always be used, and it starts from zero.

For instance, a table with columns "Name", "Age", and "Address" would allow referring to the "Age" column with either the name "Age" or the number 1.

Rows do not have a name, but instead only have an integer index. This index also starts from zero. Keywords where rows are indexed also support negative values, which start counting backwards from the end.

For instance, in a table with five rows, the first row could be referred to with the number 0. The last row could be accessed with either 4 or
-1.

**Examples:**
The `Tables` library can load tabular data from various other librariesand manipulate it.

.. code-block:: python

from robocorp.excel.tables import Tables

tables = Tables()orders = tables.read_table_from_csv("orders.csv", columns=\["name", "mail", "product"\])

customers = tables.group_table_by_column(rows, "mail")for customer in customers:for order in customer:add_cart(order)make_order()

### method `__init__`

**Source:** [`tables.py:977`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L977)

```python
__init__()
```

______________________________________________________________________

### method `add_table_column`

**Source:** [`tables.py:1250`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1250)

```python
add_table_column(table: Table, name: Optional[str] = None, values: Any = None)
```

Append a column to a table.

**Args:**

- <b>`table`</b>:    Table to modify
- <b>`name`</b>:     Name of new column
- <b>`values`</b>:   Value(s) for new column

The `values` can either be a list of values, one for each row, or one single value that is set for all rows.

**Examples:**
.. code-block:: robotframework

# Add empty columnAdd table column    ${table}

# Add empty column with nameAdd table column    ${table}    name=Home Address

# Add new column where every every row has the same valueAdd table column    ${table}    name=TOS    values=${FALSE}

# Add new column where every row has a unique value${is_first}=    Create list    ${TRUE}    ${FALSE}    ${FALSE}Add table column    ${table}    name=IsFirst    values=${is_first}

______________________________________________________________________

### method `add_table_row`

**Source:** [`tables.py:1283`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1283)

```python
add_table_row(table: Table, values: Any = None)
```

Append rows to a table.

**Args:**

- <b>`table`</b>:    Table to modify
- <b>`values`</b>:   Value(s) for new row

The `values` can either be a list of values, or a dictionary where the keys match current column names. Values for unknown keys are discarded.

It can also be a single value that is set for all columns, which is `None` by default.

**Examples:**
.. code-block:: robotframework

# Add empty rowAdd table row    ${table}

# Add row where every column has the same valueAdd table row    ${table}    Unknown

# Add values per column${values}=    Create dictionary    Username=Mark    Mail=mark@robocorp.comAdd table row    ${table}    ${values}

______________________________________________________________________

### method `clear_table`

**Source:** [`tables.py:1080`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1080)

```python
clear_table(table: Table)
```

Clear table in-place, but keep columns.

**Args:**

- <b>`table`</b>:    Table to clear

**Example:**
.. code-block:: python from robocorp.excel.tables import Tables

tables = Tables()tables.clear_table(table)

______________________________________________________________________

### method `copy_table`

**Source:** [`tables.py:1067`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1067)

```python
copy_table(table: Table) → Table
```

Make a copy of a table object.

**Args:**

- <b>`table`</b>:   Table to copy

**Returns:**

- <b>`Table`</b>:   Table object

______________________________________________________________________

### method `create_table`

**Source:** [`tables.py:985`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L985)

```python
create_table(
    data: Optional[Dict[Union[int, str], Union[Dict, List, Tuple, NamedTuple, set]], List[Union[Dict, List, Tuple, NamedTuple, set]], ForwardRef('Table')] = None,
    trim: bool = False,
    columns: List[str] = None
) → Table
```

Create Table object from data.

Data can be a combination of various iterable containers, e.g. list of lists, list of dicts, dict of lists.

**Args:**

- <b>`data`</b>:     Source data for table
- <b>`trim`</b>:     Remove all empty rows from the end of the worksheet, default `False`
- <b>`columns`</b>:  Names of columns (optional)

**Returns:**

- <b>`Table`</b>:   Table object

See the main documentation for more information about supported data types.

**Example:**
.. code-block:: python

# Create a new table using a Dictionary of Lists# Because of the dictionary keys the column names will be automatically setfrom robocorp.excel.tables import Tables

tables = Tables()

table_data_name = \["Mark", "John", "Amy"\]table_data_age = \[58, 22, 67\]table_data = { name: table_data_name, age: table_data_age }table = tables.create_table(table_data)

______________________________________________________________________

### method `export_table`

**Source:** [`tables.py:1031`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1031)

```python
export_table(
    table: Table,
    with_index: bool = False,
    as_list: bool = True
) → Union[List, Dict]
```

Convert a table object into standard Python containers.

**Args:**

- <b>`table`</b>:        Table to convert to dict
- <b>`with_index`</b>:   Include index in values
- <b>`as_list`</b>:      Export data as list instead of dict

Returns

- <b>`(Union[list, dict])`</b>:  A List or Dictionary that represents the table

**Example:**
.. code-block:: python

from robocorp.excel.tables import Tables

tables = Tables()

table_data_name = \["Mark", "John", "Amy"\]table_data_age = \[58, 22, 67\]table_data = { name: table_data_name, age: table_data_age }table = tables.create_table(table_data)

# manipulate the table..

export = tables.export_table(table)

______________________________________________________________________

### method `filter_empty_rows`

**Source:** [`tables.py:1840`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1840)

```python
filter_empty_rows(table: Table)
```

Remove all rows from a table which have only `None` values.

**Args:**

- <b>`table`</b>:    Table to filter

The filtering will be done in-place.

**Example:**
.. code-block:: robotframework

Filter empty rows    ${table}

______________________________________________________________________

### method `filter_table_by_column`

**Source:** [`tables.py:1741`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1741)

```python
filter_table_by_column(
    table: Table,
    column: Union[int, str],
    operator: str,
    value: Any
)
```

Remove all rows where column values don't match the given condition.

**Args:**

- <b>`table`</b>:      Table to filter
- <b>`column`</b>:     Column to filter with
- <b>`operator`</b>:   Filtering operator, e.g. >, \<, ==, contains
- <b>`value`</b>:      Value to compare column to (using operator)

See the keyword `Find table rows` for all supported operators and their descriptions.

The filtering will be done in-place.

**Examples:**
.. code-block:: robotframework

# Only accept prices that are non-zeroFilter table by column    ${table}   price  !=  ${0}

# Remove uwnanted product types@{types}=    Create list    Unknown    RemovedFilter table by column    ${table}   product_type  not in  ${types}

______________________________________________________________________

### method `filter_table_with_function`

**Source:** [`tables.py:1778`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1778)

```python
filter_table_with_function(table: Table, func: Callable, *args)
```

Filters the table rows with the given func.

Run a function for each row of a table, then remove all rows where the called keyword returns a falsy value.

Can be used to create custom RF keyword based filters.

**Args:**

- <b>`table`</b>:  Table to modify.
- <b>`func`</b>:  Function used as filter.
- <b>`args`</b>:  Additional keyword arguments to be passed. (optional)

The row object will be given as the first argument to the filtering keyword.

______________________________________________________________________

### method `find_table_rows`

**Source:** [`tables.py:1632`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1632)

```python
find_table_rows(
    table: Table,
    column: Union[int, str],
    operator: str,
    value: Any
) → Table
```

Find all the rows in a table which match a condition for a given column.

**Args:**

- <b>`table`</b>:  Table to search into.
- <b>`column`</b>:  Name or position of the column to compare with.
- <b>`operator`</b>:  Comparison operator used with every cell value on thespecified column.
- <b>`value`</b>:  Value to compare against.

**Returns:**

- <b>`Table`</b>:  New `Table` object containing all the rows matching the condition.

Supported operators:

============ ======================================== Operator     Description ============ ======================================== >            Cell value is larger than \<            Cell value is smaller than >=           Cell value is larger or equal than \<=           Cell value is smaller or equal than ==           Cell value is equal to !=           Cell value is not equal to is           Cell value is the same object not is       Cell value is not the same object contains     Cell value contains given value not contains Cell value does not contain given value in           Cell value is in given value not in       Cell value is not in given value ============ ========================================

Returns the matches as a new `Table` instance.

**Examples:**
.. code-block:: robotframework

# Find all rows where price is over 200@{rows} =    Find table rows    ${table}    Price  >  ${200}

# Find all rows where the status does not contain "removed"@{rows} =    Find table rows    ${table}    Status  not contains  removed

______________________________________________________________________

### method `get_table_cell`

**Source:** [`tables.py:1574`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1574)

```python
get_table_cell(
    table: Table,
    row: Union[int, str],
    column: Union[int, str]
) → Any
```

Get a cell value from a table.

**Args:**

- <b>`table`</b>:    Table to read from
- <b>`row`</b>:      Row of cell
- <b>`column`</b>:   Column of cell

**Returns:**

- <b>`(Any)`</b>:  Cell value

**Examples:**
.. code-block:: robotframework

# Get the value in the first row and first columnGet table cell    ${table}    0    0

# Get the value in the last row and first columnGet table cell    ${table}   -1    0

# Get the value in the last row and last columnGet table cell    ${table}   -1    -1

# Get the value in the third row and column "Name"Get table cell    ${table}    2    Name

______________________________________________________________________

### method `get_table_column`

**Source:** [`tables.py:1341`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1341)

```python
get_table_column(table: Table, column: Union[int, str]) → List
```

Get all values for a single column in a table.

**Args:**

- <b>`table`</b>:    Table to read
- <b>`column`</b>:   Column to read

**Returns:**

- <b>`list`</b>:  List of the rows in the selected column

**Example:**
.. code-block:: robotframework

${emails}=    Get table column    ${users}    E-Mail Address

______________________________________________________________________

### method `get_table_dimensions`

**Source:** [`tables.py:1186`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1186)

```python
get_table_dimensions(table: Table) → Tuple[int, int]
```

Return table dimensions, as (rows, columns).

**Args:**

- <b>`table`</b>:     Table to inspect

**Returns:**

- <b>`(Tuple[int, int])`</b>:  Two integer values that represent the number of rows and columns

**Example:**
.. code-block:: robotframework

${rows}  ${columns}=    Get table dimensions    ${table}Log    Table has ${rows} rows and ${columns} columns.

______________________________________________________________________

### method `get_table_row`

**Source:** [`tables.py:1314`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1314)

```python
get_table_row(
    table: Table,
    row: Union[int, str],
    as_list: bool = False
) → Union[Dict, List]
```

Get a single row from a table.

**Args:**

- <b>`table`</b>:    Table to read
- <b>`:param row`</b>:      Row to read
- <b>`:param as_list`</b>:  Return list instead of dictionary

**Returns:**

- <b>`(Union[dict, list])`</b>:  Dictionary or List of table row

**Example:**
.. code-block:: robotframework

# returns the first row in the table${first}=    Get table row    ${orders}

# returns the last row in the table${last}=      Get table row    ${orders}    -1    as_list=${TRUE}

______________________________________________________________________

### method `get_table_slice`

**Source:** [`tables.py:1480`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1480)

```python
get_table_slice(
    table: Table,
    start: Optional[int, str] = None,
    end: Optional[int, str] = None
) → Union[Table, List[List]]
```

Return a new Table from a range of given Table rows.

**Args:**

- <b>`table`</b>:    Table to read from
- <b>`start`</b>:    Start index (inclusive)
- <b>`start`</b>:    End index (exclusive)

**Returns:**

- <b>`(Union[Table, list[list]])`</b>:  Table object of the selected rows

If `start` is not defined, starts from the first row. If `end` is not defined, stops at the last row.

**Examples:**
.. code-block:: robotframework

# Get all rows except first five${slice}=    Get table slice    ${table}    start=5

# Get rows at indexes 5, 6, 7, 8, and 9${slice}=    Get table slice    ${table}    start=5    end=10

# Get all rows except last five${slice}=    Get table slice    ${table}    end=-5

______________________________________________________________________

### method `group_table_by_column`

**Source:** [`tables.py:1713`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1713)

```python
group_table_by_column(table: Table, column: Union[int, str]) → List[Table]
```

Group a table by `column` and return a list of grouped Tables.

**Args:**

- <b>`table`</b>:    Table to use for grouping
- <b>`column`</b>:   Column which is used as grouping criteria

**Returns:**

- <b>`(List[Table])`</b>:  List of Table objects

**Example:**
.. code-block:: robotframework

# Groups rows of matching customers from the `customer` column# and returns the groups or rows as Tables@{groups}=    Group table by column    ${orders}    customer# An example of how to use the List of Tables once returnedFOR    ${group}    IN    @{groups}# Process all orders for the customer at onceProcess order    ${group}END

______________________________________________________________________

### method `map_column_values`

**Source:** [`tables.py:1804`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1804)

```python
map_column_values(table: Table, column: Union[int, str], func: Callable, *args)
```

Maps given function to column values.

Run a function for each cell in a given column, and replace its content with the return value.

Can be used to easily convert column types or values in-place.

**Args:**

- <b>`table`</b>:  Table to modify.
- <b>`column`</b>:  Column to modify.
- <b>`func`</b>:  Mapping function.
- <b>`args`</b>:  Additional keyword arguments. (optional)

The cell value will be given as the first argument to the mapping keyword.

**Examples:**
.. code-block:: robotframework

# Convert all columns values to a different typeMap column values    ${table}    Price    Convert to integer

# Look up values with a custom keywordMap column values    ${table}    User     Map user ID to name

______________________________________________________________________

### method `merge_tables`

**Source:** [`tables.py:1097`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1097)

```python
merge_tables(*tables: Table, index: Optional[str] = None) → Table
```

Create a union of two tables and their contents.

**Args:**

- <b>`tables`</b>:  Tables to merge
- <b>`index`</b>:   Column name to use as index for merge

**Returns:**

- <b>`Table`</b>:  Table object

By default, rows from all tables are appended one after the other. Optionally a column name can be given with `index`, which is used to merge rows together.

**Example:**
For instance, a `name` column could be used to identifyunique rows and the merge operation should overwrite valuesinstead of appending multiple copies of the same name.

====== =====Name   Price====== =====Egg    10.0Cheese 15.0Ham    20.0====== =====

====== =====Name   Stock====== =====Egg    12.0Cheese 99.0Ham    0.0====== =====

.. code-block:: python from robocorp.excel.tables import Tables

tables = Tables()

products = tables.merge_tables(prices, stock, index="Name")for product in products:print(f'Product: {product\["Name"\]}, Product: {product\["Price"\]}'

______________________________________________________________________

### method `pop_table_column`

**Source:** [`tables.py:1448`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1448)

```python
pop_table_column(
    table: Table,
    column: Optional[int, str] = None
) → Union[Dict, List]
```

Remove column from table and return it.

**Args:**

- <b>`table`</b>:    Table to modify
- <b>`column`</b>:   Column to remove

**Returns:**

- <b>`(Union[dict, list])`</b>:  Dictionary or List of the removed, popped, column

**Examples:**
.. code-block:: robotframework

# Remove column from table and discard itPop table column    ${users}   userId

# Remove column from table and iterate over it${ids}=    Pop table column    ${users}    userIdFOR    ${id}    IN    @{ids}Log    User id: ${id}END

______________________________________________________________________

### method `pop_table_row`

**Source:** [`tables.py:1418`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1418)

```python
pop_table_row(
    table: Table,
    row: Optional[int, str] = None,
    as_list: bool = False
) → Union[Dict, List]
```

Remove row from table and return it.

**Args:**

- <b>`table`</b>:    Table to modify
- <b>`row`</b>:      Row index, pops first row if none given
- <b>`as_list`</b>:  Return list instead of dictionary

**Returns:**

- <b>`(Union[dict, list])`</b>:  Dictionary or List of the removed, popped, row

**Examples:**
.. code-block:: robotframework

# Pop the firt row in the table and discard itPop table row    ${orders}

# Pop the last row in the table and store it${row}=      Pop table row    ${data}    -1    as_list=${TRUE}

______________________________________________________________________

### method `read_table_from_csv`

**Source:** [`tables.py:1912`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1912)

```python
read_table_from_csv(
    path: str,
    header: Optional[bool] = None,
    columns: Optional[List[str]] = None,
    dialect: Optional[str, Dialect] = None,
    delimiters: Optional[str] = None,
    column_unknown: str = 'Unknown',
    encoding: Optional[str] = None
) → Table
```

Read a CSV file as a table.

**Args:**

- <b>`path`</b>:             Path to CSV file
- <b>`header`</b>:           CSV file includes header
- <b>`columns`</b>:          Names of columns in resulting table
- <b>`dialect`</b>:          Format of CSV file
- <b>`delimiters`</b>:       String of possible delimiters
- <b>`column_unknown`</b>:   Column name for unknown fields
- <b>`encoding`</b>:         Text encoding for input file, uses system encoding by default

**Returns:**

- <b>`Table`</b>:  Table object

By default, attempts to deduce the CSV format and headers from a sample of the input file. If it's unable to determine the format automatically, the dialect and header will have to be defined manually.

Builtin `dialect` values are `excel`, `excel-tab`, and `unix`, and `header` is boolean argument (`True`/`False`). Optionally a set of valid `delimiters` can be given as a string.

The `columns` argument can be used to override the names of columns in the resulting table. The amount of columns must match the input data.

If the source data has a header and rows have more fields than the header defines, the remaining values are put into the column given by `column_unknown`. By default, it has the value "Unknown".

**Examples:**
.. code-block:: robotframework

# Source dialect is deduced automatically${table}=    Read table from CSV    export.csvLog   Found columns: ${table.columns}

# Source dialect is known and given explicitly${table}=    Read table from CSV    export-excel.csv    dialect=excelLog   Found columns: ${table.columns}

______________________________________________________________________

### method `rename_table_columns`

**Source:** [`tables.py:1205`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1205)

```python
rename_table_columns(
    table: Table,
    names: List[Optional[str]],
    strict: bool = False
)
```

Renames columns in the Table with given values.

Columns with name as `None` will use the previous value.

**Args:**

- <b>`table`</b>:    Table to modify
- <b>`names`</b>:    List of new column names
- <b>`strict`</b>:   If True, raises ValueError if column lengths do not match

The renaming will be done in-place.

**Examples:**
.. code-block:: robotframework

# Initially set the column names${columns}=    Create list   First  Second  ThirdRename table columns    ${table}    ${columns}# First, Second, Third

# Update the first and second column names to Uno and Dos${columns}=    Create list   Uno  DosRename table columns    ${table}    ${columns}# Uno, Dos, Third

______________________________________________________________________

### method `set_row_as_column_names`

**Source:** [`tables.py:1512`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1512)

```python
set_row_as_column_names(table: Table, row: Union[int, str])
```

Set existing row as names for columns.

**Args:**

- <b>`table`</b>:  Table to modify
- <b>`row`</b>:    Row to use as column names

**Example:**
.. code-block:: robotframework

# Set the column names based on the first rowSet row as column names    ${table}    0

______________________________________________________________________

### method `set_table_cell`

**Source:** [`tables.py:1604`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1604)

```python
set_table_cell(
    table: Table,
    row: Union[int, str],
    column: Union[int, str],
    value: Any
)
```

Set a cell value in a table.

**Args:**

- <b>`table`</b>:    Table to modify to
- <b>`row`</b>:      Row of cell
- <b>`column`</b>:   Column of cell
- <b>`value`</b>:    Value to set

**Examples:**
.. code-block:: robotframework

# Set the value in the first row and first column to "First"Set table cell    ${table}    0    0       First

# Set the value in the last row and first column to "Last"Set table cell    ${table}   -1    0       Last

# Set the value in the last row and last column to "Corner"Set table cell    ${table}   -1    -1       Corner

# Set the value in the third row and column "Name" to "Unknown"Set table cell    ${table}    2    Name    Unknown

______________________________________________________________________

### method `set_table_column`

**Source:** [`tables.py:1393`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1393)

```python
set_table_column(table: Table, column: Union[int, str], values: Any)
```

Assign values to a column in the table.

**Args:**

- <b>`table`</b>:    Table to modify
- <b>`column`</b>:   Column to modify
- <b>`values`</b>:   Value(s) to set

The `values` can either be a list of values, one for each row, or one single value that is set for all rows.

**Examples:**
.. code-block:: robotframework

# Set different value for each row (sizes must match)${ids}=    Create list    1  2  3  4  5Set table column    ${users}    userId    ${ids}

# Set the same value for all rowsSet table column    ${users}    email     ${NONE}

______________________________________________________________________

### method `set_table_row`

**Source:** [`tables.py:1361`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1361)

```python
set_table_row(table: Table, row: Union[int, str], values: Any)
```

Assign values to a row in the table.

**Args:**

- <b>`table`</b>:    Table to modify
- <b>`row`</b>:      Row to modify
- <b>`values`</b>:   Value(s) to set

The `values` can either be a list of values, or a dictionary where the keys match current column names. Values for unknown keys are discarded.

It can also be a single value that is set for all columns.

**Examples:**
.. code-block:: robotframework

${columns}=  Create list     One  Two  Three${table}=    Create table    columns=${columns}

${values}=   Create list     1  2  3Set table row    ${table}    0    ${values}

${values}=   Create dictionary    One=1  Two=2  Three=3Set table row    ${table}    1    ${values}

Set table row    ${table}    2    ${NONE}

______________________________________________________________________

### method `sort_table_by_column`

**Source:** [`tables.py:1690`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1690)

```python
sort_table_by_column(
    table: Table,
    column: Union[int, str],
    ascending: bool = True
)
```

Sort a table in-place according to `column`.

**Args:**

- <b>`table`</b>:        Table to sort
- <b>`column`</b>:       Column to sort with
- <b>`ascending`</b>:    Table sort order

**Examples:**
.. code-block:: robotframework

# Sorts the `order_date` column ascendingSort table by column    ${orders}    order_date

# Sorts the `order_date` column descendingSort table by column    ${orders}    order_date    ascending=${FALSE}

______________________________________________________________________

### method `table_head`

**Source:** [`tables.py:1529`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1529)

```python
table_head(
    table: Table,
    count: int = 5,
    as_list: bool = False
) → Union[Table, List[List]]
```

Return first `count` rows from a table.

**Args:**

- <b>`table`</b>:    Table to read from
- <b>`count`</b>:    Number of lines to read
- <b>`as_list`</b>:  Return list instead of Table

**Returns:**

- <b>`(Union[Table, List[List]])`</b>:  Return Table object or List of the selected rows

**Example:**
.. code-block:: robotframework

# Get the first 10 employees${first}=    Table head    ${employees}    10

______________________________________________________________________

### method `table_tail`

**Source:** [`tables.py:1551`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1551)

```python
table_tail(
    table: Table,
    count: int = 5,
    as_list: bool = False
) → Union[Table, List[List]]
```

Return last `count` rows from a table.

**Args:**

- <b>`table`</b>:    Table to read from
- <b>`count`</b>:    Number of lines to read
- <b>`as_list`</b>:  Return list instead of Table

**Returns:**

- <b>`(Union[Table, List[List]])`</b>:  Return Table object or List of the selected rows

**Example:**
.. code-block:: robotframework

# Get the last 10 orders${latest}=    Table tail    ${orders}    10

______________________________________________________________________

### method `trim_column_names`

**Source:** [`tables.py:1888`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1888)

```python
trim_column_names(table: Table)
```

Remove all extraneous whitespace from column names.

**Args:**

- <b>`table`</b>:     Table to filter

The filtering will be done in-place.

**Example:**
.. code-block:: robotframework

# This example will take colums such as:# "One", "Two ", "  Three "# and trim them to become the below:# "One", "Two", "Three"Trim column names     ${table}

______________________________________________________________________

### method `trim_empty_rows`

**Source:** [`tables.py:1863`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1863)

```python
trim_empty_rows(table: Table)
```

Remove all rows from the *end* of a table, which have only `None` as values.

**Args:**

- <b>`table`</b>:     Table to filter

The filtering will be done in-place.

**Example:**
.. code-block:: robotframework

Trim empty rows    ${table}

______________________________________________________________________

### method `write_table_to_csv`

**Source:** [`tables.py:1999`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/tables.py#L1999)

```python
write_table_to_csv(
    table: Table,
    path: str,
    header: bool = True,
    dialect: Union[str, Dialect] = <Dialect.Excel: 'excel'>,
    encoding: Optional[str] = None,
    delimiter: Optional[str] = ','
)
```

Write a table as a CSV file.

**Args:**

- <b>`table`</b>:     Table to write
- <b>`path`</b>:      Path to write to
- <b>`header`</b>:    Write columns as header to CSV file
- <b>`dialect`</b>:   The format of output CSV
- <b>`encoding`</b>:  Text encoding for output file, uses system encoding by default
- <b>`delimiter`</b>:  Delimiter character between columns

Builtin `dialect` values are `excel`, `excel-tab`, and `unix`.

**Example:**
.. code-block:: robotframework

${sheet}=    Read worksheet as table    orders.xlsx    header=${TRUE}Write table to CSV    ${sheet}    output.csv
