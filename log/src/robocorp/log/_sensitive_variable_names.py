import re
from typing import Dict, Optional, Pattern, Sequence, Set


class SensitiveVariableNames:
    def __init__(self, default_sensitive_variable_names: Sequence[str]):
        self._sensitive_variable_re: Optional[Pattern[str]] = None

        self._sensitive_variable_regexps: Set[str] = set()

        self._cache: Dict[str, bool] = {}

        for variable_name in default_sensitive_variable_names:
            self.add_sensitive_variable_name(variable_name)

    def is_sensitive_variable_name(self, variable_name):
        try:
            return self._cache[variable_name]
        except KeyError:
            pass

        regexp = self._sensitive_variable_re
        if regexp is None:
            # Build the regexp now
            regexp = self._sensitive_variable_re = re.compile(
                "|".join(self._sensitive_variable_regexps)
            )
        is_sensitive = regexp.match(variable_name)
        self._cache[variable_name] = is_sensitive
        return is_sensitive

    def add_sensitive_variable_name(self, variable_name: str) -> None:
        variable_name_pattern = f".*{re.escape(variable_name)}.*"
        self.add_sensitive_variable_name_pattern(variable_name_pattern)

    def add_sensitive_variable_name_pattern(self, variable_name_pattern: str) -> None:
        self._sensitive_variable_regexps.add(variable_name_pattern)
        self._sensitive_variable_re = None
        self._cache.clear()
