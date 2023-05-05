<h1>
  <a href="https://github.com/robocorp/robo/">
    <img src="./docs/include/logo.png" alt="Robo Logo" height="100">
  </a>
</h1>

# Robo is an all-in-one Python automation framework

## Create, develop, run, and deploy your automation code with Robo - and operate it all with Control Room

Supports Windows, MacOS, and Linux

<br/>
<details open="open">
<summary>Table of Contents</summary>

- [What is Robo?](#what-is-robo)
- [CLI](#cli)
- [Libraries](#libraries)
- [Documentation](#documentation)

</details>

---

## What is Robo?

Robo is both a CLI for managing your Python projects, and a set of libraries for automating your tasks. It handles your entire automation development lifecycle, and has several key features:

- **Isolated environments.** Get started without installing any other tools, not even Python. Robo automatically creates fully isolated environments for projects, which can be reproduced anywhere else.
- **Batteries included.** Robo ships with a broad set of libraries for automating common tasks, be it browser automation, document processing, or navigating desktop applications.
- **Reduce boilerplate.** Turn your Python snippet into a runnable automation with minimal effort. Robo can be used to execute your code in other environments, and deployed in Control Room without any infrastructure work.
- **Troubleshoot easily.** Robo automatically traces your automation task, and create an easy-to-read report of what happened. You can quickly see if something went wrong - and how to fix it.

Robo is designed to function as a single tool that helps you more easily get things done. It is entirely compatible with the PyPI and Conda ecosystems, but also brings in a set of libraries designed from the ground up to be focused on automation.

## CLI

The `robo` CLI is used to manage and run your projects during development, and it bundles your project for deployment.

#### `robo new`

Create an entirely new Python project, isolated from the rest of your system. No need to install Python separately or manually manage virtual environments.

#### `robo run`

Run your defined Python tasks. Robo instruments the running code, and generates a pretty report of what was executed.

#### `robo exec`

Easily run an arbitrary command within the isolated environment, such as shell commands or a locally installed application.

#### `robo export`

Package your project as a Control Room compatible bundle, ready for deployment.

## Libraries

The framework includes Python libraries for configuring project entrypoints and controlling features such as a logging. The project also provides an extensive selection of libraries for the most common automation tasks, and anything else can be easily done through what is already available in the Python ecosystem.

#### `robocorp.tasks`

Create entrypoints for your automation project.

#### `robocorp.log`

Configure and control the execution log.

#### `robocorp.vault`

Store secret values in Control Room and access them during the execution.

#### `robocorp.workitems`

Interact with Control Room work items; Read data from previous steps, create output data.

#### `robocorp.browser`

Automate actions in a browser, powered by [Playwright](https://playwright.dev/).

#### `robocorp.http`

Download files easily, or make custom HTTP requests.

## Documentation

To see how to use the libraries, refer to [API documentation](docs/README.md) hosted in the repository.

For in-depth tutorials and troubleshooting guides, refer to [Robocorp Docs](https://robocorp.com/docs).
