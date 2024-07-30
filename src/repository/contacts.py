from datetime import date, datetime, timedelta
from fastapi import Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.entity.models import Contact, User
from src.schemas import ContactSchema

async def create_contact(body: ContactSchema, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(email=body.email).first()
    if contact:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact already exists!")
    contact=Contact(fullname=body.fullname, phone_number=body.phone_number, email=body.email, birthday =body.birthday)
    db.add(contact)
    db.commit()
    return contact


async def get_contacts(db: Session = Depends(get_db)):
    contacts = db.query(Contact).all()
    return contacts


async def get_contact_by_id(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id=contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


async def get_contact_by_fullname(contact_fullname: str, db: Session, user: User):
    return db.query(Contact).filter(Contact.user == user).filter(Contact.fullname == contact_fullname).first()


async def get_contact_by_email(contact_email: str, db: Session, user: User):
    return db.query(Contact).filter(Contact.user == user).filter(Contact.email == contact_email).first()


async def get_upcoming_birthdays(db: Session = Depends(get_db)):
    current_date = date.today()
    future_date = current_date + timedelta(days=7)
    contacts = db.query(Contact).filter(current_date >= Contact.birthday, Contact.birthday <= future_date).all()
    print(contacts)
    return contacts


async def get_upcoming_birthdays_from_new_date(new_date: str = Path(..., description="Current date in format YYYY-MM-DD"),db: Session = Depends(get_db)):
    new_date_obj = datetime.strptime(new_date,"%Y-%m-%d").date()
    future_date = new_date_obj + timedelta(days=7)
    contacts = db.query(Contact).filter(Contact.birthday >= new_date_obj, Contact.birthday <= future_date).all()
    print(contacts)
    return contacts


async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1),db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id = contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    contact.fullname = body.fullname
    contact.email = body.email
    contact.phone_number = body.phone_number
    contact.birthday = body.birthday
    db.commit()
    return contact


async def delete_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter_by(id = contact_id).first()
    if contact is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Contact does not exist or you do not have permission to delete it.")
    db.delete(contact)
    db.commit()
    return contact