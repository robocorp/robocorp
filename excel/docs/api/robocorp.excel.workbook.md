<!-- markdownlint-disable -->

# module `robocorp.excel.workbook`

# Functions

______________________________________________________________________

# Class `Workbook`

Manager class for both .xls and .xlsx Excel files.

### `__init__`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L13)

```python
__init__(excel: Union[XlsWorkbook, XlsxWorkbook])
```

## Methods

______________________________________________________________________

### `close`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L25)

```python
close()
```

______________________________________________________________________

### `create_worksheet`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L40)

```python
create_worksheet(
    name: str,
    content: Optional[Any] = None,
    exist_ok: Optional[bool] = False,
    header: Optional[bool] = False
)
```

______________________________________________________________________

### `list_worksheets`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L61)

```python
list_worksheets() → List[str]
```

______________________________________________________________________

### `remove_worksheet`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L71)

```python
remove_worksheet(sheet: Union[str, int])
```

______________________________________________________________________

### `save`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L17)

```python
save(name: Union[str, Path, BytesIO], overwrite=True)
```

______________________________________________________________________

### `worksheet`

If name is not provided take the first worksheet?

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L30)

```python
worksheet(sheet: Union[str, int]) → Worksheet
```

______________________________________________________________________

### `worksheet_exists`

[**Link to source**](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L64)

```python
worksheet_exists(sheet: Union[str, int]) → bool
```
