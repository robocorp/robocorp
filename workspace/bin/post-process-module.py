#! /usr/bin/env python


import re
import sys
from functools import lru_cache
from pathlib import Path


RE_MODEL_TO_PRIMITIVE = re.compile(
    # Optional[StrictStr].from_dict(obj.get("...")) ... -> obj.get("...")
    r'([\S]+)?Strict\w+?[^.]+?\.from_dict.+?(?P<object>obj\.get\("[^"]+"\)).+?(?=,?\n)'
)


@lru_cache(maxsize=1)
def _get_content(source: Path):
    return source.read_text()


def fix_model_reference_types(content: str) -> str:
    return RE_MODEL_TO_PRIMITIVE.sub(lambda match: match.group("object"), content)


def patch_model(content: str) -> str:
    if "has_more:" in content:
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

    if new_content and new_content != _get_content(source):
        source.write_text(new_content)


if __name__ == "__main__":
    main()
