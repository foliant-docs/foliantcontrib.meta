# 1.3.2

- Cutomids are now cut out from titles.
- Added logging.
- Meta commands now support `--debug -d` and `--quiet -q` arguments.
- `meta generate` command now gives some verbose output after work.
- Fix: get_section_by_offset didn't count YFM.

# 1.3.1

- `remove_meta` now also trims whitespaces in the beginning of the file after removing YFM
- Main section's title is now set to first heading, if:
    * the first heading is a 1-level heading (#),
    * the first heading doesn't have meta.
- Fix: YFM was not included in meta in some cases

# 1.3.0

- Restructure modules to aid import errors. Meta-related functions and classes are now available independantly from `foliant.meta` package.

# 1.2.3

- Add `get_chapter` method to Meta class.
- Add Developer's guide to readme.

# 1.2.2

- Don't require empty line between heading and meta tag.
- Allow comments in YFM.
- Better patterns for sections detection.

# 1.2.1

- Fix bug with imports.

# 1.2.0

- Support sections
- meta.yml format restructure

# 1.1.0

- Remove the sections entity.
- Restructure code.

# 1.0.3

- Add span to meta

# 1.0.2

- Fix: subsections title may be specified in YFM;
- Fix: in subsections title was being cropped out

# 1.0.1

- Fix: seeds for main sections were not processed.
- Add debug messages for seeds processing.

# 1.0.0

Initial release.
