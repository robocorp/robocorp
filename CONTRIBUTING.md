# Contributing

This is a contribution guide for the `robocorp` project and associated libraries.

## Library Development

### Prerequisites

The tool used for Python dependency management is `poetry` and the commands
to manage the project are run with `invoke`.

They can be installed via pip:

```
pip install poetry
pip install invoke
```

Note that `invoke` will automatically call the commands using `poetry run`, so,
in general it's not needed to activate the environment manually.

### Conda

While `conda` is not always required (if not found a `.venv` will be created
by `poetry` based on the global python found), when it's found, running 
commands from `invoke` will prefix such commands with 
`conda run -n <project-name>` and `inv install` will create
the related environment automatically. 

When using conda, `poetry` and `invoke` should've been installed in the base environment.

### Development

To start working on a library, you need to install the project's development-time
dependencies. This can be done by navigating to the library's folder and running:

```
inv install
```

This will create an environment for that project (either in `.venv` or with
conda with an env based on the project name).

If other dependent libraries also need to be changed (for instance, when
running on `robocorp-tasks` but also needing to change something in `robocorp-log`),
it's possible to use:

```
inv devinstall
```

This will install all the robocorp libraries in development mode in the python env.

### Calling invoke tasks

To see all available tasks, run `invoke --list` or `inv -l` for short:

```
invoke --list
```

For instance, linting can be run with:

```
inv lint
```

If linting fails, syntax issues are usually be fixed by: 

```
inv pretty
```

Typechecking can be checked with:

```
inv typecheck
```


### Testing

Testing is done with `pytest` for python libraries. For javascript `jest` is
usually used.

To run all tests for a given project, go to the project folder in the monorepo
and then run `inv test`.
(to run single tests, it's recommended that you configure your favorite editor/IDE
to use the test framework inside your IDE).

### Releasing

To make a new release from a library, ensure the following things are done:

1. Documentation has been updated by running `invoke docs` and committing the generated files.
2. The version has been updated according to [semantic versioning](https://semver.org/).
   This can be done by running `invoke set-version <version>`, which modifies all related
   files with the new version number.
3. A new changelog entry is added to `<library>/docs/CHANGELOG.md` that describes the changes.
4. All changed code is pushed to `master` and the test workflows in GitHub Actions are passing.

To trigger a release, a commit should be tagged with the name and version of the library.
The tag can be generated automatically with `invoke make-release`. After the tag has been pushed,
a corresponding GitHub Actions workflow will be triggered that builds the library and publishes
it to PyPI.

### Metapackage

In the `meta` folder is a metapackage for the core features of the `robocorp` framework,
i.e. logging, tasks, and Control Room libraries. It is used in templates and examples
as an easy way to get the main features into a project.

The package is available in PyPI as [robocorp](https://pypi.org/project/robocorp/).

After a new release has been made to one of the contained libraries, the metapackage
should be updated with the correct dependencies. To see if the current configuration
matches what is availale in PyPI, run the following:

```
inv outdated
```

If it warns about outdated packages, they can be updated with:

```
inv update
```

The update task also automatically bumps the version of the metapackage based
on the changed versions of the dependencies. Releasing it, is done similarly
to other libraries with `invoke make-release`.
