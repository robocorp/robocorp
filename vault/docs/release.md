
Steps to do a new release
---------------------------

- Open a shell at the proper place (something as `X:/robocorpws/robo/vault`)

- Create a new branch (`git checkout -b release-vault-branch`)

- Update version (`inv set-version 0.3.0`).

- Update README.md to add notes on features/fixes (on `robocorp-vault`).

- Update changelog.md to add notes on features/fixes and set release date.

- Push contents, and check if tests passed in https://github.com/robocorp/robo/actions.
  - `mu acp robocorp-vault release 0.3.0`

- Create a tag and push it (`git tag robocorp-vault-0.3.0&&git push origin robocorp-vault-0.3.0`).

- Rebase with master (`git checkout master&git rebase -`).

- Send release msg. i.e.:

Hi @channel,

I'm happy to announce the release of `Robocorp vault 0.3.0`.

*## Changes*


`Robocorp vault` may be installed with: `pip install robocorp-vault`.
Links: [PyPI](https://pypi.org/project/robocorp-vault/), [GitHub (sources)](https://github.com/robocorp/robocorp-vault)