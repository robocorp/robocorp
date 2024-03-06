"""
Note: this is not public at this point.
Headers and Cookies are not currently integrated...
"""
import typing
from typing import Dict


class _CaseInsensitiveReadOnlyDict(typing.Mapping[str, str]):
    """
    An immutable, case-insensitive multidict.
    """

    def __init__(
        self,
        headers: typing.Optional[typing.Mapping[str, str]],
    ) -> None:
        if not headers:
            headers = {}

        use_dict = dict((key.upper(), val) for (key, val) in headers.items())

        self._headers: Dict[str, str] = use_dict

    def keys(self) -> typing.KeysView[str]:
        return self._headers.keys()

    def values(self) -> typing.ValuesView[str]:
        return self._headers.values()

    def items(self) -> typing.ItemsView[str, str]:
        return self._headers.items()

    def __getitem__(self, key: str) -> str:
        return self._headers[key.upper()]

    def __contains__(self, key: typing.Any) -> bool:
        return key.upper() in self._headers

    def __iter__(self) -> typing.Iterator[typing.Any]:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self._headers)

    def __eq__(self, other: typing.Any) -> bool:
        if not isinstance(other, _CaseInsensitiveReadOnlyDict):
            return False
        return self._headers == other._headers

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self._headers!r})"


class Headers(_CaseInsensitiveReadOnlyDict):
    pass


class Cookies(_CaseInsensitiveReadOnlyDict):
    pass


class Request:
    """
    Requests contains the information exposed in a request.

    If clients require more information, this class can be extended as
    needed.
    """

    def __init__(self, headers: Headers, cookies: Cookies):
        self.headers: Headers = headers
        self.cookies: Cookies = cookies
