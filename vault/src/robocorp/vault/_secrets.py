import collections
from typing import Any, Dict, Iterator


class SecretContainer(collections.abc.Mapping[str, Any]):
    """Container for a secret with name, description, and multiple key-value pairs.

    Avoids logging internal values when possible.

    Note that keys are always converted to str internally.
    """

    def __init__(self, name: str, description: str, values: Dict[str, Any]):
        """
        Args:
            name:        Name of secret
            description: Human-friendly description for secret
            values:      Dictionary of key-value pairs stored in secret
        """
        self._name = name
        self._desc = description
        self._dict = dict((str(key), val) for key, val in values.items())

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._desc

    def update(self, kvpairs) -> None:
        self._dict.update(kvpairs)

    def __getitem__(self, key: str) -> Any:
        key = str(key)
        return self._dict[key]

    def __setitem__(self, key: str, value: Any):
        key = str(key)
        self._dict[key] = value

    def __contains__(self, key: object) -> bool:
        key = str(key)
        return key in self._dict

    def __iter__(self) -> Iterator[str]:
        return iter(self._dict)

    def __len__(self) -> int:
        return len(self._dict)

    def __repr__(self) -> str:
        return "Secret(name={name}, keys=[{keys}])".format(
            name=self.name, keys=", ".join(str(key) for key in self.keys())
        )
