
Steps to do a new release
---------------------------

- Open a shell at the proper place (something as `X:/robocorpws/robo/browser`)

- Update version (`inv set-version 1.0.2`).

- Update docs (`inv docs`).

- Update README.md to add notes on features/fixes (on `robocorp-browser`).

- Update changelog.md to add notes on features/fixes and set release date.

- Push contents, and check if tests passed in https://github.com/robocorp/robo/actions.
  - `mu acp robocorp-browser release 1.0.2`

- `inv make-release` to create tag
