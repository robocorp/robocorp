
Steps to do a new release
---------------------------

- Open a shell at the proper place (something as `X:/robocorpws/robo/storage`)

- Update version (`inv set-version 0.1.0`).

- Update docs version (`inv docs`).

- Update README.md to add notes on features/fixes (on `robocorp-storage`).

- Update changelog.md to add notes on features/fixes and set release date.

- Create a tag (`git tag robocorp-storage-0.1.0`) and push it.

- Notify users about release.
