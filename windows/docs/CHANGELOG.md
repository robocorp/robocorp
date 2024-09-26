# Changelog

## Unreleased

## 1.0.4 - 2024-09-25

- Bump zipp to 3.20.2

## 1.0.3 - 2024-04-08

- Stable API documentation generation impacting parameters taking functions as defaults.
- Update package's main README.
- Make `get_win_version` a static method of `windows.Desktop` for easier usage.

## 1.0.2 - 2024-02-01

- Notice in the docs about the need to include `robocorp-windows` dependency in order
  to make it available in the environment. (not included by default in `robocorp`)

## 1.0.1 - 2024-01-14

- Fix main README and update docs.

## 1.0.0 - 2023-12-12

- Documentation fixes regarding the `timeout` parameter.
- Find functions/methods now support the `raise_error` switch, and when disabled, a
  `None` is returned instead of raising in the absence of the element.
- First major release: the library passed basic testing and is considered ready for
  development.

## 0.0.1 - 2023-10-18

- First public release.
- Still considered alpha.
- Features to find window/children and interact with those as needed.
- API may still change.
