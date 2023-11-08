#! /usr/bin/env python

import sys
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def _get_content(source: Path):
    return source.read_text()


def fix_model_reference_types(content: str):
    # FIXME(cmin764, 8 Nov 2023): Replace `.from_dict`.
    return content


def patch_model(content: str):
    if "cls.model_validate" in content:
        content = fix_model_reference_types(content)

    return content


def main():
    patchers = {
        "models": patch_model,
    }
    source = Path(sys.argv[1])
    # New content obtained after patching, gets chained to all the next subsequent
    #  patchers.
    new_content = None
    for trace, patch_func in patchers.items():
        if trace in str(source):
            new_content = patch_func(new_content or _get_content(source))

    if new_content != _get_content(source):
        source.write_text(new_content)


if __name__ == "__main__":
    main()
