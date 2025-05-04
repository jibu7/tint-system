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
         summary="Search Color Formula by Code",
         tags=["Color Search"])
async def search_color_code(color_code: str, db: AsyncSession = Depends(get_session)):
    """
    Retrieves details for a specific color code, including its required colorants,
    from the relational database structure.
    """
    try:
        async with db as session:
            # Log the query we're attempting
            print(f"Searching for color code: {color_code}")
            
            # Check if the Formulation table and model match
            print(f"Table name: {models.Formulation.__tablename__}")
            
            try:
                query = select(models.Formulation).where(models.Formulation.color_code == color_code)
                result = await session.execute(query)
                formulations = result.scalars().all()  # Get ALL matching formulations
                
                print(f"Found {len(formulations)} matching formulations")
            except Exception as db_error:
                print(f"Database query error: {str(db_error)}")
                raise HTTPException(status_code=500, 
                                   detail=f"Error querying formulations: {str(db_error)}")
            
            if not formulations:
                raise HTTPException(status_code=404, detail=f"Color code '{color_code}' not found.")
            
            # Return all formulations with their details
            response_data = []
            for formulation in formulations:
                try:
                    # Print formulation attributes to debug
                    print(f"Processing formulation ID: {formulation.id}, attributes: {vars(formulation)}")
                    
                    details_query = select(models.ColorantDetail).where(
                        models.ColorantDetail.formulation_id == formulation.id
                    )
                    details_result = await session.execute(details_query)
                    colorant_details = details_result.scalars().all()
                    
                    print(f"Found {len(colorant_details)} colorant details")
                    
                    # Extract data using a safer approach
                    formulation_data = {
                        "id": getattr(formulation, "id", None),
                        "color_code": getattr(formulation, "color_code", None),
                        "colorant_type": getattr(formulation, "colorant_type", None),
                        "color_series": getattr(formulation, "color_series", None),
                        "color_card": getattr(formulation, "color_card", None),
                        "paint_type": getattr(formulation, "paint_type", None),
                        "base_paint": getattr(formulation, "base_paint", None),
                        "packaging_spec": getattr(formulation, "packaging_spec", None),
                        "colorant_details": []
                    }
                    
                    # Process colorant details with safer approach
                    for detail in colorant_details:
                        detail_data = {
                            "colorant_name": getattr(detail, "colorant_name", None),
                            "weight_g": float(getattr(detail, "weight_g", 0)) if getattr(detail, "weight_g", None) else None,
                            "volume_ml": float(getattr(detail, "volume_ml", 0)) if getattr(detail, "volume_ml", None) else None
                        }
                        formulation_data["colorant_details"].append(detail_data)
                    
                    response_data.append(formulation_data)
                except Exception as e:
                    print(f"Error processing formulation {getattr(formulation, 'id', 'unknown')}: {str(e)}")
                    # Instead of skipping, include error info
                    error_data = {
                        "id": getattr(formulation, "id", None),
                        "color_code": getattr(formulation, "color_code", None),
                        "error": str(e)
                    }
                    response_data.append(error_data)
            
            return response_data
    except HTTPException:
        # Re-raise HTTP exceptions
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

@app.get("/api/verify-models", tags=["Health"])
async def verify_models():
    """Test endpoint to verify model names against database tables"""
    try:
        from sqlalchemy import inspect
        from database import engine_sync  # You may need to add a sync engine to your database.py
        
        inspector = inspect(engine_sync)
        tables = inspector.get_table_names()
        
        expected_tables = ["formulations", "colorant_details", "colorants"]
        missing_tables = [table for table in expected_tables if table not in tables]
        
        model_info = {
            "Available tables": tables,
            "Missing expected tables": missing_tables if missing_tables else "None",
            "Model mappings": {
                "Formulation": models.Formulation.__tablename__,
                "ColorantDetail": models.ColorantDetail.__tablename__
            }
        }
        
        return {
            "status": "ok" if not missing_tables else "warning",
            "message": "All models verified" if not missing_tables else "Some tables missing",
            "details": model_info
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error verifying models: {str(e)}"
        }

# --- To run the backend server: ---
# Activate virtual env: source venv/bin/activate
# Run: uvicorn main:app --reload --port 8000