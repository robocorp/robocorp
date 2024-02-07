# Changelog

## 1.4.3 - 2024-02-07

- Support for retrieving the error through the `exception` property of a failed input
  work item.

## 1.4.2 - 2024-01-14

- Fix main README and update docs.

## 1.4.1 - 2023-11-09

- Upgrades `dataclasses-json` dependency to at least **0.6.1**
- Prevent invalid operations on released work items with `FileAdapter`

## 1.4.0 - 2023-09-07

- Add support for `RC_DISABLE_SSL`

## 1.3.2 - 2023-08-24

- Handle exceptions derived from `BusinessException` or `ApplicationException`

## 1.3.1 - 2023-08-22

- Create missing parent folders when testing in VSCode

## 1.3.0 - 2023-07-31

- Improve development workflow with better error messages and more lenient defaults
- Allow mutating input work items

## 1.2.1 - 2023-06-28

- Updated dependency on `robocorp-tasks` to `>=1,<3`.
