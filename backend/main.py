from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from typing import List
import os

import models
import schemas
from database import get_session

# Helper function to convert RGB to HEX
def rgb_to_hex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

app = FastAPI(title="Color Code Search API (Relational)")

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Add production frontend URL if available
production_frontend_url = os.getenv("FRONTEND_URL")
if production_frontend_url:
    origins.append(production_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],  # Ensure OPTIONS is allowed for preflight
    allow_headers=["*"],
)

@app.get("/api/search/{color_code}",
         response_model=List[schemas.FormulationResponseWithColor],
         summary="Search Color Formula by Code with RGB",
         tags=["Color Search"])
async def search_color_code(color_code: str, db: AsyncSession = Depends(get_session)):
    """
    Retrieves details for a specific color code, including its required colorants
    and RGB/HEX values, from the relational database structure.
    """
    try:
        async with db as session:
            print(f"Searching for color code: {color_code}")

            # Fetch formulations
            formulation_query = select(models.Formulation).where(models.Formulation.color_code == color_code)
            formulation_result = await session.execute(formulation_query)
            formulations = formulation_result.scalars().all()

            print(f"Found {len(formulations)} matching formulations")

            if not formulations:
                raise HTTPException(status_code=404, detail=f"Color code '{color_code}' not found.")

            response_data = []
            for formulation in formulations:
                try:
                    print(f"Processing formulation ID: {formulation.id}")

                    # Fetch colorant details for the current formulation
                    details_query = select(models.ColorantDetail).where(
                        models.ColorantDetail.formulation_id == formulation.id
                    )
                    details_result = await session.execute(details_query)
                    colorant_details = details_result.scalars().all()
                    print(f"Found {len(colorant_details)} colorant details for formulation {formulation.id}")

                    # Fetch RGB value for the current formulation's color code and card
                    rgb_data = None
                    if formulation.color_code and formulation.color_card:
                        rgb_query = select(models.ColorRgbValue).where(
                            models.ColorRgbValue.color_code == formulation.color_code,
                            models.ColorRgbValue.color_card == formulation.color_card
                        ).limit(1) # Expecting only one match per code/card combo
                        rgb_result = await session.execute(rgb_query)
                        color_rgb_value = rgb_result.scalar_one_or_none()

                        if color_rgb_value:
                            print(f"Found RGB data for {formulation.color_code} / {formulation.color_card}")
                            rgb_dict = schemas.RgbColor(r=color_rgb_value.red, g=color_rgb_value.green, b=color_rgb_value.blue)
                            hex_value = rgb_to_hex(color_rgb_value.red, color_rgb_value.green, color_rgb_value.blue)
                            rgb_data = {"rgb": rgb_dict.dict(), "hex": hex_value}
                        else:
                            print(f"No RGB data found for {formulation.color_code} / {formulation.color_card}")
                    else:
                         print(f"Skipping RGB lookup for formulation {formulation.id} due to missing color_code or color_card")


                    # Prepare formulation data including RGB
                    formulation_data = schemas.FormulationResponseWithColor(
                        id=formulation.id,
                        color_code=formulation.color_code,
                        colorant_type=formulation.colorant_type,
                        color_series=formulation.color_series,
                        color_card=formulation.color_card,
                        paint_type=formulation.paint_type,
                        base_paint=formulation.base_paint,
                        packaging_spec=formulation.packaging_spec,
                        created_at=formulation.created_at,
                        updated_at=formulation.updated_at,
                        colorant_details=[
                            schemas.ColorantDetailBase(
                                colorant_name=detail.colorant_name,
                                weight_g=float(detail.weight_g) if detail.weight_g is not None else None,
                                volume_ml=float(detail.volume_ml) if detail.volume_ml is not None else None
                            )
                            for detail in colorant_details
                        ],
                        color_rgb=rgb_data
                    )

                    response_data.append(formulation_data)

                except Exception as e:
                    print(f"Error processing formulation {getattr(formulation, 'id', 'unknown')}: {str(e)}")
                    pass

            return response_data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unhandled error in search_color_code: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

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

@app.get("/api/wakeup", tags=["Health"])
async def wakeup_db(db: AsyncSession = Depends(get_session)):
    """Pings the database to keep it awake."""
    try:
        async with db as session:
            await session.execute(text("SELECT 1"))
        return {"status": "db_woken_up"}
    except Exception as e:
        print(f"Error waking up DB: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not ping database")

@app.get("/api/verify-models", tags=["Health"])
async def verify_models(db: AsyncSession = Depends(get_session)): # Add db session dependency
    """Test endpoint to verify model names against database tables using async engine"""
    try:
        from sqlalchemy import inspect
        # Use db.run_sync for a safer approach with AsyncSession
        
        def get_tables_sync(conn):
            inspector = inspect(conn)
            return inspector.get_table_names()
        
        # Using run_sync on the session directly
        tables = await db.run_sync(get_tables_sync)

        expected_tables = ["formulations", "colorant_details", "colorants", "color_rgb_values"]
        missing_tables = [table for table in expected_tables if table not in tables]
        
        model_info = {
            "Available tables": tables,
            "Missing expected tables": missing_tables if missing_tables else "None",
            "Model mappings": {
                "Formulation": models.Formulation.__tablename__,
                "ColorantDetail": models.ColorantDetail.__tablename__,
                "ColorRgbValue": models.ColorRgbValue.__tablename__
            }
        }
        
        return {
            "status": "ok" if not missing_tables else "warning",
            "message": "All models verified" if not missing_tables else "Some tables missing",
            "details": model_info
        }
    except ImportError:
        return {
            "status": "error",
            "message": "Could not import 'engine_sync'. This endpoint needs review for async compatibility or a sync engine instance."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error verifying models: {str(e)}"
        }

# --- To run the backend server: ---
# Activate virtual env: source venv/bin/activate
# Run: uvicorn main:app --reload --port 8000