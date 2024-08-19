from fastapi import APIRouter, Depends, UploadFile, File
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.entity.models import User
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserResponse

router = APIRouter()
cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
    )

@router.get("/me/", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    public_id = f"ImageStorage/{current_user.email}"
    print(f"Generated public_id: {public_id}")
    resource = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
    print(resource)
    src_url = cloudinary.CloudinaryImage(f'ImageStorage/{current_user.email}')\
                        .build_url(width=250, height=250, crop='fill', version=resource.get('version'))
    user = await repository_users.update_avatar_url(current_user.email, src_url, db)
    return user
