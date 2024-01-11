# robocorp (metapackage)

This is a metapackage for installing the core libraries like logging, vault, asset storage and Control Room integrations, in a single easy to install dependency.


The following packages are currently included:

[![robocorp](https://img.shields.io/pypi/v/robocorp?label=robocorp)](https://pypi.org/project/robocorp/)


| Name                                | Releases in PyPI                                                                                                                                          | Description                                                                                                                       |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|
| [`robocorp.tasks`](./tasks)         | [![robocorp-tasks](https://img.shields.io/pypi/v/robocorp-tasks?label=robocorp-tasks)](https://pypi.org/project/robocorp-tasks/)                 | Create entrypoints for your automation project.                                                                                   |
| [`robocorp.log`](./log)             | [![robocorp-log](https://img.shields.io/pypi/v/robocorp-log?label=robocorp-log)](https://pypi.org/project/robocorp-log/)                         | Configure and control the execution log.                                                                                          |
| [`robocorp.vault`](./vault)         | [![robocorp-vault](https://img.shields.io/pypi/v/robocorp-vault?label=robocorp-vault)](https://pypi.org/project/robocorp-vault/)                 | Store secret values in Control Room and access them during the execution.                                                         |
| [`robocorp.workitems`](./workitems) | [![robocorp-workitems](https://img.shields.io/pypi/v/robocorp-workitems?label=robocorp-workitems)](https://pypi.org/project/robocorp-workitems/) | Interact with Control Room work items; Read data from previous steps, create output data.                                         |
| [`robocorp.storage`](./storage)     | [![robocorp-storage](https://img.shields.io/pypi/v/robocorp-storage?label=robocorp-storage)](https://pypi.org/project/robocorp-storage/)         | Store assets in Control Room and manage them during the execution.                                                                |


For further documentation on libraries, see the [Libraries docs](../docs/README.md).
