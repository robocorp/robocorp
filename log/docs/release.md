
Steps to do a new release
---------------------------

- Open a shell at the proper place (something as `X:/robocorpws/robo/log`)

- Update version (`inv set-version 1.2.0`).

- Update docs version (`inv docs`).

- Update README.md to add notes on features/fixes (on `robocorp-log`).

- Update changelog.md to add notes on features/fixes and set release date.

- `mu acp robocorp-log release 1.2.0`

- Create a tag (`git tag robocorp-log-1.2.0`) and push it.

- After published in PyPi, head over to the tasks module and run: `poetry lock` (then a new tasks release may be done).

- Notify users about release.
