# robocorp-excel

This library provides a simple way to deal with both legacy `.xls` files
and newer `.xlsx` files directly. It can be used to read and edit them
directly without having Microsoft Excel installed.

> ⚠️ This library isn't included by default in `robocorp`. In order to use this, you
> have to make it available in your Python environment by listing
> ![`robocorp-excel`](https://img.shields.io/pypi/v/robocorp-excel?label=robocorp-excel)
> as a requirement in your dependencies configuration file:
> - _conda.yaml_ for an automation Task Package
> - _action-package.yaml_ for an automation Action Package
> - _requirements.txt_, _pyproject.toml_ etc. for the rest

> 👉 `robocorp-excel` is not yet production ready. 
> We work in semver and consider versions below 1.0.0 as development phase releases,
> you can use them but to get to v1 we need to get the feature support and testing to a
> level where we feel comfortable recommending production usage.

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

Information on specific functions or classes: [robocorp.excel](https://github.com/robocorp/robocorp/blob/master/excel/docs/api/robocorp.excel.md)

## Changelog

A list of releases and corresponding changes can be found in the
[changelog](https://github.com/robocorp/robocorp/blob/master/excel/docs/CHANGELOG.md).
