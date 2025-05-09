from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Represents a single colorant's details in the API response
class ColorantDetailBase(BaseModel):
    colorant_name: str
    weight_g: Optional[float] = None
    volume_ml: Optional[float] = None

class ColorantDetailCreate(ColorantDetailBase):
    pass

class ColorantDetailResponse(ColorantDetailBase):
    id: int
    formulation_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Represents formulation data for creation
class FormulationBase(BaseModel):
    color_code: str
    colorant_type: Optional[str] = None
    color_series: Optional[str] = None
    color_card: Optional[str] = None
    paint_type: Optional[str] = None
    base_paint: Optional[str] = None
    packaging_spec: Optional[str] = None

class FormulationCreate(FormulationBase):
    colorant_details: List[ColorantDetailCreate]

# Represents the full response for a color formula search
class FormulationResponse(FormulationBase):
    id: int
    colorant_details: List[ColorantDetailBase]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- RGB Schemas ---

class RgbColor(BaseModel):
    r: int
    g: int
    b: int

class ColorRgbValueBase(BaseModel):
    color_code: str
    color_card: str
    red: int
    green: int
    blue: int

class ColorRgbValueResponse(ColorRgbValueBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Updated Formulation Response to include RGB/HEX
class FormulationResponseWithColor(FormulationBase):
    id: int
    colorant_details: List[ColorantDetailBase]
    created_at: datetime
    updated_at: datetime
    color_rgb: Optional[dict] = None # Will contain {"rgb": RgbColor, "hex": str}

    class Config:
        from_attributes = True