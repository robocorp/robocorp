# robocorp-excel

This library provides a simple way to deal with both legacy `.xls` files and newer `.xlsx` files directly. It can be used to read and edit them directly without having Microsoft Excel installed.

## Usage

[![`robocorp-excel`](https://img.shields.io/pypi/v/robocorp-excel?label=robocorp-excel)](https://pypi.org/project/robocorp-excel/)

> 👉 Check that you have added the dependency in your configuration; this library is not part of the [**robocorp**](https://pypi.org/project/robocorp/) bundle.
> - _conda.yaml_ for automation [Task Packages](https://robocorp.com/docs/robot-structure)
> - _package.yaml_ for automation Action Packages
> - _requirements.txt_, _pyproject.toml_, _setup.py|cfg_ etc. for the rest

> ⚠ `robocorp-excel` is not yet production ready.  
> We work in SemVer, so consider versions below `1.0.0` as development phase releases. You can use them, but to get to **v1**, we need to get the feature support and testing to a level where we feel comfortable recommending this library for production usage.

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

## Guides

Further user guides and tutorials can be found in [Robocorp Docs](https://robocorp.com/docs).

## API Reference

Explore our [API](https://github.com/robocorp/robocorp/blob/master/excel/docs/api/README.md) for extensive documentation.

## Changelog

A list of releases and corresponding changes can be found in the [changelog](https://github.com/robocorp/robocorp/blob/master/excel/docs/CHANGELOG.md).
