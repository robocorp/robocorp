# Changelog

## Unreleased

## 0.6.0 - 2026-11-01

- **Breaking:** require Python 3.11 or newer. Python 3.10 reached end of life in October 2026,
  and the `pillow` security fixes below exist only in releases that require Python 3.11.
- Require `pillow` 13.0.0 or newer (fixes 41 security advisories, 5 of them critical: heap buffer
  overflows in JPEG, FlashPix and TIFF decoding, stale native storage reuse in multi-frame loaders
  and argument injection in the Ghostscript call).

## 0.5.1 - 2026-10-18

- Require `pillow` 12.3.0 or newer (fixes 13 security advisories, including CVE-2026-59205 and CVE-2026-59200).

## 0.5.0 - 2026-03-12

- Update dependencies

## 0.4.5 - 2024-09-25

- Update dependencies
- Add more types

## 0.4.4 - 2024-04-08

- Update package's main README.

## 0.4.3 - 2024-02-01

- Notice in the docs about the need to include `robocorp-excel` dependency in order to make it available in the environment. (not included by default in `robocorp`)

## 0.4.2 - 2024-01-14

- Fix main README and update docs.
