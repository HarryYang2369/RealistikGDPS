from __future__ import annotations

from fastapi import Depends
from fastapi import Form
from fastapi import Request
from fastapi.responses import FileResponse

from rgdps import logger
from rgdps.api import responses
from rgdps.api.context import HTTPContext
from rgdps.api.dependencies import password_authenticate_dependency
from rgdps.config import config
from rgdps.constants.errors import ServiceError
from rgdps.models.user import User
from rgdps.usecases import save_data


async def save_data_get(
    ctx: HTTPContext = Depends(),
    user: User = Depends(password_authenticate_dependency()),
):
    # TODO: Streaming
    data = await save_data.get(ctx, user.id)

    if isinstance(data, ServiceError):
        logger.info(
            "Failed to fetch save data.",
            extra={
                "user_id": user.id,
                "error": data.value,
            },
        )
        return responses.fail()

    logger.info(
        "Successfully fetched save data.",
        extra={
            "user_id": user.id,
        },
    )
    return data


async def save_data_post(
    ctx: HTTPContext = Depends(),
    user: User = Depends(password_authenticate_dependency()),
    data: str = Form(..., alias="saveData"),  # Pain.
    game_version: int = Form(..., alias="gameVersion"),
    binary_version: int = Form(..., alias="binaryVersion"),
):
    res = await save_data.save(
        ctx,
        user.id,
        data,
        game_version,
        binary_version,
    )

    if isinstance(res, ServiceError):
        logger.info(
            "Failed to write save data.",
            extra={
                "user_id": user.id,
                "error": res.value,
            },
        )
        return responses.fail()

    logger.info(
        "Successfully wrote save data.",
        extra={
            "user_id": user.id,
        },
    )
    return responses.success()


# An endpoint that specified which server to use for storing user save data.
# TODO: Support an external save server.
async def get_save_endpoint(request: Request) -> str:
    return f"{request.url.scheme}://{request.url.hostname}{config.http_url_prefix}"
