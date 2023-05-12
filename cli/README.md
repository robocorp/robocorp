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

## Installing RCC from command line

### Windows

1. Open the command prompt
1. Download: `curl -o robo.exe https://downloads.robocorp.com/robo/releases/latest/windows64/robo.exe`
1. [Add to system path](https://www.architectryan.com/2018/03/17/add-to-the-path-on-windows-10/): Open Start -> `Edit the system environment variables`
1. Test: `robo`

### macOS

Coming soon
#### Brew cask from Robocorp tap

1. Install: `brew install robocorp/tools/robo`
1. Test: `robo`

Upgrading: `brew upgrade robo`

#### Raw download

1. Open the terminal
1. Download: `curl -o robo https://downloads.robocorp.com/robo/releases/latest/macos64/robo`
1. Make the downloaded file executable: `chmod a+x robo`
1. Add to path: `sudo mv robo /usr/local/bin/`
1. Test: `robo`

### Linux

1. Open the terminal
1. Download: `curl -o robo https://downloads.robocorp.com/robo/releases/latest/linux64/robo`
1. Make the downloaded file executable: `chmod a+x robo`
1. Add to path: `sudo mv robo /usr/local/bin/`
1. Test: `robo`

### [Direct downloads for signed executables provided by Robocorp](https://downloads.robocorp.com/robo/releases/index.html)

Follow above link to download site. Both tested and bleeding edge versions are available from same location.


# development instructions

## Releasing

1. Update the version in `cli/VERSION`
2. Add the new version and a short description of changes to `cli/CHANGELOG.md`
3. Git commit the above changes
4. Tag the commit matching the pattern `cli-<version>` (e.g. `cli-0.1.0`)
5. Push the commit and tag to GitHub
6. Wait for CI to build the new release and upload the artifacts.

## Marking a release as "stable" / latest

1. Run the AWS codebuild for Robo

## Updating the stable version in Homebrew

1. Run the "Update Robo in Homebrew" github action in https://github.com/robocorp/packaging/actions, pass in the desired version.
