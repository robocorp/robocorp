
Steps to do a new release
---------------------------

- Open a shell at the proper place (something as `X:/robocorpws/robo/tasks`)

- Update version (`inv set-version 0.2.0`).

- Update README.md to add notes on features/fixes (on `robocorp-tasks`).

- Update changelog.md to add notes on features/fixes and set release date.

- Push contents, and check if tests passed in https://github.com/robocorp/robo/actions.
  - `mu acp robocorp-tasks release 0.2.0`

- Create a tag (`git tag robocorp-tasks-0.2.0`) and push it.

- Rebase with master (`git checkout master&git rebase release-robocorp-tasks`).

- Send release msg. i.e.:

Hi @channel,

I'm happy to announce the release of `Robocorp Tasks 0.2.0`.

*## Changes*


`Robocorp Tasks` may be installed with: `pip install robocorp-tasks`.
Links: [PyPI](https://pypi.org/project/robocorp-tasks/), [GitHub (sources)](https://github.com/robocorp/robocorp-tasks)