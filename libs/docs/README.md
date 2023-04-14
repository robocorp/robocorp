<!-- markdownlint-disable -->

# API Overview

## Modules

- [`browser`](./browser.md#module-browser)
- [`excel`](./excel.md#module-excel)
- [`tables`](./tables.md#module-tables)
- [`workbook`](./workbook.md#module-workbook)
- [`worksheet`](./worksheet.md#module-worksheet)
- [`vault`](./vault.md#module-vault)

## Classes

- [`tables.Dialect`](./tables.md#class-dialect): CSV dialect.
- [`tables.Table`](./tables.md#class-table): Container class for tabular data.
- [`tables.Tables`](./tables.md#class-tables): ``Tables`` is a library for manipulating tabular data.
- [`workbook.Workbook`](./workbook.md#class-workbook): Manager class for both .xls and .xlsx Excel files.
- [`worksheet.Worksheet`](./worksheet.md#class-worksheet): Common class for worksheets to manage the worksheet's content.
- [`vault.BaseSecretManager`](./vault.md#class-basesecretmanager): Abstract class for secrets management.
- [`vault.FileSecrets`](./vault.md#class-filesecrets): Adapter for secrets stored in a database file.
- [`vault.RobocorpVault`](./vault.md#class-robocorpvault): Adapter for secrets stored in Robocorp Vault.
- [`vault.RobocorpVaultError`](./vault.md#class-robocorpvaulterror): Raised when there's problem with reading from Robocorp Vault.
- [`vault.Secret`](./vault.md#class-secret): Container for a secret with name, description, and multiple key-value pairs.
- [`vault.Vault`](./vault.md#class-vault): `Vault` is a library for interacting with secrets stored in the ``Robocorp Control Room Vault``.

## Functions

- [`browser.open_browser`](./browser.md#function-open_browser): Launches a Playwright browser instance.
- [`browser.open_url`](./browser.md#function-open_url): Launches a Playwright browser instance and opens the given URL.
- [`excel.create_workbook`](./excel.md#function-create_workbook): Create and open a new Excel workbook in memory.
- [`excel.open_workbook`](./excel.md#function-open_workbook): Open an existing Excel workbook.
- [`tables.if_none`](./tables.md#function-if_none): Return default if value is None.
- [`tables.return_table_as_raw_list`](./tables.md#function-return_table_as_raw_list)
- [`tables.to_condition`](./tables.md#function-to_condition): Convert string operator into callable condition function.
- [`tables.to_identifier`](./tables.md#function-to_identifier): Convert string to valid identifier.
- [`tables.to_list`](./tables.md#function-to_list): Convert (possibly scalar) value to list of `size`.
- [`tables.uniq`](./tables.md#function-uniq): Return list of unique values while preserving order.


---

_This file was automatically generated via [lazydocs](https://github.com/ml-tooling/lazydocs)._
