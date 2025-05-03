from .database import database
from .models import FormulationDetail, ColorantDetail
from typing import Optional
import json

async def get_formulation_by_color_code(color_code: str) -> Optional[dict]:
    # Fetch formulation metadata
    query_formulation = "SELECT * FROM formulations WHERE color_code = :color_code"
    formulation_record = await database.fetch_one(query=query_formulation, values={"color_code": color_code})
    
    if not formulation_record:
        return None
    
    # Fetch associated colorant details
    query_colorants = """
        SELECT colorant_name, weight_g, volume_ml 
        FROM colorant_details 
        WHERE formulation_id = :formulation_id 
        ORDER BY colorant_name
    """
    colorant_records = await database.fetch_all(
        query=query_colorants, 
        values={"formulation_id": formulation_record["id"]}
    )
    
    # Combine results into a dictionary matching Pydantic models
    result = dict(formulation_record)
    result["colorants"] = [dict(c) for c in colorant_records]
    
    return result

async def create_formulation(formulation_data: dict) -> dict:
    # Start a transaction
    async with database.transaction():
        # Insert formulation
        colorants = formulation_data.pop("colorants", [])
        query = """
            INSERT INTO formulations (
                color_code, colorant_type, color_series, color_card,
                paint_type, base_paint, packaging_spec
            ) VALUES (
                :color_code, :colorant_type, :color_series, :color_card,
                :paint_type, :base_paint, :packaging_spec
            ) RETURNING id
        """
        formulation_id = await database.execute(query=query, values=formulation_data)
        
        # Insert colorants
        for colorant in colorants:
            query = """
                INSERT INTO colorant_details (
                    formulation_id, colorant_name, weight_g, volume_ml
                ) VALUES (
                    :formulation_id, :colorant_name, :weight_g, :volume_ml
                )
            """
            await database.execute(
                query=query,
                values={
                    "formulation_id": formulation_id,
                    "colorant_name": colorant["colorant_name"],
                    "weight_g": colorant.get("weight_g"),
                    "volume_ml": colorant.get("volume_ml")
                }
            )
        
        # Return the created formulation
        return await get_formulation_by_color_code(formulation_data["color_code"])