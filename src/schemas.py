
import datetime
#from typing import List, Optional
from pydantic import BaseModel, EmailStr


class ContactSchema(BaseModel):
    fullname: str
    email: EmailStr
    phone_number:str
    birthday: datetime.date
    #birthdate: str

    class Config:
        from_attributes = True


class ContactResponse(ContactSchema):
    id: int
   
    class Config:
        from_attributes = True 

        
class UserModel(BaseModel):
    username: str
    email: EmailStr
    password: str
    #refresh_token: Optional[str] = None
 
    class Config:
        from_attributes = True  

    
class UserResponse(BaseModel):
    detail: str = "User successfully created" 

    
class RequestEmail(BaseModel):
    email: EmailStr


class EmailSchema(BaseModel):
    email: EmailStr


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"