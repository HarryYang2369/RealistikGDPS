from __future__ import annotations

from rgdps.api.commands.framework import CommandContext
from rgdps.api.commands.framework import CommandRouter
from rgdps.api.commands.framework import LevelCommand
from rgdps.api.commands.framework import make_command
from rgdps.constants.errors import ServiceError
from rgdps.constants.users import UserPrivileges
from rgdps.models.level import Level
from rgdps.usecases import levels

router = CommandRouter("levels_root")
level_group = CommandRouter("level")
router.register_command(level_group)


@level_group.register_function()
async def award(ctx: CommandContext, level: Level | None = None) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to delete."

    res = await levels.set_award(ctx, level.id)

    if isinstance(res, ServiceError):
        return f"Failed to award level with error {res!r}!"

    return f"The level {level.name!r} has been awarded."


@level_group.register_function()
async def unaward(ctx: CommandContext, level: Level | None = None) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to delete."

    res = await levels.set_unaward(ctx, level.id)

    if isinstance(res, ServiceError):
        return f"Failed to unaward level with error {res!r}!"

    return f"The level {level.name!r} has been unawarded."


@level_group.register_function()
async def delete(ctx: CommandContext, level: Level | None = None) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to delete."

    res = await levels.delete(
        ctx,
        level.id,
        ctx.user.id,
        ctx.user.privileges & UserPrivileges.LEVEL_DELETE_OTHER > 0,
    )

    if isinstance(res, ServiceError):
        return f"Failed to delete level with error {res!r}!"

    return f"The level {level.name!r} has been deleted."


@level_group.register_function()
async def unlist(
    ctx: CommandContext,
    friends_only: bool = False,
    level: Level | None = None,
) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to unlist."

    res = await levels.set_unlisted(
        ctx,
        level.id,
        ctx.user.id,
        friends_only,
        ctx.user.privileges & UserPrivileges.LEVEL_MODIFY_VISIBILITY > 0,
    )

    if isinstance(res, ServiceError):
        return f"Failed to unlist level with error {res!r}!"

    return f"The level {level.name!r} has been unlisted."


@level_group.register_function()
async def relist(
    ctx: CommandContext,
    level: Level | None = None,
) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to relist."

    res = await levels.set_listed(
        ctx,
        level.id,
        ctx.user.id,
        ctx.user.privileges & UserPrivileges.LEVEL_MODIFY_VISIBILITY > 0,
    )

    if isinstance(res, ServiceError):
        return f"Failed to relist level with error {res!r}!"

    return f"The level {level.name!r} has been re-listed."


@level_group.register_function()
async def description(
    ctx: CommandContext,
    description: str,
    level: Level | None = None,
) -> str:
    if level is None:
        level = ctx.level

    if level is None:
        return "You need to specify a level to set the description of."

    res = await levels.set_description(
        ctx,
        level.id,
        ctx.user.id,
        description,
        ctx.user.privileges & UserPrivileges.LEVEL_CHANGE_DESCRIPTION_OTHER > 0,
    )

    if isinstance(res, ServiceError):
        return f"Failed to set level description with error {res!r}!"

    return f"The level {level.name!r} has had its description set."
