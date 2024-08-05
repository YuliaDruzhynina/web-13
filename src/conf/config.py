from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DB: str 
    POSTGRES_USER: str 
    POSTGRES_PASSWORD: str 
    POSTGRES_PORT: int 

    SQLALCHEMY_DATABASE_URL: str
    
    SECRET_KEY: str
    ALGORITHM: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    TEMPLATE_FOLDER: Path = Path(__file__).parent.parent / 'templates'

    REDIS_URL: str

  
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        from_attributes = True

settings = Settings()

