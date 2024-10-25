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

        use_dict = {}
        for key, value in headers.items():
            if not isinstance(key, str):
                raise ValueError(
                    f"Expected key to be a string. Found: {key} ({type(key)})"
                )
            if not isinstance(value, str):
                raise ValueError(
                    f"Expected value to be a string. Found: {value} ({type(value)})"
                )
            use_dict[key.upper()] = value

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
    Contains the information exposed in a request (such as headers and cookies).

    May be extended in the future to provide more information.
    """

    @property
    def headers(self) -> Headers:
        """
        Provides the headers received in the request (excluding `cookies` which
        are available in `cookies`).
        """
        raise NotImplementedError(
            "This is an abstract class. Subclasses are expected to reimplement this method."
        )

    @property
    def cookies(self) -> Cookies:
        """
        Provides the cookies received in the request.
        """
        raise NotImplementedError(
            "This is an abstract class. Subclasses are expected to reimplement this method."
        )

    @classmethod
    def model_validate(cls, dct: dict) -> "Request":
        from sema4ai.actions._request_impl import _RequestImpl

        return _RequestImpl.model_validate(dct)
