
Steps to do a new release
---------------------------

- Open a shell at the proper place (something as `X:/robocorpws/robo/browser`)

- Update version (`inv set-version 0.4.0`).

- Update README.md to add notes on features/fixes (on `robocorp-browser`).

- Update changelog.md to add notes on features/fixes and set release date.

- Push contents, and check if tests passed in https://github.com/robocorp/robo/actions.
  - `mu acp robocorp-browser release 0.4.0`

- Create a tag and push it (`git tag robocorp-browser-0.4.0&&git push origin robocorp-browser-0.4.0`).

- Rebase with master (`git checkout master&git rebase -`).
