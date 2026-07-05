from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"

settings = Settings()
engine = create_async_engine(settings.database_url)
AsyncSessionLocal = async_sessionmaker(class_=AsyncSession,expire_on_commit=False,autoflush=False, bind=engine)

Base = declarative_base()

async def get_db():
    db = AsyncSessionLocal()
    try:
        yield db
    except Exception as e:
        await db.rollback()
        raise e
    finally:
        await db.close()