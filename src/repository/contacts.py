from datetime import date, datetime, timedelta
from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.db import get_db
from src.entity.models import Contact, User
from src.schemas import ContactSchema


async def create_contact(body: ContactSchema, db: AsyncSession):
    contact = Contact(**body.model_dump(exclude_unset=True))
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def get_contacts(limit: int, offset: int, db: AsyncSession  = Depends(get_db)):
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact_by_id(contact_id: int = Path(ge=1), db: AsyncSession  = Depends(get_db)):
    stmt = select(Contact).filter_by(id=contact_id)
    result =  await db.execute(stmt)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    contact = result.scalar_one_or_none()
    return contact

async def get_contact_by_fullname(contact_fullname: str, db: AsyncSession, user: User):
    stmt = select(Contact).filter(Contact.user_id==user.id, Contact.fullname==contact_fullname)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    return contact

# async def get_contact_by_fullname(contact_fullname: str, db: AsyncSession, user: User):
#     stmt = select(Contact).filter(user=user, fullname=contact_fullname)
#     result = await db.execute(stmt)
#     contact = result.scalar_one_or_none()
#     return contact


async def get_contact_by_email(contact_email: str, db: AsyncSession, user: User):
    stmt = select(Contact).filter(Contact.user == user, Contact.email == contact_email)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    return contact


async def get_upcoming_birthdays(db: AsyncSession  = Depends(get_db)):
    current_date = date.today()
    future_date = current_date + timedelta(days=7)
    stmt = db.select(Contact).filter(current_date >= Contact.birthday, Contact.birthday <= future_date)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def get_upcoming_birthdays_from_new_date(new_date: str = Path(..., description="Current date in format YYYY-MM-DD"),db: AsyncSession  = Depends(get_db)):
    new_date_obj = datetime.strptime(new_date,"%Y-%m-%d").date()
    future_date = new_date_obj + timedelta(days=7)
    stmt = select(Contact).filter(Contact.birthday >= new_date_obj, Contact.birthday <= future_date)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1),db: AsyncSession  = Depends(get_db)):
    stmt = select(Contact).filter(id = contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    contact.fullname = body.fullname
    contact.email = body.email
    contact.phone_number = body.phone_number
    contact.birthday = body.birthday
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)):
    contact = await db.execute(select(Contact).filter_by(id=contact_id)).scalar_one_or_none()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact does not exist or you do not have permission to delete it.")
    await db.delete(contact)
    await db.commit()
    return contact
