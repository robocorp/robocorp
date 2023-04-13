<!-- markdownlint-disable -->

# API Overview

## Modules

- [`excel`](./excel.md#module-excel)
- [`tables`](./tables.md#module-tables)
- [`workbook`](./workbook.md#module-workbook)
- [`worksheet`](./worksheet.md#module-worksheet)
- [`browser`](./browser.md#module-browser)

## Classes

- [`tables.Dialect`](./tables.md#class-dialect): CSV dialect.
- [`tables.Table`](./tables.md#class-table): Container class for tabular data.
- [`tables.Tables`](./tables.md#class-tables): ``Tables`` is a library for manipulating tabular data.
- [`workbook.Workbook`](./workbook.md#class-workbook): Manager class for both .xls and .xlsx Excel files.
- [`worksheet.Worksheet`](./worksheet.md#class-worksheet): Common class for worksheets to manage the worksheet's content.

## Functions

- [`excel.create_workbook`](./excel.md#function-create_workbook): Create and open a new Excel workbook in memory.
- [`excel.open_workbook`](./excel.md#function-open_workbook): Open an existing Excel workbook.
- [`tables.if_none`](./tables.md#function-if_none): Return default if value is None.
- [`tables.return_table_as_raw_list`](./tables.md#function-return_table_as_raw_list)
- [`tables.to_condition`](./tables.md#function-to_condition): Convert string operator into callable condition function.
- [`tables.to_identifier`](./tables.md#function-to_identifier): Convert string to valid identifier.
- [`tables.to_list`](./tables.md#function-to_list): Convert (possibly scalar) value to list of `size`.
- [`tables.uniq`](./tables.md#function-uniq): Return list of unique values while preserving order.
- [`browser.open_browser`](./browser.md#function-open_browser): Launches a Playwright browser instance.
- [`browser.open_url`](./browser.md#function-open_url): Launches a Playwright browser instance and opens the given URL.


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
