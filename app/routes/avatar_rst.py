from typing import Annotated

import filetype  # type: ignore[import-untyped]
from fastapi import APIRouter, File, UploadFile
from filetype.types.image import Webp  # type: ignore[import-untyped]

from app.common.responses import Responses
from app.utils.authorization import AuthorizedUser

router = APIRouter(tags=["current user avatar"])


class AvatarResponses(Responses):
    WRONG_FORMAT = (415, "Invalid image format")


@router.put("/", status_code=204, responses=AvatarResponses.responses())
async def update_or_create_avatar(
    user: AuthorizedUser,
    avatar: Annotated[UploadFile, File(description="image/webp")],
) -> None:
    if not filetype.match(avatar.file, [Webp()]):
        raise AvatarResponses.WRONG_FORMAT.value

    with user.avatar_path.open("wb") as file:
        file.write(await avatar.read())


@router.delete("/", status_code=204)
async def delete_avatar(user: AuthorizedUser) -> None:
    user.avatar_path.unlink(missing_ok=True)
