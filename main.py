# uvicorn main:app --host 127.0.0.1 --port 8000 --reload
#pip install -r requirements.txt
import re
from ipaddress import ip_address
from typing import Callable
from contextlib import asynccontextmanager
import sys
import os
import redis.asyncio as redis
from dotenv import load_dotenv
from fastapi import FastAPI, status, Request
from fastapi_limiter import FastAPILimiter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.routes.contact_router import router as contact_router
from src.routes.email_router import router as email_router
from src.routes.auth_router import router as auth_router
from src.routes.user_router import router as user_router

load_dotenv()# Загружаем переменные окружения до инициализации FastAP

@asynccontextmanager
async def lifespan(app: FastAPI):
    r = await redis.Redis(
        host="localhost", port=6379, db=0, encoding="utf-8", decode_responses=True
    )
    await FastAPILimiter.init(r)
    yield
    await r.close()


app = FastAPI(lifespan=lifespan)


app.include_router(contact_router, prefix="/contacts", tags=["contacts"])
app.include_router(email_router, prefix="/email", tags=["email"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(user_router, prefix="/user", tags=["user"])


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


banned_ips = [
    ip_address("192.168.1.1"),
    ip_address("192.168.1.2"),
    #ip_address("127.0.0.1"),  # hometest
]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # used as we have get token куки, авторизационных заголовков
    allow_methods=["*"],  # PUT,GET -   HTTP-методы
    allow_headers=["*"],  # "Autorization"
)

user_agent_ban_list = [
    r"Googlebot",
    r"Python-urllib",
]  # Список регулярных выражений-шаблон


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    ip = ip_address(request.client.host)
    if ip in banned_ips:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "You are banned"})
    #print(request.headers.get("Authorization")) # Вывод: Bearer your_access_token_here

    user_agent = request.headers.get("user-agent")
    #print(user_agent)
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You are banned"},
            )
    response = await call_next(request)
    return response


@app.get("/healthchecker")
async def root():
    return {"message": "Welcome to FastAPI!"}



# if __name__ == '__main__':
#     result=main()
#     import uvicorn
#     uvicorn.run(app, host=config.HOST, port=config)
