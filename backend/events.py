from fastapi import FastAPI
from .database import close_db

def setup_events(app: FastAPI):
    @app.on_event("shutdown")
    async def shutdown_event():
        await close_db()
