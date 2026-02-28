from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("postgresql"):
    DATABASE_URL_ASYNC = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
else:
    DATABASE_URL_ASYNC = DATABASE_URL

async_engine = create_async_engine(
    DATABASE_URL_ASYNC,
    echo=settings.BACKEND_DEBUG,
    pool_pre_ping=True if DATABASE_URL.startswith("postgresql") else False,
    pool_size=10 if DATABASE_URL.startswith("postgresql") else 5,
    max_overflow=20 if DATABASE_URL.startswith("postgresql") else 10,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
