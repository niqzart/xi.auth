from fastapi import APIRouter

from app.models.users_db import User
from app.utils.authorization import AuthorizedUser
from app.utils.users import TargetUser, UserResponses

router = APIRouter(tags=["users"])


@router.get(
    "/by-id/{user_id}/profile/",
    response_model=User.UserProfileModel,
    responses=UserResponses.responses(),
    summary="Retrieve user profile by id",
)
async def get_profile_by_id(user: TargetUser) -> User:
    return user


@router.get(
    "/by-username/{username}/profile/",
    response_model=User.UserProfileModel,
    responses=UserResponses.responses(),
    summary="Retrieve user profile by username",
)
async def get_profile_by_username(
    username: str,
    current_user: AuthorizedUser,
) -> User:
    user = await User.find_first_by_kwargs(username=username)
    if user is None:
        raise UserResponses.USER_NOT_FOUND.value
    return user
