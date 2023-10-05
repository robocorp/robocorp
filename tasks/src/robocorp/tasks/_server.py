from enum import Enum
from functools import cache, wraps
from queue import Queue
from threading import Thread
from typing import Any, Iterator, Optional, Union

from fastapi import FastAPI
from pydantic import BaseModel

from ._protocols import IContext, ITask


class ServerSettings(BaseModel):
    title: str = "robo"
    host: str = "localhost"
    port: int = 8080

    class Config:
        # pylint: disable=too-few-public-methods
        validate_assignment = True

    @classmethod
    def defaults(cls):
        props = cls.schema()["properties"]
        return {key: value.get("default") for key, value in props.items()}

    def from_args(self, args):
        # self.host = args.host
        self.port = args.server_port

    def to_uvicorn(self):
        return {
            "host": self.host,
            "port": self.port,
            "reload": False,
            "log_config": None,
        }


@cache
def get_settings() -> ServerSettings:
    return ServerSettings()


class ErrorCode(str, Enum):
    UNKNOWN = "unknown"
    INTERNAL_ERROR = "internal-error"
    VALIDATION_ERROR = "validation-error"
    TIMED_OUT_ERROR = "timed-out-error"
    NOT_AVAILABLE = "not-available"
    INVALID_REQUEST = "invalid-request"
    INVALID_VALUE = "invalid-value"


class ErrorResponse(BaseModel):
    error_code: ErrorCode
    message: str


def _add_error_handlers(app: FastAPI, context: IContext):
    import traceback
    from typing import Any, Dict, Union

    from fastapi import status
    from fastapi.exceptions import HTTPException, RequestValidationError
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.openapi.constants import REF_PREFIX
    from fastapi.openapi.utils import validation_error_response_definition
    from fastapi.requests import Request
    from fastapi.responses import JSONResponse
    from pydantic import ValidationError

    def _to_response(
        error_code: ErrorCode,
        message: str,
        path: str,
        trace=False,
    ) -> Dict[str, Any]:
        context.show_error(f"Invalid request: {message} ({path})")
        if trace:
            context.show_error(traceback.format_exc())

        return {"error_code": error_code, "message": message}

    async def _http_error_handler(
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

    app.add_exception_handler(HTTPException, _http_error_handler)

    async def _http422_error_handler(
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

    app.add_exception_handler(RequestValidationError, _http422_error_handler)

    async def _http500_error_handler(
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

    app.add_exception_handler(Exception, _http500_error_handler)

    validation_error_response_definition["properties"] = {
        "errors": {
            "title": "Errors",
            "type": "array",
            "items": {"$ref": f"{REF_PREFIX}ValidationError"},
        },
    }


def _add_event_handlers(app: FastAPI, context: IContext):
    settings = get_settings()

    def _on_startup():
        docs_url = f"http://{settings.host}:{settings.port}/docs"
        context.show("\n\033[1mStarted server \033[93mଘ(੭ˊᵕˋ)੭* ੈ✩‧₊˚\033[0m")
        context.show(f"Documentation: {docs_url}")

    def _on_shutdown():
        pass

    app.add_event_handler("startup", _on_startup)
    app.add_event_handler("shutdown", _on_shutdown)


@cache
def _get_app() -> FastAPI:
    from fastapi.middleware.cors import CORSMiddleware

    settings = get_settings()

    app = FastAPI(title=settings.title)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    return app


class TaskInfo(BaseModel):
    name: str
    line: int
    file: str
    docs: str


class QueueRequest(BaseModel):
    name: str
    fields: dict[str, Any]


class QueueResponse(BaseModel):
    status: bool
    error: Optional[str] = None
    value: Any


class TxQueue:
    def __init__(self):
        self._requests: Queue[QueueRequest] = Queue()
        self._responses: Queue[QueueResponse] = Queue()

    def __iter__(self) -> Iterator[QueueRequest]:
        while True:
            yield self._requests.get()

    def send_request(self, name, **fields):
        self._requests.put(QueueRequest(name=name, fields=fields))

    def send_response(self, result: QueueResponse):
        self._responses.put(result)

    def wait_response(self) -> QueueResponse:
        return self._responses.get()


def run_server(context: IContext, tasks: list[ITask]) -> tuple[TxQueue, Thread]:
    import uvicorn

    app = _get_app()
    queue = TxQueue()

    _add_event_handlers(app, context)
    _add_error_handlers(app, context)

    @app.get("/list")
    def list_tasks() -> list[TaskInfo]:
        response = []
        for task in tasks:
            response.append(
                TaskInfo(
                    name=task.name,
                    line=task.lineno,
                    file=task.filename,
                    docs=getattr(task.method, "__doc__") or "",
                )
            )
        return response

    for task in tasks:
        # Who doesn't love closures?
        def _make_endpoint(task):
            @app.post(f"/run/{task.name}")
            @wraps(task.method)
            def run_task(**kwargs):
                queue.send_request(task.name, **kwargs)
                resp = queue.wait_response()
                if not resp.status:
                    raise RuntimeError(str(resp.error))

                return resp.value

        _make_endpoint(task)

    kwargs = get_settings().to_uvicorn()
    thread = Thread(target=uvicorn.run, args=(app,), kwargs=kwargs)
    thread.daemon = True
    thread.start()

    return queue, thread
