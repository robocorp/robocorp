# Changelog

## 1.3.3 - 2024-02-01

- Leave the range more flexible for cryptography so that users can use a newer
  version (`">=41.0.6,<44"`)

## 1.3.2 - 2024-01-14

- Security update: use at least `cryptography` **41.0.6**.
  ([*CVE-2023-49083*](https://nvd.nist.gov/vuln/detail/CVE-2023-49083))

## 1.3.1 - 2024-01-14

- Fix main README and update docs.

## 1.3.0 - 2023-09-07

- Add support for `RC_DISABLE_SSL`

## 1.2.0 - 2023-07-14

- Add method `create_secret` for creating new secrets in Vault

## 1.1.0 - 2023-07-12

- Automatic API retries for higher robustness
- Improved error messages

## 1.0.0

- In the file backend if an error happens such error is thrown
- Besides automatically hiding secret values from the log as `str(value)`, values
  are also hidden as `repr(value)`

## 0.4.0

- cryptography now requires 41.x

## 0.3.0

- Updated APIs. Public APIs are now: `robocorp.vault.get_secret` and `robocorp.vault.set_secret`
