
Steps to do a new release
---------------------------

- Open a shell at the proper place (something as `X:/robocorpws/robo/log`)

- Update version (`python -m dev set-version 0.0.12`).

- Update README.md to add notes on features/fixes (on `robocorp-log`).

- Update changelog.md to add notes on features/fixes and set release date.

- Push contents, and check if tests passed in https://github.com/robocorp/robo/actions.
  - `mu acp robocorp-log release 0.0.12`

- Create a tag (`git tag robocorp-log-0.0.12`) and push it.

- After published in PyPi, head over to the tasks module and run: `poetry lock` (then a new tasks release may be done).

- Rebase with master (`git checkout master&git rebase release-robocorp-log`).

- Send release msg. i.e.:

Hi @channel,

I'm happy to announce the release of `Robocorp Logging 0.0.12`.

*## Changes*


`Robocorp Logging` may be installed with: `pip install robocorp-log`.
Links: [PyPI](https://pypi.org/project/robocorp-log/), [GitHub (sources)](https://github.com/robocorp/robocorp-log)