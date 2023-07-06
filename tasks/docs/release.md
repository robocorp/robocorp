
Steps to do a new release
---------------------------

- Open a shell at the proper place (something as `D:/x/robocorpws/robo/tasks`)

- Update version, poetry, docs -- make sure not to be in `subst` drive:
```
inv set-version 2.1.1
poetry lock
poetry install
inv docs
```

- Update README.md to add notes on features/fixes (on `robocorp-tasks`).

- Update changelog.md to add notes on features/fixes and set release date.

- Push contents, and check if tests passed in https://github.com/robocorp/robo/actions.
  - `mu acp robocorp-tasks release 2.1.1`

- Create a tag and push it (`inv make-release`).

- Send release msg. i.e.:

Hi @channel,

I'm happy to announce the release of `Robocorp Tasks 1.0.0`.

*## Changes*


`Robocorp Tasks` may be installed with: `pip install robocorp-tasks`.
Links: [PyPI](https://pypi.org/project/robocorp-tasks/), [GitHub (sources)](https://github.com/robocorp/robocorp-tasks)