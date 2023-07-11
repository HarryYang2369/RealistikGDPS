from __future__ import annotations

from datetime import datetime
from typing import NamedTuple
from typing import Optional
from typing import Union

from rgdps import repositories
from rgdps.common import hashes
from rgdps.common.context import Context
from rgdps.constants.errors import ServiceError
from rgdps.constants.friends import FriendStatus
from rgdps.constants.users import UserPrivacySetting
from rgdps.constants.users import UserPrivileges
from rgdps.models.user import User


DEFAULT_PRIVILEGES = (
    UserPrivileges.USER_AUTHENTICATE
    | UserPrivileges.USER_PROFILE_PUBLIC
    | UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC
    | UserPrivileges.USER_CP_LEADERBOARD_PUBLIC
    | UserPrivileges.USER_CREATE_USER_COMMENTS
    | UserPrivileges.USER_CHANGE_CREDENTIALS_OWN
    | UserPrivileges.LEVEL_UPLOAD
    | UserPrivileges.LEVEL_UPDATE
    | UserPrivileges.LEVEL_DELETE_OWN
    | UserPrivileges.COMMENTS_POST
    | UserPrivileges.COMMENTS_DELETE_OWN
    | UserPrivileges.COMMENTS_TRIGGER_COMMANDS
    | UserPrivileges.MESSAGES_SEND
    | UserPrivileges.MESSAGES_DELETE_OWN
    | UserPrivileges.FRIEND_REQUESTS_SEND
    | UserPrivileges.FRIEND_REQUESTS_ACCEPT
    | UserPrivileges.FRIEND_REQUESTS_DELETE_OWN
    | UserPrivileges.COMMENTS_LIKE
)


async def register(
    ctx: Context,
    name: str,
    password: str,
    email: str,
) -> Union[User, ServiceError]:

    if await repositories.user.check_email_exists(ctx, email):
        return ServiceError.USER_EMAIL_EXISTS
    elif await repositories.user.check_username_exists(ctx, name):
        return ServiceError.USER_USERNAME_EXISTS

    hashed_password = await hashes.hash_bcypt_async(password)

    user = User(
        id=0,
        username=name,
        email=email,
        password=hashed_password,
        privileges=DEFAULT_PRIVILEGES,
        stars=0,
        demons=0,
        creator_points=0,
        display_type=0,
        primary_colour=0,
        secondary_colour=0,
        coins=0,
        user_coins=0,
        icon=0,
        ship=0,
        ball=0,
        ufo=0,
        wave=0,
        robot=0,
        spider=0,
        explosion=0,
        glow=False,
        message_privacy=UserPrivacySetting.PUBLIC,
        friend_privacy=UserPrivacySetting.PUBLIC,
        comment_privacy=UserPrivacySetting.PUBLIC,
        youtube_name=None,
        twitter_name=None,
        twitch_name=None,
        register_ts=datetime.now(),
        diamonds=0,
    )

    user_id = await repositories.user.create(ctx, user)
    user.id = user_id
    return user


async def authenticate(
    ctx: Context,
    username: str,
    password: str,
) -> Union[User, ServiceError]:
    user = await repositories.user.from_name(ctx, username)

    if user is None:
        return ServiceError.AUTH_NOT_FOUND

    if not await hashes.compare_bcrypt(user.password, password):
        return ServiceError.AUTH_PASSWORD_MISMATCH

    if not user.privileges & UserPrivileges.USER_AUTHENTICATE:
        return ServiceError.AUTH_NO_PRIVILEGE

    return user


class UserPerspective(NamedTuple):
    user: User
    rank: int
    friend_status: FriendStatus


async def get(
    ctx: Context,
    user_id: int,
    is_own: bool = True,
) -> Union[UserPerspective, ServiceError]:
    # TODO: Perform Friend Check
    # TODO: Friend Request Check
    # TODO: Messages Check

    user = await repositories.user.from_id(ctx, user_id)
    if user is None:
        return ServiceError.USER_NOT_FOUND

    rank = await repositories.leaderboard.get_star_rank(ctx, user_id)

    if is_own:
        ...

    return UserPerspective(
        user=user,
        rank=rank,
        friend_status=FriendStatus.NONE,
    )


async def update_stats(
    ctx: Context,
    user_id: int,
    stars: Optional[int] = None,
    demons: Optional[int] = None,
    display_type: Optional[int] = None,
    diamonds: Optional[int] = None,
    primary_colour: Optional[int] = None,
    secondary_colour: Optional[int] = None,
    icon: Optional[int] = None,
    ship: Optional[int] = None,
    ball: Optional[int] = None,
    ufo: Optional[int] = None,
    wave: Optional[int] = None,
    robot: Optional[int] = None,
    spider: Optional[int] = None,
    glow: Optional[bool] = None,
    explosion: Optional[int] = None,
    coins: Optional[int] = None,
    user_coins: Optional[int] = None,
    message_privacy: Optional[UserPrivacySetting] = None,
    friend_privacy: Optional[UserPrivacySetting] = None,
    comment_privacy: Optional[UserPrivacySetting] = None,
    youtube_name: Optional[str] = None,
    twitter_name: Optional[str] = None,
    twitch_name: Optional[str] = None,
    update_rank: bool = False,
) -> Union[User, ServiceError]:
    # TODO: Validation
    # TODO: Anticheat checks on the user's gains
    user = await repositories.user.from_id(ctx, user_id)

    if user is None:
        return ServiceError.USER_NOT_FOUND

    updated_user = User(
        id=user.id,
        username=user.username,
        email=user.email,
        password=user.password,
        privileges=user.privileges,
        message_privacy=message_privacy or user.message_privacy,
        friend_privacy=friend_privacy or user.friend_privacy,
        comment_privacy=comment_privacy or user.comment_privacy,
        youtube_name=youtube_name or user.youtube_name,
        twitter_name=twitter_name or user.twitter_name,
        twitch_name=twitch_name or user.twitch_name,
        register_ts=user.register_ts,
        stars=stars or user.stars,
        demons=demons or user.demons,
        display_type=display_type or user.display_type,
        diamonds=diamonds or user.diamonds,
        primary_colour=primary_colour or user.primary_colour,
        secondary_colour=secondary_colour or user.secondary_colour,
        icon=icon or user.icon,
        ship=ship or user.ship,
        ball=ball or user.ball,
        ufo=ufo or user.ufo,
        wave=wave or user.wave,
        robot=robot or user.robot,
        spider=spider or user.spider,
        glow=glow or user.glow,
        explosion=explosion or user.explosion,
        coins=coins or user.coins,
        user_coins=user_coins or user.user_coins,
        creator_points=user.creator_points,
    )

    if update_rank:
        await repositories.leaderboard.set_star_count(ctx, user.id, updated_user.stars)

    await repositories.user.update(ctx, updated_user)
    return updated_user


async def update_privileges(
    ctx: Context,
    user_id: int,
    privileges: UserPrivileges,
) -> Union[User, ServiceError]:

    user = await repositories.user.from_id(ctx, user_id)
    if user is None:
        return ServiceError.USER_NOT_FOUND

    # Check if we should remove them from the leaderboard
    if not privileges & UserPrivileges.USER_STAR_LEADERBOARD_PUBLIC:
        await repositories.leaderboard.remove_star_count(ctx, user_id)

    if not privileges & UserPrivileges.USER_CP_LEADERBOARD_PUBLIC:
        # TODO: Add CP leaderboard
        ...

    updated_user = user.copy()
    updated_user.privileges = privileges
    await repositories.user.update(ctx, updated_user)
    return updated_user
