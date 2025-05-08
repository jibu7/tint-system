import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file

DATABASE_URL_FROM_ENV = os.getenv("DATABASE_URL")

if not DATABASE_URL_FROM_ENV:
    raise ValueError("No DATABASE_URL environment variable set. Check your .env file.")

connect_args = {}
# The URL for SQLAlchemy's create_async_engine should retain the +asyncpg driver part
# e.g., "postgresql+asyncpg://user:pass@host/db"
processed_db_url = DATABASE_URL_FROM_ENV

# Handle sslmode: remove from URL string and add to connect_args for asyncpg
# This is to prevent sslmode=require from being passed as a kwarg to asyncpg.connect()
# by SQLAlchemy, and instead pass it as connect_args={'ssl': 'require'}
if "?sslmode=require" in processed_db_url:
    processed_db_url = processed_db_url.replace("?sslmode=require", "")
    connect_args["ssl"] = "require"
    print(f"INFO: Configuring SSL for asyncpg via connect_args. Original URL had ?sslmode=require. Processed URL: {processed_db_url}")
elif "&sslmode=require" in processed_db_url: # In case sslmode is not the first query param
    processed_db_url = processed_db_url.replace("&sslmode=require", "")
    connect_args["ssl"] = "require"
    print(f"INFO: Configuring SSL for asyncpg via connect_args. Original URL had &sslmode=require. Processed URL: {processed_db_url}")

# Ensure that if there are no query parameters left, the URL doesn't end with '?'
if processed_db_url.endswith("?"):
    processed_db_url = processed_db_url[:-1]

# echo=True prints SQL statements, useful for debugging, set to False for production
# Pass connect_args to create_async_engine
engine = create_async_engine(processed_db_url, echo=False, connect_args=connect_args)

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