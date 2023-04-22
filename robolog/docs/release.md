
Steps to do a new release
---------------------------

- Open a shell at the proper place (something as `X:/robocorpws/robo/robolog`)

- Update version (`python -m dev set-version 0.0.10`).

- Update README.md to add notes on features/fixes (on `robocorp-robolog`).

- Update changelog.md to add notes on features/fixes and set release date.

- Push contents, and check if tests passed in https://github.com/robocorp/robo/actions.
  - `mu acp robocorp-robolog release 0.0.10`

- Create a tag (`git tag robocorp-robolog-0.0.10`) and push it.

- After published in PyPi, head over to the tasks module and run: `poetry lock` (then a new tasks release may be done).

- Rebase with master (`git checkout master&git rebase release-robocorp-robolog`).

- Send release msg. i.e.:

Hi @channel,

I'm happy to announce the release of `Robocorp Logging 0.0.10`.

*## Changes*


`Robocorp Logging` may be installed with: `pip install robocorp-robolog`.
Links: [PyPI](https://pypi.org/project/robocorp-robolog/), [GitHub (sources)](https://github.com/robocorp/robocorp-robolog)