from ._request import Cookies, Headers, Request


class _RequestImpl(Request):
    """
    Actual implementation of a request (not exposed to clients, the public API
    is only considered to be the `Request`).

    In particular, it's possible that the constructor changes in the future
    to handle things more lazily.
    """

    def __init__(self, headers: Headers, cookies: Cookies):
        self._headers: Headers = headers
        self._cookies: Cookies = cookies

    @property
    def headers(self) -> Headers:
        return self._headers

    @property
    def cookies(self) -> Cookies:
        return self._cookies

    @classmethod
    def model_validate(cls, dct: dict) -> "Request":
        """
        If the user passes the request in the json input (for testing), we should
        be able to decode it and provide a request based on that data.
        """
        headers = Headers(dct.get("headers"))
        cookies = Cookies(dct.get("cookies"))

        return cls(headers=headers, cookies=cookies)
