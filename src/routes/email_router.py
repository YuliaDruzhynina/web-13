
from fastapi import APIRouter, BackgroundTasks, Depends, Request, status, HTTPException, Response
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_mail.errors import ConnectionErrors

from src.conf.config import settings
from src.database.db import get_db
from src.schemas import EmailSchema, RequestEmail
from src.services.send_email import send_email
from src.repository import users as repositories_users
#from src.repository.users import get_user_by_email, confirmed_email
from src.services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME="goithw13",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=settings.TEMPLATE_FOLDER,
)   

router = APIRouter()
fm = FastMail(conf)

@router.post("/send-email")
async def send_in_background(background_tasks: BackgroundTasks, body: EmailSchema):
    try:
        token_verification = auth_service.create_email_token({"sub": body.email})
        message = MessageSchema(
            subject="Fastapi mail module",
            recipients=[body.email],
            template_body={"fullname": "Bill Murray", "host": "http://127.0.0.1:8000", "token": token_verification},
            subtype=MessageType.html
        )
        background_tasks.add_task(fm.send_message, message, template_name="email_template.html")
        return {"message": "Email has been sent"}
    except ConnectionErrors as err:
        print(f"Connection error: {err}")
        return {"error": "Failed to connect to the email server"}
    except Exception as e:
        print(f"General error: {e}")
        return {"error": "An unexpected error occurred"}

@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repositories_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    user = await repositories_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}

# @router.get('/{username}')
# async def request_email(username: str, response: Response, db: AsyncSession = Depends(get_db)):
#     print('--------------------------------')
#     print(f'{username} зберігаємо що він відкрив email в БД')
#     print('--------------------------------')
#     return FileResponse("src/static/open_check.png", media_type="image/png", content_disposition_type="inline")

