# package.yaml

### Note: introduced in the Action Server version: 0.0.21

The `package.yaml` file is the base file which defines everything related to the
actions available in the action package.

> Note: previous versions of the action server used a `conda.yaml` or `action-server.yaml`,
which are not directly compatible to `package.yaml` (so, they can't be just renamed
directly and some changes are expected in how to define the environment).

> Running: `action-server package update` can be used to automatically
upgrade a package in an older version to the new expected format.

An example `package.yaml` would be something as:

```yaml
    # Required: Defines the name of the action package.
    name: My awesome cookie maker  

    # Required: A description of what's in the action package.
    description: This does cookies  

    # Required: The current version of this action package.
    version: 0.2.3

    # Required: A link to where the documentation on the package lives.
    documentation: https://github.com/robocorp/actions-cookbook/blob/master/database-postgres/README.md

    # Required:
    # Defines the Python dependencies which should be used to launch the 
    # actions.
    # The action server will automatically create a new python environment
    # based on this specification.
    # Note that at this point the only operator supported is `=`.
    dependencies:
      conda-forge: 
        # This section is required: at least the python version must be specified.
        - python=3.10.12
        - pip=23.2.1
        - robocorp-truststore=0.8.0

      pypi:
        # This section is required: at least `robocorp-actions` must
        # be specified.
        # Note: robocorp-actions is special case because the action server
        # has coupling with the library. This means that if the version of
        # robocorp-actions is not pinned to a value the action server will
        # select a version based on a version that's known to work with the
        # current version of the action server.
        # If the version is pinned, then the action server will validate
        # if the given version can be used with it.
        - robocorp-actions
        - robocorp=1.4.3
        - pytz=2023.3

    post-install:
        # This can be used to run custom commands which will still affect the 
        # environment after it is created (the changes to the environment will
        # be cached).
        - python -m robocorp.browser install chrome --isolated

    packaging:
      # This section is optional.
      # By default all files and folders in this directory are packaged when uploaded.
      # Add exclusion rules below (expects glob format: https://docs.python.org/3/library/glob.html)
      exclude:
       - *.temp
       - .vscode/**
```
