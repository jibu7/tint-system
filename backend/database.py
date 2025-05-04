import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL environment variable set. Check your .env file.")

# echo=True prints SQL statements, useful for debugging, set to False for production
engine = create_async_engine(DATABASE_URL, echo=False)

# expire_on_commit=False prevents attributes from being expired after commit
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

# Dependency to get DB session in path operations
async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

# Function to create database tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Use ONLY for resetting during dev
        await conn.run_sync(Base.metadata.create_all)
    print("Database tables created or verified.")