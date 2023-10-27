import logging
import traceback
from enum import Enum
from typing import Any, Dict, Union

from fastapi import status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.constants import REF_PREFIX
from fastapi.openapi.utils import validation_error_response_definition
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

LOGGER = logging.getLogger(__name__)


class ErrorCode(str, Enum):
    UNKNOWN = "unknown"
    INTERNAL_ERROR = "internal-error"
    VALIDATION_ERROR = "validation-error"
    TIMEOUT_ERROR = "timeout-error"
    NOT_AVAILABLE = "not-available"
    INVALID_REQUEST = "invalid-request"
    INVALID_VALUE = "invalid-value"


class RequestError(RuntimeError):
    def __init__(self, error_code: ErrorCode, message: str):
        super().__init__()
        self.error_code = error_code
        self.message = message


class ErrorResponse(BaseModel):
    error_code: ErrorCode
    message: str


def _to_response(
    error_code: ErrorCode,
    message: str,
    path: str,
    trace=False,
) -> Dict[str, Any]:
    LOGGER.error("Invalid request: %s [%s]", message, path)
    if trace:
        LOGGER.error(traceback.format_exc())

    return {"error_code": error_code, "message": message}


async def request_error_handler(request: Request, exc: RequestError):
    return JSONResponse(
        status_code=400,
        content=_to_response(
            error_code=exc.error_code,
            message=exc.message,
            path=str(request.url.path),
        ),
    )


async def http_error_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_to_response(
            error_code=ErrorCode.UNKNOWN,
            message=str(exc.detail),
            path=str(request.url.path),
        ),
    )


async def http422_error_handler(
    request: Request,
    exc: Union[RequestValidationError, ValidationError],
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_to_response(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="\n".join(str(err) for err in exc.errors()),
            path=str(request.url.path),
        ),
    )


async def http500_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_to_response(
            error_code=ErrorCode.INTERNAL_ERROR,
            message=str(exc),
            path=str(request.url.path),
            trace=True,
        ),
    )

    # CORSMiddleware is not used for unhandled server exceptions
    # in FastAPI/Starlette, so we set it manually here
    origin = request.headers.get("origin")
    if origin:
        cors = CORSMiddleware(
            app=request.app,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
            allow_credentials=True,
        )
        response.headers.update(cors.simple_headers)
        if cors.allow_all_origins and "cookie" in request.headers:
            response.headers["Access-Control-Allow-Origin"] = origin
        elif not cors.allow_all_origins and cors.is_allowed_origin(origin=origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers.add_vary_header("Origin")

    return response


validation_error_response_definition["properties"] = {
    "errors": {
        "title": "Errors",
        "type": "array",
        "items": {"$ref": f"{REF_PREFIX}ValidationError"},
    },
}
