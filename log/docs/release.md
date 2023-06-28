
Steps to do a new release
---------------------------

- Open a shell at the proper place (something as `D:/x/robocorpws/robo/log`)

- Update version (`inv set-version 2.0.0`).

- Update docs version (`inv docs`)  -- make sure not to be in `subst` drive.

- Update README.md to add notes on features/fixes (on `robocorp-log`).

- Update changelog.md to add notes on features/fixes and set release date.

- `mu acp robocorp-log release 2.0.0`

- Create a tag (`inv make-release`) and push it.

- After published in PyPi, head over to the tasks module and run: `poetry lock` (then a new tasks release may be done).

- Notify users about release.
