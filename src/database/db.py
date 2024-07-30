from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.conf.config import settings


SQLALCHEMY_DATABASE_URL = (
    settings.SQLALCHEMY_DATABASE_URL
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# pip install asyncpg
# pip install sqlalchemy[asyncio]
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from src.conf.config import settings


#engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# SessionLocal = sessionmaker(
#     bind=engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
#     autocommit=False,
#     autoflush=False,
# )

# async def get_db():
#     async with SessionLocal() as session:
#         yield session

       
