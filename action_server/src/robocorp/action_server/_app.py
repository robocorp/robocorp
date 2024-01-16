import logging
from functools import cache

from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from . import _errors
from ._settings import get_settings

LOGGER = logging.getLogger(__name__)


@cache
def get_app():
    settings = get_settings()

    server = {"url": settings.server_url}
    app = FastAPI(title=settings.title, servers=[server])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_exception_handler(_errors.RequestError, _errors.request_error_handler)
    app.add_exception_handler(HTTPException, _errors.http_error_handler)
    app.add_exception_handler(RequestValidationError, _errors.http422_error_handler)
    app.add_exception_handler(Exception, _errors.http500_error_handler)

    return app
