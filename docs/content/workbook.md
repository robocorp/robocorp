<!-- markdownlint-disable -->

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\excel\src\robo\libs\excel\workbook.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `workbook`






---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\excel\src\robo\libs\excel\workbook.py#L8"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Workbook`
Manager class for both .xls and .xlsx Excel files. 

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\excel\src\robo\libs\excel\workbook.py#L11"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(excel: Union[XlsWorkbook, XlsxWorkbook])
```








---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\excel\src\robo\libs\excel\workbook.py#L19"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `close`

```python
close()
```





---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\excel\src\robo\libs\excel\workbook.py#L34"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `create_worksheet`

```python
create_worksheet(
    name: str,
    content: Optional[Any] = None,
    exist_ok: Optional[bool] = False,
    header: Optional[bool] = False
)
```





---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\excel\src\robo\libs\excel\workbook.py#L52"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `list_worksheets`

```python
list_worksheets() → List[str]
```





---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\excel\src\robo\libs\excel\workbook.py#L62"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `remove_worksheet`

```python
remove_worksheet(sheet: Union[str, int])
```





---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\excel\src\robo\libs\excel\workbook.py#L15"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `save`

```python
save(name: Union[str, Path])
```





---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\excel\src\robo\libs\excel\workbook.py#L24"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `worksheet`

```python
worksheet(sheet: Union[str, int]) → Worksheet
```

If name is not provided take the first worksheet? 

---

<a href="https://github.com/robocorp/draft-python-framework/blob/master/libs\excel\src\robo\libs\excel\workbook.py#L55"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `worksheet_exists`

```python
worksheet_exists(sheet: Union[str, int]) → bool
```








---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
