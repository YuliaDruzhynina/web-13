from datetime import date, datetime, timedelta
from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from src.database.db import get_db
from src.entity.models import Contact, User
from src.schemas import ContactSchema
from src.services.auth import auth_service


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    contact = await db.execute(select(Contact).filter(Contact.email == body.email, Contact.user_id == user.id))
    existing_contact = contact.scalar_one_or_none()
    if existing_contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact already exists!")  
    contact = Contact(
        fullname=body.fullname,
        phone_number=body.phone_number,
        email=body.email,
        birthday=body.birthday,
        user=user,
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def get_all_contacts(limit: int, offset: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Contact).limit(limit).offset(offset)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact_by_id(
    limit: int, offset: int,    
    contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)
):
    stmt = select(Contact).filter(Contact.id == contact_id).limit(limit).offset(offset)
    result = await db.execute(stmt)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    contact = result.scalar_one_or_none()
    return contact


async def get_contact_by_fullname(limit: int, offset: int, contact_fullname: str, db: AsyncSession, user: User):
    stmt = select(Contact).filter(
        Contact.user_id == user.id, Contact.fullname == contact_fullname
    ).limit(limit).offset(offset)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    return contact


async def get_contact_by_email(limit: int, offset: int, contact_email: str, db: AsyncSession, user: User):
    stmt = select(Contact).filter(Contact.user == user, Contact.email == contact_email).limit(limit).offset(offset)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    return contact


async def get_upcoming_birthdays(db: AsyncSession, user: User ):
    current_date = date.today()
    future_date = current_date + timedelta(days=7)
    stmt = select(Contact).filter(current_date >= Contact.birthday, Contact.birthday <= future_date)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def get_upcoming_birthdays_from_new_date(
    new_date: str,      
    limit: int,
    offset: int,
    db: AsyncSession,
    user: User
) -> List[Contact]:
    new_date_obj = datetime.strptime(new_date, "%Y-%m-%d").date()
    future_date = new_date_obj + timedelta(days=7)
    stmt = select(Contact).filter(
        Contact.birthday >= new_date_obj, Contact.birthday <= future_date
    ).limit(limit).offset(offset)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def update_contact(
    body: ContactSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)
):
    stmt = select(Contact).filter(Contact.user_id == user.id, Contact.id == contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    contact.fullname = body.fullname
    contact.email = body.email
    contact.phone_number = body.phone_number
    contact.birthday = body.birthday
   
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(
    contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db)
):
    stmt = select(Contact).filter(Contact.id == contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    await db.delete(contact)
    await db.commit()
    return {"detail": "Contact deleted successfully"}
