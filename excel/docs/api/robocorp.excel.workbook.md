<!-- markdownlint-disable -->

# module `robocorp.excel.workbook` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/workbook.py#L0)






---

## class `Workbook` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/workbook.py#L10)

Manager class for both .xls and .xlsx Excel files.

### method `__init__` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/workbook.py#L13)


```python
__init__(excel: Union[XlsWorkbook, XlsxWorkbook])
```







---

### method `close` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/workbook.py#L25)


```python
close()
```




---

### method `create_worksheet` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/workbook.py#L40)


```python
create_worksheet(
    name: str,
    content: Optional[Any] = None,
    exist_ok: Optional[bool] = False,
    header: Optional[bool] = False
)
```




---

### method `list_worksheets` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/workbook.py#L61)


```python
list_worksheets() → List[str]
```




---

### method `remove_worksheet` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/workbook.py#L71)


```python
remove_worksheet(sheet: Union[str, int])
```




---

### method `save` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/workbook.py#L17)


```python
save(name: Union[str, Path, BytesIO], overwrite=True)
```




---

### method `worksheet` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/workbook.py#L30)


```python
worksheet(sheet: Union[str, int]) → Worksheet
```

If name is not provided take the first worksheet?

---

### method `worksheet_exists` [![Source](https://img.shields.io/badge/-source-cccccc?style=flat-square)](https://github.com/robocorp/robo/tree/master/excel/src/robocorp/excel/workbook.py#L64)


```python
worksheet_exists(sheet: Union[str, int]) → bool
```





