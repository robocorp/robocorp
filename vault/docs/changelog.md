1.0.0
-----------------------------

- In the file backend if an error happens such error is thrown.
- Besides automatically hiding secret values from the log as `str(value)`, values
  are also hidden as `repr(value)`.


0.4.0
-----------------------------

- cryptography now requires 41.x

0.3.0
-----------------------------

- Updated APIs. Public APIs are now: `robocorp.vault.get_secret` and `robocorp.vault.set_secret`.
