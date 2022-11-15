from __future__ import annotations

import base64

from fastapi import Depends
from fastapi import Form

from rgdps import logger
from rgdps.common import gd_obj
from rgdps.constants.errors import ServiceError
from rgdps.constants.levels import LevelLength
from rgdps.constants.responses import GenericResponse
from rgdps.models.user import User
from rgdps.usecases import levels
from rgdps.usecases import songs
from rgdps.usecases.auth import authenticate_dependency


async def get_song_info(
    song_id: int = Form(..., alias="songID"),
) -> str:

    song = await songs.get(song_id)
    if isinstance(song, ServiceError):
        logger.info(f"Failed to fetch song with error {song!r}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully fetched song {song}.")
    return gd_obj.dumps(gd_obj.create_song(song), sep="~|~")


async def upload_level(
    user: User = Depends(authenticate_dependency()),
    level_id: int = Form(..., alias="levelID"),
    name: str = Form(..., alias="levelName"),
    custom_song_id: int = Form(..., alias="songID"),
    copy_password: int = Form(..., alias="password"),
    two_player: bool = Form(..., alias="twoPlayer"),
    object_count: int = Form(..., alias="objects"),
    coins: int = Form(...),
    unlisted: bool = Form(..., alias="unlisted"),
    render_str: str = Form(..., alias="extraString"),
    requested_stars: int = Form(..., alias="requestedStars", ge=0, le=10),
    level_data: str = Form(..., alias="levelString"),
    length: LevelLength = Form(..., alias="levelLength"),
    version: int = Form(..., alias="levelVersion"),
    description_b64: str = Form(..., alias="levelDesc"),
    original: int = Form(..., alias="original"),
    official_song_id: int = Form(..., alias="audioTrack"),
    game_version: int = Form(..., alias="gameVersion"),
    binary_version: int = Form(..., alias="binaryVersion"),
    low_detail_mode: bool = Form(..., alias="ldm"),
    building_time: int = Form(..., alias="wt2"),
) -> str:

    description = base64.urlsafe_b64decode(description_b64.encode()).decode()

    level = await levels.create_or_update(
        user=user,
        level_id=level_id,
        name=name,
        custom_song_id=custom_song_id,
        copy_password=copy_password,
        two_player=two_player,
        object_count=object_count,
        coins=coins,
        unlisted=unlisted,
        render_str=render_str,
        requested_stars=requested_stars,
        level_data=level_data,
        length=length,
        version=version,
        description=description,
        original=original,
        official_song_id=official_song_id,
        game_version=game_version,
        binary_version=binary_version,
        low_detail_mode=low_detail_mode,
        building_time=building_time,
    )

    if isinstance(level, ServiceError):
        logger.info(f"Failed to upload level with error {level!r}.")
        return str(GenericResponse.FAIL)

    logger.info(f"Successfully uploaded level {level}.")
    return str(level.id)