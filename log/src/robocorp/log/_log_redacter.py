import itertools
from collections.abc import MutableSet
from functools import partial
from re import Pattern
from typing import Optional

from robocorp.log._lifecycle_hooks import Callback


class _SetWithChangeModification(MutableSet[str]):
    def __init__(self, initial=()):
        self._data = set()
        self._data.update(initial)

        # Clients may register 'on_change' to get notifications.
        self.on_change = Callback()
        self.on_change.raise_exceptions = True

    def update(self, values):
        initial_len = len(self._data)
        self._data.update(values)
        if len(self._data) == initial_len:
            # Nothing actually changed
            return

        self.on_change()

    def pop(self):
        self._data.pop()
        self.on_change()

    def clear(self):
        if not self._data:
            return

        self._data.clear()
        self.on_change()

    def add(self, value):
        if value in self._data:
            return  # Don't trigger a modified
        self._data.add(value)
        self.on_change()

    def discard(self, value):
        if value not in self._data:
            return  # Don't trigger a modified
        self._data.discard(value)
        self.on_change()

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, item):
        return item in self._data


class RedactConfiguration:
    def __init__(self, on_changed) -> None:
        self._next = partial(next, itertools.count())

        # By default common python strings are not tracked
        self._dont_hide_strings: _SetWithChangeModification = (
            _SetWithChangeModification(("None", "True", "False"))
        )
        self._hide_strings: _SetWithChangeModification = _SetWithChangeModification()

        # By default, strings with 1 or 2 chars won't be
        self._minimum_string_size: int = 2

        self._dont_hide_strings.on_change.register(on_changed)
        self._hide_strings.on_change.register(on_changed)
        self._on_changed = on_changed

    # Public API

    @property
    def dont_hide_strings(self) -> MutableSet[str]:
        return self._dont_hide_strings

    @property
    def hide_strings(self) -> MutableSet[str]:
        return self._hide_strings

    @property
    def dont_hide_strings_smaller_or_equal_to(self) -> int:
        return self._minimum_string_size

    @dont_hide_strings_smaller_or_equal_to.setter
    def dont_hide_strings_smaller_or_equal_to(self, minimum_string_size: int) -> None:
        assert isinstance(
            minimum_string_size, int
        ), f"Expected int. Found: {minimum_string_size}."
        self._minimum_string_size = minimum_string_size
        self._on_changed()


class LogRedacter:
    def __init__(self) -> None:
        self._hide_strings_re: Optional[Pattern[str]] = None
        self.config = RedactConfiguration(self._after_redact_info_changed)
        self.redact = self._no_redact

    def hide_from_output(self, string_to_hide: str) -> None:
        self.config.hide_strings.add(string_to_hide)

    def _after_redact_info_changed(self):
        self.redact = self._update_redact_re_and_redact

    def _update_redact_information(self):
        import re

        lst = []
        dont_hide_strings = self.config.dont_hide_strings
        dont_hide_strings_smaller_or_equal_to = (
            self.config.dont_hide_strings_smaller_or_equal_to
        )
        for s in self.config.hide_strings:
            if s and s not in dont_hide_strings:
                if len(s) > dont_hide_strings_smaller_or_equal_to:
                    lst.append(re.escape(s))

        if lst:
            self._hide_strings_re = re.compile("|".join(lst))
        else:
            self._hide_strings_re = None

    def _update_redact_re_and_redact(self, s, replacement="<redacted>"):
        self._update_redact_information()
        hide_strings_re = self._hide_strings_re
        if hide_strings_re is None:
            self.redact = self._no_redact
            return s

        self.redact = self._re_redact
        return self.redact(s, replacement)

    def _re_redact(self, s, replacement="<redacted>"):
        return self._hide_strings_re.sub(replacement, s)

    def _no_redact(self, s, replacement="<redacted>"):
        return s


_log_redacter = LogRedacter()
