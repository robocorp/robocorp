# robocorp-log-pytest

`robocorp-log-pytest` is a library which provides a pytest plugin which integrates
`robocorp-log` with `pytest` so that auto-logging is provided for tests run with `pytest`.

By default just having it in use without any configuration will generate a `./output/log.html` (and by default at most 5 `.robolog` files, each with 50MB may be created).

It's possible to configure the output directory and html output name as well as the maximum number of files and the max log file size.

Note that if the logs actually start rotating information on previous tests may be lost (so, in the testing case it's recommended that the log files always cover the whole test run, which is why the default limits are set to be 50MB * 5).

Ideally for the testing use-case logs would keep the failures, but this isn't currently implemented for robocorp-log (these would need heuristics when removing old files to strip them instead of just remove them).

## API Reference

Explore our [API](https://github.com/robocorp/robocorp/blob/master/log_pytest/docs/api/README.md) for extensive documentation.

## Changelog

A list of releases and corresponding changes can be found in the
[changelog](https://github.com/robocorp/robocorp/blob/master/log_pytest/docs/CHANGELOG.md).
