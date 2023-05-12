# robo command line tool

## Functionality

The `robo` CLI is used to manage and run your projects during development, and it bundles your project for deployment.

#### `robo new`

Create an entirely new Python project, isolated from the rest of your system. No need to install Python separately or manually manage virtual environments.

#### `robo run`

Run your defined Python tasks. Robo instruments the running code, and generates a pretty report of what was executed.

#### `robo exec`

Easily run an arbitrary command within the isolated environment, such as shell commands or a locally installed application.

#### `robo export`

Package your project as a Control Room compatible bundle, ready for deployment.


# development instructions

## Releasing

1. Update the version in `cli/VERSION`
2. Add the new version and a short description of changes to `cli/CHANGELOG.md`
3. Git commit the above changes
4. Tag the commit matching the pattern `cli-<version>` (e.g. `cli-0.1.0`)
5. Push the commit and tag to GitHub
6. Wait for CI to build the new release and upload the artifacts.
