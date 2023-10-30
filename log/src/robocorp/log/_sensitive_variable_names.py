import re
from typing import Dict, List, Optional, Pattern, Sequence, Set, Union


class SensitiveVariableNames:
    def __init__(self, default_sensitive_variable_names: Sequence[str]):
        self._sensitive_variable_re: Optional[Pattern[str]] = None
        self._additional_patterns: List[Pattern] = []

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
            if self._sensitive_variable_regexps:
                regexp = self._sensitive_variable_re = re.compile(
                    "|".join(self._sensitive_variable_regexps)
                )

        if regexp is not None:
            is_sensitive = regexp.match(variable_name)
        else:
            is_sensitive = False

        if not is_sensitive:
            for pattern in self._additional_patterns:
                if pattern.match(variable_name):
                    is_sensitive = True
                    break

        self._cache[variable_name] = is_sensitive
        return is_sensitive

    def add_sensitive_variable_name(self, variable_name: str) -> None:
        variable_name_pattern = f".*{re.escape(variable_name)}.*"
        self.add_sensitive_variable_name_pattern(variable_name_pattern)

    def add_sensitive_variable_name_pattern(
        self, variable_name_pattern: Union[str, Pattern]
    ) -> None:
        if isinstance(variable_name_pattern, str):
            if not variable_name_pattern:
                raise ValueError(
                    "Error: empty string cannot be used to match sensitive variable names."
                )
            self._sensitive_variable_regexps.add(variable_name_pattern)
            self._sensitive_variable_re = None
        elif isinstance(variable_name_pattern, re.Pattern):
            self._additional_patterns.append(variable_name_pattern)
        else:
            raise ValueError(
                f"Expected a str or Pattern. Received: {type(variable_name_pattern)}."
            )
        self._cache.clear()


_sensitive_names = SensitiveVariableNames(("password", "passwd"))
