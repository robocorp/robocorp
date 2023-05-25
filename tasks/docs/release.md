
Steps to do a new release
---------------------------

- Open a shell at the proper place (something as `X:/robocorpws/robo/tasks`)

- Create a new branch (`git checkout -b release-tasks-branch`)

- Update version (`inv set-version 0.3.0`).

- Update README.md to add notes on features/fixes (on `robocorp-tasks`).

- Update changelog.md to add notes on features/fixes and set release date.

- Push contents, and check if tests passed in https://github.com/robocorp/robo/actions.
  - `mu acp robocorp-tasks release 0.3.0`

- Create a tag and push it (`git tag robocorp-tasks-0.3.0&&git push origin robocorp-tasks-0.3.0`).

- Rebase with master (`git checkout master&git rebase -`).

- Send release msg. i.e.:

Hi @channel,

I'm happy to announce the release of `Robocorp Tasks 0.3.0`.

*## Changes*


`Robocorp Tasks` may be installed with: `pip install robocorp-tasks`.
Links: [PyPI](https://pypi.org/project/robocorp-tasks/), [GitHub (sources)](https://github.com/robocorp/robocorp-tasks)