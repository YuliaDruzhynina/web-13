from fastapi import APIRouter, Depends, Path, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_limiter.depends import RateLimiter

# from typing import List
# import json
from src.database.db import get_db
from src.entity.models import User, Role
from src.schemas import ContactResponse, ContactSchema
from src.services.auth import auth_service
from src.repository import contacts as repository_contacts
from src.services.role import RoleAccess


router = APIRouter()
access_to_route_all = RoleAccess([Role.admin, Role.moderator])


@router.get("/")
def main_root():
    return {"message": "Hello, fastapi application!"}


@router.post(
    "/contacts/",
    response_model=ContactResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=5))],
)
async def create_contact(
    body: ContactSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    return await repository_contacts.create_contact(body, db, user)


@router.get("/contacts/open", response_model=list[ContactResponse])
async def get_contacts(
    limit: int = Query(default=10),
    offset: int = Query(default=0),
    db: AsyncSession = Depends(get_db),
):
    return await repository_contacts.get_contacts(limit, offset, db)


@router.get(
    "/contacts/all",
    response_model=list[ContactResponse],
    dependencies=[
        Depends(access_to_route_all),
        Depends(RateLimiter(times=1, seconds=20)),
    ],
)
async def get_all_contacts(
    limit: int = Query(default=10),
    offset: int = Query(default=0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    return await repository_contacts.get_all_contacts(limit, offset, db)


@router.get("/contacts/id/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(
    limit: int = Query(default=10),
    offset: int = Query(default=0),
    contact_id: int = Path(..., ge=1),
    db: AsyncSession = Depends(get_db),
):
    contact = await repository_contacts.get_contact_by_id(limit, offset, contact_id, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get("/contacts/by_name/{contact_fullname}", response_model=ContactResponse)
async def get_contact_by_fullname(
    limit: int = Query(default=10),
    offset: int = Query(default=0),
    contact_fullname: str = Path(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    contact = await repository_contacts.get_contact_by_fullname(
        limit, offset, contact_fullname, db, user
    )
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.get("/contacts/by_email/{contact_email}", response_model=ContactResponse)
async def get_contact_by_email(
    limit: int = Query(default=10),
    offset: int = Query(default=0),
    contact_email: str = Path(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    return await repository_contacts.get_contact_by_email(
        limit, offset, contact_email, db, user
    )


@router.get(
    "/contacts/by_birthday/{get_birthday}", response_model=list[ContactResponse]
)
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db)):
    return await repository_contacts.get_upcoming_birthdays(db)


@router.get("/contacts/get_new_day/{new_date}", response_model=list[ContactResponse])
async def get_upcoming_birthdays_from_new_date(
    limit: int = Query(default=10),
    offset: int = Query(default=0),
    new_date: str = Path(..., description="Current date in format YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
):
    return await repository_contacts.get_upcoming_birthdays_from_new_date(
        limit, offset, new_date, db
    )


@router.put("/contacts/update/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
    contact_id: int = Path(ge=1),
):
    contact = await repository_contacts.update_contact(body, db, user, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/contacts/delete/{contact_id}", response_model=dict)
async def delete_contact(
    contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)
):
    return await repository_contacts.delete_contact(contact_id, db)


# @router.get("/contacts", response_model=list[ContactResponse])
# async def get_contacts(
#     limit: int = Query(default=10),
#     offset: int = Query(default=0),
#     db: AsyncSession = Depends(get_db),
#     redis_client=Depends(get_redis_client)
# ):
#     cache_key = f"contacts:limit={limit}:offset={offset}"
#     данные из кэша
#     cached_data = await redis_client.get(cache_key)
#     if cached_data:
#         return json.loads(cached_data)
#     # Если данных нет в кэше, получите их из базы данных
#     contacts = await repository_contacts.get_contacts(limit=limit, offset=offset, db=db)
#     await redis_client.set(cache_key, ex=60)
#     return contacts
