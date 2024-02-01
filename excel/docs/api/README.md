<!-- markdownlint-disable -->

# API Overview

## Modules

- [`robocorp.excel`](./robocorp.excel.md#module-robocorpexcel): Main module for doing Excel automation.
- [`robocorp.excel.excel`](./robocorp.excel.excel.md#module-robocorpexcelexcel)
- [`robocorp.excel.tables`](./robocorp.excel.tables.md#module-robocorpexceltables)
- [`robocorp.excel.workbook`](./robocorp.excel.workbook.md#module-robocorpexcelworkbook)
- [`robocorp.excel.worksheet`](./robocorp.excel.worksheet.md#module-robocorpexcelworksheet)

## Classes

- [`tables.Table`](./robocorp.excel.tables.md#class-table): Container class for tabular data.
- [`tables.Dialect`](./robocorp.excel.tables.md#class-dialect): CSV dialect.
- [`tables.Table`](./robocorp.excel.tables.md#class-table): Container class for tabular data.
- [`tables.Tables`](./robocorp.excel.tables.md#class-tables): `Tables` is a library for manipulating tabular data.
- [`workbook.Workbook`](./robocorp.excel.workbook.md#class-workbook): Manager class for both .xls and .xlsx Excel files.
- [`worksheet.Worksheet`](./robocorp.excel.worksheet.md#class-worksheet): Common class for worksheets to manage the worksheet's content.

## Functions

- [`excel.create_workbook`](./robocorp.excel.excel.md#function-create_workbook): Create and open a new Excel workbook in memory.
- [`excel.open_workbook`](./robocorp.excel.excel.md#function-open_workbook): Open an existing Excel workbook.
- [`excel.create_workbook`](./robocorp.excel.excel.md#function-create_workbook): Create and open a new Excel workbook in memory.
- [`excel.open_workbook`](./robocorp.excel.excel.md#function-open_workbook): Open an existing Excel workbook.
- [`tables.if_none`](./robocorp.excel.tables.md#function-if_none): Return default if value is None.
- [`tables.return_table_as_raw_list`](./robocorp.excel.tables.md#function-return_table_as_raw_list)
- [`tables.to_condition`](./robocorp.excel.tables.md#function-to_condition): Convert string operator into callable condition function.
- [`tables.to_identifier`](./robocorp.excel.tables.md#function-to_identifier): Convert string to valid identifier.
- [`tables.to_list`](./robocorp.excel.tables.md#function-to_list): Convert (possibly scalar) value to list of `size`.
- [`tables.uniq`](./robocorp.excel.tables.md#function-uniq): Return list of unique values while preserving order.
