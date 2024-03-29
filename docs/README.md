# Documentation

## Overview

The repository contains the essential parts of the Robocorp Automation Stack for Python:
- AI Actions and Action Server are described in the main [README](../README.md).
- Libraries with which the Actions or [Tasks](guides/using-with-rcc.md) are created are also housed and developed under this repository.

## Python Libraries

The framework includes Python libraries for configuring package's entry points and controlling features such as logging.  
The project also provides an extensive selection of libraries for the most common automation tasks, and anything else can be easily done through what is already available in the Python ecosystem.

You can find the source code and library API documentation in this repository.  
We strongly recommend to surf our documentation [website](https://robocorp.com/docs/python).

### The `robocorp` meta-package

[![robocorp](https://img.shields.io/pypi/v/robocorp?label=robocorp)](https://pypi.org/project/robocorp/)

The easiest way to get started is to install the [**robocorp**](../meta/README.md) meta-package, which includes the framework's core features such as defining _Tasks_, logging, _Work Items_, _Vault_, _Assets_ and other Control Room integrations.

### Packages

It's possible to install individual components of the project as separate dependencies.

| Name                                | Release in PyPI                                                                                                                                        | Description                                                                                                                       | Metapackage |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------| --- |
| [`robocorp.actions`](../actions)     | [![robocorp-actions](https://img.shields.io/pypi/v/robocorp-actions?label=robocorp-actions)](https://pypi.org/project/robocorp-actions/)         | Enables creation of AI Actions for Action Server: "Give hands to your AI" | - |
| [`robocorp.tasks`](../tasks)         | [![robocorp-tasks](https://img.shields.io/pypi/v/robocorp-tasks?label=robocorp-tasks)](https://pypi.org/project/robocorp-tasks/)                 | Create entrypoints for your automation project.                                                                                   | ✅ |
| [`robocorp.log`](../log)             | [![robocorp-log](https://img.shields.io/pypi/v/robocorp-log?label=robocorp-log)](https://pypi.org/project/robocorp-log/)                         | Configure and control the execution log.                                                                                          | ✅ |
| [`robocorp.workitems`](../workitems) | [![robocorp-workitems](https://img.shields.io/pypi/v/robocorp-workitems?label=robocorp-workitems)](https://pypi.org/project/robocorp-workitems/) | Interact with Control Room work items; Read data from previous steps, create output data.                                         | ✅ |
| [`robocorp.vault`](../vault)         | [![robocorp-vault](https://img.shields.io/pypi/v/robocorp-vault?label=robocorp-vault)](https://pypi.org/project/robocorp-vault/)                 | Store secret values in Control Room and access them during the execution.                                                         | ✅ |
| [`robocorp.storage`](../storage)     | [![robocorp-storage](https://img.shields.io/pypi/v/robocorp-storage?label=robocorp-storage)](https://pypi.org/project/robocorp-storage/)         | Store assets in Control Room and manage them during the execution.                                                                | ✅ |
| [`robocorp.browser`](../browser)     | [![robocorp-browser](https://img.shields.io/pypi/v/robocorp-browser?label=robocorp-browser)](https://pypi.org/project/robocorp-browser/)         | Automate actions in a browser, powered by [Playwright](https://playwright.dev/).                                                  | - |
| [`robocorp.windows`](../windows)     | [![robocorp-windows](https://img.shields.io/pypi/v/robocorp-windows?label=robocorp-windows)](https://pypi.org/project/robocorp-windows/)         | Automate Windows desktop applications, powered by [uiautomation](https://github.com/yinkaisheng/Python-UIAutomation-for-Windows). | - |
| [`robocorp.excel`](../excel)         | [![robocorp-excel](https://img.shields.io/pypi/v/robocorp-excel?label=robocorp-excel)](https://pypi.org/project/robocorp-excel/)                 | Read and write Excel files directly, with support for both .xlsx and .xls.                                                        | - |

> ⚠️ Any library that isn't included by default in `robocorp` (not having the "Metapackage" mark) should be added as a dependency if you wish to make it available in your Python environment.  
> Do this by listing any of the above as a requirement in your dependencies configuration file:
> - _conda.yaml_ for automation [Task Packages](https://robocorp.com/docs/robot-structure)
> - _package.yaml_ for automation Action Packages
> - _requirements.txt_, _pyproject.toml_, _setup.py|cfg_ etc. for the rest

#### On versions

We follow [SemVer](https://semver.org) to the best of our ability in library versioning.  
This means that libraries with version `0.x.x` are in the development phase, so there can be breaking changes on any
version update.  
We aim to get libraries to version `1` as soon as possible, and after that, following the expected SemVer rules.

A new major version will be published when breaking changes are introduced, therefore the changelog should contain guidance on migration given what was changed.

> Be aware that modules starting with an underscore `_` are not considered part of the public API and should not be imported directly!  
> So only the functions/classes reached from the `robocorp.<library>` namespace should be used. If availability to some other private object is needed, please create a feature request to address it.

### Other libraries

- [RPA Framework for Python](https://rpaframework.org/)
  - For additional automation capabilities on the Robocorp platform, please refer to the wide array of libraries and keywords available in **rpaframework**.
  - [PyPI](https://pypi.org/project/rpaframework/)
  - [GitHub](https://github.com/robocorp/rpaframework)
  - [Documentation](https://robocorp.com/docs/python/rpa-framework)

- [3rd-party libraries](3rd_party/README.md)
  - We are also collecting pointers to other 3rd-party libraries that we see as commonly used or just beneficial to automation cases.
  - We try to collect the needed links and provide some common code snippets to help you on your way.
  - [Documentation](https://robocorp.com/docs/python/3rd-party-libraries)
