
Steps to do a new release
---------------------------

- Open a shell at the proper place (something as `x:\robocorpws\robocorp-logging`)

- Create release branch (`git branch -D release-robocorp-logging&git checkout -b release-robocorp-logging`)

- When leaving pre-alpha: Update classifier in setup.py (currently in pre-alpha) and notes regarding being alpha in README.md.

- Update version (`python -m dev set-version 0.0.6`).

- Update embedded index.html (`python -m dev build-output-view`).

- Update README.md to add notes on features/fixes (on `robocorp-logging`).

- Update changelog.md to add notes on features/fixes and set release date.

- Push contents, and check if tests passed in https://github.com/robocorp/robotframework-lsp/actions.
  - `mu acp Robot Framework Output Stream Release 0.0.6`

- Rebase with master (`git checkout master&git rebase release-robocorp-logging`).

- Create a tag (`git tag robocorp-logging-0.0.6`) and push it.

- Send release msg. i.e.:

Hi @channel,

I'm happy to announce the release of `Robot Framework Output Stream 0.0.6`.

*## Changes*


`Robot Framework Output Stream` may be installed with: `pip install robocorp-logging`.
Links: [PyPI](https://pypi.org/project/robocorp-logging/), [GitHub (sources)](https://github.com/robocorp/robotframework-lsp/tree/master/robocorp-logging)