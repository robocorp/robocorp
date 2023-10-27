from fastapi import APIRouter

from .. import __version__
from .._models import StatusResponse

router = APIRouter()


@router.get("/status", response_model=StatusResponse)
def status():
    return {"version": __version__}
