from __future__ import annotations

from typing import Optional

from realistikgdps.constants.likes import LikeType
from realistikgdps.models.like import Like
from realistikgdps.state import services


async def from_id(id: int) -> Optional[Like]:
    like_db = await services.database.fetch_one(
        "SELECT target_type, target_id, user_id, value FROM likes WHERE id = :id",
        {
            "id": id,
        },
    )

    if like_db is None:
        return None

    return Like(
        id=id,
        target_type=LikeType(like_db["target_type"]),
        target_id=like_db["target_id"],
        user_id=like_db["user_id"],
        value=like_db["value"],
    )


async def create(like: Like) -> int:
    return await services.database.execute(
        "INSERT INTO likes (target_type, target_id, user_id, value) VALUES "
        "(:target_type, :target_id, :user_id, :value)",
        {
            "target_type": like.target_type.value,
            "target_id": like.target_id,
            "user_id": like.user_id,
            "value": like.value,
        },
    )


async def exists_by_target_and_user(
    target_type: LikeType,
    target_id: int,
    user_id: int,
) -> bool:
    return (
        await services.database.fetch_one(
            "SELECT id FROM likes WHERE target_type = :target_type AND target_id = :target_id AND user_id = :user_id",
            {
                "target_type": target_type.value,
                "target_id": target_id,
                "user_id": user_id,
            },
        )
        is not None
    )


async def sum_by_target(
    target_type: LikeType,
    target_id: int,
) -> int:
    like_db = await services.database.fetch_one(
        "SELECT SUM(value) AS sum FROM likes WHERE target_type = :target_type "
        "AND target_id = :target_id",
        {
            "target_type": target_type.value,
            "target_id": target_id,
        },
    )

    if like_db is None:
        return 0

    return like_db["sum"]