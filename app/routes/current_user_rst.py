from typing import Annotated

from aio_pika import Message
from fastapi import APIRouter
from pydantic import Field
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_422_UNPROCESSABLE_ENTITY

from app.common.config import email_confirmation_cryptography, pochta_producer
from app.common.responses import Responses
from app.models.users_db import User
from app.utils.authorization import (
    AuthorizedResponses,
    AuthorizedSession,
    AuthorizedUser,
)
from app.utils.magic import include_responses
from app.utils.users import UsernameResponses, is_username_unique

router = APIRouter(tags=["current user"])


@router.get(
    "/home/",
    response_model=User.FullModel,
    responses=AuthorizedResponses.responses(),
)
async def get_user_data(user: AuthorizedUser) -> User:
    return user


@include_responses(UsernameResponses, AuthorizedResponses)
class UserPatchResponses(Responses):
    pass


@router.patch(
    "/profile/",
    response_model=User.FullModel,
    responses=UserPatchResponses.responses(),
    summary="Update current user's profile data",
)
async def patch_user_data(
    patch_data: User.ProfilePatchModel, user: AuthorizedUser
) -> User:
    if not await is_username_unique(patch_data.username, user.username):
        raise UsernameResponses.USERNAME_IN_USE.value
    user.update(**patch_data.model_dump(exclude_defaults=True))
    return user


@include_responses(AuthorizedResponses)
class PasswordProtectedResponses(Responses):
    WRONG_PASSWORD = (HTTP_401_UNAUTHORIZED, "Wrong password")


@include_responses(PasswordProtectedResponses)
class PasswordChangeResponse(Responses):
    OLD_PASSWORD = (
        HTTP_422_UNPROCESSABLE_ENTITY,
        "Can't change old password to the old one",
    )


class EmailChangeModel(User.PasswordModel):
    new_email: Annotated[str, Field(max_length=100)]


class PasswordChangeModel(User.PasswordModel):
    new_password: str


@router.put(
    "/email/",
    response_model=User.FullModel,
    responses=PasswordProtectedResponses.responses(),
    summary="Update current user's email",
)
async def change_user_email(user: AuthorizedUser, put_data: EmailChangeModel) -> User:
    if not user.is_password_valid(password=put_data.password):
        raise PasswordProtectedResponses.WRONG_PASSWORD.value

    user.email = put_data.new_email
    user.email_confirmed = False

    confirmation_token: str = email_confirmation_cryptography.encrypt(user.email)
    await pochta_producer.send_message(
        message=Message(
            (
                f"Your email has been changed to {put_data.new_email},"
                + f"confirm new email: {confirmation_token}"
            ).encode("utf-8")
        ),
    )

    return user


@router.put(
    "/password/",
    response_model=User.FullModel,
    responses=PasswordChangeResponse.responses(),
    summary="Update current user's password",
)
async def change_user_password(
    user: AuthorizedUser, session: AuthorizedSession, put_data: PasswordChangeModel
) -> User:
    if not user.is_password_valid(password=put_data.password):
        raise PasswordProtectedResponses.WRONG_PASSWORD

    if user.is_password_valid(put_data.new_password):
        raise PasswordChangeResponse.OLD_PASSWORD

    user.change_password(put_data.new_password)
    await session.disable_all_other()

    return user
