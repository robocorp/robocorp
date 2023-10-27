from fastapi import APIRouter
from fastapi.routing import APIRoute

from . import runs, status, tasks

api_router = APIRouter(prefix="/api")

api_router.include_router(
    status.router,
    tags=["status"],
)
api_router.include_router(
    tasks.router,
    tags=["tasks"],
)
api_router.include_router(
    runs.router,
    tags=["runs"],
)

for route in api_router.routes:
    if isinstance(route, APIRoute):
        route.operation_id = route.name
