import logging
from functools import cache

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from . import _errors
from ._settings import get_settings

LOGGER = logging.getLogger(__name__)


class _CustomFastAPI(FastAPI):
    def openapi(self):
        """
        As we're no longer using custom models for the routing APIs (instead of
        pydantic or generated methods for the API, the body is directly queried
        and interpreted as json and its schema validated), FastAPI is no longer
        adding the error references, so, we override the FastAPI.openapi()
        method to provide the needed components.
        """
        if self.openapi_schema:
            return self.openapi_schema

        openapi = FastAPI.openapi(self)
        components = openapi.setdefault("components", {})
        schemas = components.setdefault("schemas", {})
        schemas["HTTPValidationError"] = {
            "properties": {
                "errors": {
                    "items": {"$ref": "#/components/schemas/ValidationError"},
                    "type": "array",
                    "title": "Errors",
                }
            },
            "type": "object",
            "title": "HTTPValidationError",
        }
        schemas["ValidationError"] = {
            "properties": {
                "loc": {
                    "items": {"anyOf": [{"type": "string"}, {"type": "integer"}]},
                    "type": "array",
                    "title": "Location",
                },
                "msg": {"type": "string", "title": "Message"},
                "type": {"type": "string", "title": "Error Type"},
            },
            "type": "object",
            "required": ["loc", "msg", "type"],
            "title": "ValidationError",
        }

        return openapi


@cache
def get_app() -> FastAPI:
    settings = get_settings()

    server = {"url": settings.server_url}
    app = _CustomFastAPI(title=settings.title, servers=[server])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_exception_handler(_errors.RequestError, _errors.request_error_handler)  # type: ignore
    app.add_exception_handler(HTTPException, _errors.http_error_handler)  # type: ignore
    app.add_exception_handler(RequestValidationError, _errors.http422_error_handler)  # type: ignore
    app.add_exception_handler(Exception, _errors.http500_error_handler)

    return app
