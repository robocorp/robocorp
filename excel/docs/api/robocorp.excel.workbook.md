<!-- markdownlint-disable -->

# module `robocorp.excel.workbook`

**Source:** [`workbook.py:0`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L0)

______________________________________________________________________

## class `Workbook`

**Source:** [`workbook.py:10`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L10)

Manager class for both .xls and .xlsx Excel files.

### method `__init__`

**Source:** [`workbook.py:13`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L13)

```python
__init__(excel: Union[XlsWorkbook, XlsxWorkbook])
```

______________________________________________________________________

### method `close`

**Source:** [`workbook.py:25`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L25)

```python
close()
```

______________________________________________________________________

### method `create_worksheet`

**Source:** [`workbook.py:40`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L40)

```python
create_worksheet(
    name: str,
    content: Optional[Any] = None,
    exist_ok: Optional[bool] = False,
    header: Optional[bool] = False
)
```

______________________________________________________________________

### method `list_worksheets`

**Source:** [`workbook.py:61`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L61)

```python
list_worksheets() → List[str]
```

______________________________________________________________________

### method `remove_worksheet`

**Source:** [`workbook.py:71`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L71)

```python
remove_worksheet(sheet: Union[str, int])
```

______________________________________________________________________

### method `save`

**Source:** [`workbook.py:17`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L17)

```python
save(name: Union[str, Path, BytesIO], overwrite=True)
```

______________________________________________________________________

### method `worksheet`

**Source:** [`workbook.py:30`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L30)

```python
worksheet(sheet: Union[str, int]) → Worksheet
```

If name is not provided take the first worksheet?

______________________________________________________________________

### method `worksheet_exists`

**Source:** [`workbook.py:64`](https://github.com/robocorp/robocorp/tree/master/excel/src/robocorp/excel/workbook.py#L64)

```python
worksheet_exists(sheet: Union[str, int]) → bool
```
