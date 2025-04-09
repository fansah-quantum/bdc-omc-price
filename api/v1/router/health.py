from typing import Union

import fastapi
from fastapi import responses

from config.setting import Settings
from schemas.health import Health, Status

"""
This health router is used to check the health of the application

"""

settings = Settings()

health_router = fastapi.APIRouter()


class HealthResponse(responses.JSONResponse):
    media_type = "application/json"


@health_router.get(
    "/health",
    response_model=Health,
    response_class=HealthResponse,
    responses={500: {"model": Health}},
)
async def get_health(
    response: HealthResponse,
) -> Union[dict[str, str], HealthResponse]:
    response.headers["Cache-Control"] = "max-age=3600"

    content = {
        "status": Status.SUCCESS,
        "version": settings.version,
        "releaseId": settings.releaseId,
    }

    return content