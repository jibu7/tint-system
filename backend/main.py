from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

from database import get_session, init_db
from models import Formulation, ColorantDetail, ColorRgbValue

# Pydantic models for response
class ColorantDetailResponse(BaseModel):
    colorant_name: str
    weight_g: Optional[Decimal] = None
    volume_ml: Optional[Decimal] = None

    class Config:
        from_attributes = True

class RgbValueResponse(BaseModel):
    rgb: dict = {"r": 0, "g": 0, "b": 0}
    hex: str = "#000000"

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        return f"#{r:02x}{g:02x}{b:02x}"

    class Config:
        from_attributes = True

class FormulationResponse(BaseModel):
    color_code: str
    colorant_type: Optional[str] = None
    color_series: Optional[str] = None
    color_card: Optional[str] = None
    paint_type: Optional[str] = None
    base_paint: Optional[str] = None
    packaging_spec: Optional[str] = None
    colorant_details: List[ColorantDetailResponse]
    color_rgb: Optional[RgbValueResponse] = None

    class Config:
        from_attributes = True

# FastAPI instance
app = FastAPI(title="Paint Formulation API")

# CORS configuration
origins = [
    "http://localhost:3000",    # Next.js default port
    "http://localhost:8080",    # Alternative frontend port
    "http://127.0.0.1:3000",   # Next.js default port (alternative)
    "http://127.0.0.1:8080",   # Alternative frontend port (alternative)
    "http://localhost:5173",    # Vite default port
    "https://tinting-system-frontend.vercel.app",  # Production frontend
    "*"                        # Allow all origins in development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Paint Formulation API"}

@app.get("/api/formulation/{color_code}", response_model=List[FormulationResponse])
async def get_formulation(
    color_code: str,
    db: AsyncSession = Depends(get_session)
):
    """
    Get formulation details by color code.
    Returns colorant values and RGB color information if available.
    """
    # Query for formulation with RGB values
    query = (
        select(Formulation, ColorRgbValue)
        .outerjoin(
            ColorRgbValue,
            (Formulation.color_code == ColorRgbValue.color_code) &
            (Formulation.color_card == ColorRgbValue.color_card)
        )
        .where(Formulation.color_code == color_code)
    )

    result = await db.execute(query)
    rows = result.all()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No formulation found for color code: {color_code}"
        )

    # Prepare response
    response_data = []
    for formulation, rgb in rows:
        # Convert RGB values if available
        rgb_value = None
        if rgb:
            hex_color = RgbValueResponse.rgb_to_hex(rgb.red, rgb.green, rgb.blue)
            rgb_value = RgbValueResponse(
                rgb={"r": rgb.red, "g": rgb.green, "b": rgb.blue},
                hex=hex_color
            )

        # Create response object
        formulation_response = FormulationResponse(
            color_code=formulation.color_code,
            colorant_type=formulation.colorant_type,
            color_series=formulation.color_series,
            color_card=formulation.color_card,
            paint_type=formulation.paint_type,
            base_paint=formulation.base_paint,
            packaging_spec=formulation.packaging_spec,
            colorant_details=[
                ColorantDetailResponse(
                    colorant_name=detail.colorant_name,
                    weight_g=detail.weight_g,
                    volume_ml=detail.volume_ml
                ) for detail in formulation.colorant_details
            ],
            color_rgb=rgb_value
        )
        response_data.append(formulation_response)

    return response_data

@app.get("/api/search", response_model=List[FormulationResponse])
async def search_formulations(
    q: str,
    db: AsyncSession = Depends(get_session)
):
    """
    Search for formulations by color code.
    Supports partial matches and is case-insensitive.
    """
    query = (
        select(Formulation, ColorRgbValue)
        .outerjoin(
            ColorRgbValue,
            (Formulation.color_code == ColorRgbValue.color_code) &
            (Formulation.color_card == ColorRgbValue.color_card)
        )
        .where(Formulation.color_code.ilike(f"%{q}%"))
    )

    result = await db.execute(query)
    rows = result.all()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No formulations found matching: {q}"
        )

    # Prepare response using the same format as get_formulation
    response_data = []
    for formulation, rgb in rows:
        rgb_value = None
        if rgb:
            hex_color = RgbValueResponse.rgb_to_hex(rgb.red, rgb.green, rgb.blue)
            rgb_value = RgbValueResponse(
                rgb={"r": rgb.red, "g": rgb.green, "b": rgb.blue},
                hex=hex_color
            )

        formulation_response = FormulationResponse(
            color_code=formulation.color_code,
            colorant_type=formulation.colorant_type,
            color_series=formulation.color_series,
            color_card=formulation.color_card,
            paint_type=formulation.paint_type,
            base_paint=formulation.base_paint,
            packaging_spec=formulation.packaging_spec,
            colorant_details=[
                ColorantDetailResponse(
                    colorant_name=detail.colorant_name,
                    weight_g=detail.weight_g,
                    volume_ml=detail.volume_ml
                ) for detail in formulation.colorant_details
            ],
            color_rgb=rgb_value
        )
        response_data.append(formulation_response)

    return response_data