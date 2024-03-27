# Contributing

This is a contribution guide for the Robocorp project and its associated libraries.

## Libraries

### Prerequisites

The tool used for Python dependency management is Poetry (`poetry`), and the commands to manage the project are run
with Invoke (`invoke` / `inv`).

These, along the rest of the other required initial dependencies, should be installed from our
[requirements.txt][requirements] file.

```
pip install -r devutils/requirements.txt
```

> Note that Invoke will automatically call its commands under the Poetry context (`poetry run` prefix), therefore you
> don't need to usually activate any virtual environment before running such commands.

#### Environment isolation

Sometimes you don't want to end up with development dependencies in your system's Python, or simply, you want to be in
control of the interpreter version you use without affecting the default Python.

Therefore, you have a couple of flexible options to achieve this top-level isolation:

##### RCC

Leveraging `rcc venv` power on creating ready-for-development virtual environments with a simple script run.

###### Mac / Linux

```bash
% ./devutils/bin/develop.sh
% . ./devutils/bin/develop.sh
```

###### Windows

```bat
> .\devutils\bin\develop.bat
```

##### Conda

While `conda` is not always required (if not found, a _.venv_ will be created by Poetry based on the global Python
found), if it's found, running commands with Invoke, will prefix them with `conda run -n <package-name>`, thus
`inv install` will create the adjacent environment automatically.

##### Pyenv

After [installing](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation) `pyenv`, you should be able to pick
and configure your desired interpreter version, isolated from the system.

This step is required once, right from the repository root directory:

```
pyenv install 3.10.12
pyenv local 3.10.12
```

Check with `pyenv versions` your currently active interpreter to be used as default under any package, and with
`pyenv which <executable>` the absolute path to the resolved executable you want to run.

> When using Conda or Pyenv, Poetry and Invoke should have been installed in the base environment by _pip_ installing
> the [requirements.txt][requirements] first.

### Development

To start working on a library, you need to install the project's development-time dependencies. This can be done by
navigating to the package's folder and running:

```
inv install
```

💡 This will create/set up an environment for that project, either in a new local _.venv_ dir (Pyenv approach), or in the
currently active virtual environment (RCC/Conda approach).

If other dependent libraries also need to be changed (for instance, when changes in [_tasks_](tasks) require changes in
[_log_](log) as well to work end-to-end), it's possible to use `inv devinstall`. This will install all the `robocorp-*`
libraries in development mode right in the same Python virtual environment.

### Calling Invoke tasks

To see all the available tasks, run `invoke --list` (`inv -l` for short).

For instance, linting can be run with:

```
inv lint
```

If linting fails, auto-format can be applied with:

```
inv pretty
```

Type-checking can be checked with:

```
inv typecheck
```

Docs should be generated after each change with:

```
inv docs
```

And everything combined with:

```
inv check-all
```

### Testing

Testing is done with `pytest` for the Python libraries. For javascript `jest` is the used one.

To run all tests for a given project, go to the project's folder in the monorepo and then run `inv test`. If you want
a specific test to be run, then `inv test -t path/to/test.py::function_name` would do it.

> It's recommended that you configure your favorite editor/IDE to use the test framework inside your IDE.

### Releasing

To make a new release for a library, ensure the following steps are accomplished in order:

1. Documentation is up-to-date in the _docs_ dir through the `inv docs` command and `inv check-all` is passing.
2. The version is bumped according to [semantic versioning](https://semver.org/). This can be done by running
   `inv set-version <version>`, which updates all relevant files with the new version number, then adds an entry to the
   _docs/CHANGELOG.md_ describing the changes.
3. The changes above are already committed/integrated into `master`, the test workflows in GitHub Actions are passing,
   and you're operating on the `master` branch locally.
5. You run `inv make-release` to create and push the release tag which will trigger the GitHub workflow that makes the
   release.

> To trigger a release, a commit should be tagged with the name and version of the library. The tag can be generated
> and pushed automatically with `inv make-release`. After the tag has been pushed, a corresponding GitHub Actions 
> workflow will be triggered that builds the library and publishes it to PyPI.

### The meta-package

In the [_meta_](meta) folder is a meta-package for the core features of the `robocorp` framework, i.e. logging, tasks,
and Control Room libraries. It is used in templates and examples as a quick way to get the essential features into
the automation code.

The package is available in PyPI as [**robocorp**](https://pypi.org/project/robocorp/) and bundles a couple of frequent
vital `robocorp-*` libraries.

After a new release has been made to one of the contained libraries, the meta-package should be updated with the
correct dependencies. To see if the current configuration matches what is available in PyPI, run the following:

```
inv outdated
```

If it warns about outdated packages, they can be updated with:

```
inv update
```

The `update` task also automatically bumps the version of the meta-package based on the changed versions of the
dependencies. Releasing it, is done similarly as with the other libraries, ending by running the very same
`inv make-release` command.


[requirements]: <devutils/requirements.txt>
