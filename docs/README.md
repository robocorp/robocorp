# Documentation

## Overview

The repository contains the essential parts of the Robocorp Automation Stack for Python:
- AI Actions and Action Server are described in the [main readme](../README.md)
- To create your Actions or [Tasks](guides/using-with-rcc.md) the repo also houses the sources for the new automation libraries for Python

## Python Libraries

The framework includes Python libraries for configuring project entry points and controlling features such as logging. The project also provides an extensive selection of libraries for the most common automation tasks, and anything else can be easily done through what is already available in the Python ecosystem.

You can find the source codes and library API documentation in this repository.

You can also use the our [documentation -site](https://robocorp.com/docs/python)

### The 'robocorp' -meta package
[![robocorp](https://img.shields.io/pypi/v/robocorp?label=robocorp)](https://pypi.org/project/robocorp/)

The easiest way to get started is to install the [`robocorp`](../meta/README.md) meta-package, which includes the framework's core features, such as logging, Vault, Asset Storage, and Control Room integrations.


### Packages

It's possible to install individual components of the project as separate dependencies.

| Name                                | Release in PyPI                                                                                                                                        | Description                                                                                                                       | Metapackage |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------| --- |
| [`robocorp.tasks`](../tasks)         | [![robocorp-tasks](https://img.shields.io/pypi/v/robocorp-tasks?label=robocorp-tasks)](https://pypi.org/project/robocorp-tasks/)                 | Create entrypoints for your automation project.                                                                                   | ✅ |
| [`robocorp.log`](../log)             | [![robocorp-log](https://img.shields.io/pypi/v/robocorp-log?label=robocorp-log)](https://pypi.org/project/robocorp-log/)                         | Configure and control the execution log.                                                                                          | ✅ |
| [`robocorp.vault`](../vault)         | [![robocorp-vault](https://img.shields.io/pypi/v/robocorp-vault?label=robocorp-vault)](https://pypi.org/project/robocorp-vault/)                 | Store secret values in Control Room and access them during the execution.                                                         | ✅ |
| [`robocorp.workitems`](../workitems) | [![robocorp-workitems](https://img.shields.io/pypi/v/robocorp-workitems?label=robocorp-workitems)](https://pypi.org/project/robocorp-workitems/) | Interact with Control Room work items; Read data from previous steps, create output data.                                         | ✅ |
| [`robocorp.storage`](../storage)     | [![robocorp-storage](https://img.shields.io/pypi/v/robocorp-storage?label=robocorp-storage)](https://pypi.org/project/robocorp-storage/)         | Store assets in Control Room and manage them during the execution.                                                                | ✅ |
| [`robocorp.browser`](../browser)     | [![robocorp-browser](https://img.shields.io/pypi/v/robocorp-browser?label=robocorp-browser)](https://pypi.org/project/robocorp-browser/)         | Automate actions in a browser, powered by [Playwright](https://playwright.dev/).                                                  | - |
| [`robocorp.actions`](../actions)     | [![robocorp-actions](https://img.shields.io/pypi/v/robocorp-actions?label=robocorp-actions)](https://pypi.org/project/robocorp-actions/)         | Enables creation of AI Actions for Action Server: "Give hands to your AI" | - |
| [`robocorp.windows`](../windows)     | [![robocorp-windows](https://img.shields.io/pypi/v/robocorp-windows?label=robocorp-windows)](https://pypi.org/project/robocorp-windows/)         | Automate Windows desktop applications, powered by [uiautomation](https://github.com/yinkaisheng/Python-UIAutomation-for-Windows). | - |
| [`robocorp.excel`](../excel)         | [![robocorp-excel](https://img.shields.io/pypi/v/robocorp-excel?label=robocorp-excel)](https://pypi.org/project/robocorp-excel/)                 | Read and write Excel files directly, with support for both .xlsx and .xls.                                                        | - |

> ⚠️ Any library that isn't included by default in `robocorp` (not having the
> "Metapackage" mark) should be added as a dependency if you wish to make it available
> in your Python environment. Do this by listing any of the above as a requirement in
> your dependencies configuration file:
> - _conda.yaml_ for an automation Task Package
> - _action-package.yaml_ for an automation Action Package
> - _requirements.txt_, _pyproject.toml_ etc. for the rest

> **On versions:** <br/>
We follow [semver](https://semver.org) to the best of our ability in library versioning.<br/>
This means that libraries with version `v0.x.x' are in the development phase, so there can be breaking changes on any version update.<br/>
We aim to get libraries to `v1` as soon as possible and after that again follow the normal `semver` rules.

### Other libraries

- [RPA Framework for Python](https://robocorp.com/docs/python/rpa-framework)
  - For additional automation capabilities on the Robocorp platform, please refer to the wide array of libraries and keywords available in 'rpaframework'
  - [PyPI](https://pypi.org/project/rpaframework/)
  - [GitHub](https://github.com/robocorp/rpaframework)

- [3rd-party libraries](3rd_party/README.md)
  - We are also collecting pointers to other 3rd-party libraries that we see as commonly used or just beneficial to automation cases.
  - We try to collect the needed links and provide some common code snippets to help you on your way
  - [List in this repo](./3rd_party/README.md)
  - [Docs-site (coming soon...)](https://robocorp.com/docs/python/3rd-party)
