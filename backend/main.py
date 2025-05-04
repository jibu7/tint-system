from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

import models
import schemas
from database import get_session

app = FastAPI(title="Color Code Search API (Relational)")

# Configure CORS
origins = [
    "http://localhost:3000", # Default Next.js dev port
    "http://127.0.0.1:3000",
    # Add your deployed frontend URL here if applicable
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"], # Only allow GET for this simple API
    allow_headers=["*"],
)

@app.get("/api/search/{color_code}",
         response_model=schemas.FormulationResponse,
         summary="Search Color Formula by Code",
         tags=["Color Search"])
async def search_color_code(color_code: str, db: AsyncSession = Depends(get_session)):
    """
    Retrieves details for a specific color code, including its required colorants,
    from the relational database structure.
    """
    # Query to find the formula and eagerly load related colorant details
    stmt = (
        select(models.Formulation)
        .where(models.Formulation.color_code == color_code)
        .options(selectinload(models.Formulation.colorant_details))
    )
    result = await db.execute(stmt)
    formulation = result.scalar_one_or_none() # Get a single result or None

    if formulation is None:
        raise HTTPException(status_code=404, detail=f"Color code '{color_code}' not found.")

    # The colorant_details are already loaded with the selectin strategy
    # from the relationship definition in the model

    return formulation

@app.get("/api/formulations", 
         response_model=List[schemas.FormulationBase],
         summary="List all formulations",
         tags=["Color Search"])
async def list_formulations(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_session)):
    """
    Retrieves a list of all color formulations with basic information.
    Supports pagination with skip and limit parameters.
    """
    stmt = (
        select(models.Formulation)
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    formulations = result.scalars().all()
    
    return formulations

@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    # Add DB connection check here if needed
    return {"status": "ok"}

# --- To run the backend server: ---
# Activate virtual env: source venv/bin/activate
# Run: uvicorn main:app --reload --port 8000