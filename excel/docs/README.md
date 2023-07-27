# robocorp-excel

This library provides a simple way to deal with both legacy `.xls` files
and newer `.xlsx` files directly. It can be used to read and edit them
directly without having Microsoft Excel installed.

## Getting started

```python
from robocorp import excel
from robocorp.tasks import task

@task
def inspect_workbook():
    workbook = excel.open_workbook("orders.xlsx")
    worksheet = workbook.worksheet("Sheet1")

    for row in worksheet.as_table(header=True):
    	print(row)
```

Further user guides and tutorials can be found in [Robocorp Docs](https://robocorp.com/docs).

## API Reference

Information on specific functions or classes: [robocorp.excel](https://github.com/robocorp/robo/blob/master/excel/docs/api/robocorp.excel.md)

## Changelog

A list of releases and corresponding changes can be found in the
[changelog](https://github.com/robocorp/robo/blob/master/excel/docs/CHANGELOG.md).
