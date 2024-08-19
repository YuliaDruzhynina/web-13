
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    Security,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
 
from src.database.db import get_db, get_redis_client
from src.entity.models import User
from src.schemas import UserModel, TokenModel, UserResponse
from src.services.auth import auth_service
    
from src.services.send_email import send_email
#from src.repository.users import get_user_by_email, create_user, update_token
from src.repository import users as repositories_users
#from src.routes.email_router import send_in_background


router = APIRouter()

security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    exist_user = await repositories_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repositories_users.create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return new_user


@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await repositories_users.get_user_by_email(body.username, db)#по стандарту username(а ім можу буть і пошта)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):#чистый пароль сравниваем с хешем
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email, "test": "коза-дереза"})#это payload
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/refresh_token", response_model=TokenModel)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),#HTTPAuthorizationCredentials = Depends(get_refresh_token)
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials
    email = await auth_service.get_email_from_refresh_token(token)
    user = await repositories_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repositories_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
      
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    user.refresh_token = refresh_token
    await repositories_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/secret")
async def read_item(user: User = Depends(auth_service.get_current_user)):
    return {"message": 'secret router', "owner": user.email}

@router.post("/test_cache/set")
async def set_cache(key:str, value:str, redis_client: redis.Redis = Depends(get_redis_client)):
    await redis_client.set(key, value)

@router.get("/test_cache/get/{key}")
async def get_cache(key:str, redis_client: redis.Redis = Depends(get_redis_client)):
    value = await redis_client.get(key)  
    return {key: value}   