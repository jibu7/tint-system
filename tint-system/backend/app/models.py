from app import db
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

class Formulation(db.Model):
    __tablename__ = 'formulations'
    
    id = db.Column(db.Integer, primary_key=True)
    color_code = db.Column(db.String(255), unique=True, nullable=False)
    colorant_type = db.Column(db.String(255))
    color_series = db.Column(db.String(255))
    color_card = db.Column(db.String(255))
    paint_type = db.Column(db.String(255))
    base_paint = db.Column(db.String(255))
    packaging_spec = db.Column(db.String(255))
    
    # Relationship with colorant details
    colorant_details = db.relationship('ColorantDetail', backref='formulation', lazy=True,
                                     cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Formulation {self.color_code}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'color_code': self.color_code,
            'colorant_type': self.colorant_type,
            'color_series': self.color_series,
            'color_card': self.color_card,
            'paint_type': self.paint_type,
            'base_paint': self.base_paint,
            'packaging_spec': self.packaging_spec,
            'colorants': [colorant.to_dict() for colorant in self.colorant_details]
        }

class ColorantDetail(db.Model):
    __tablename__ = 'colorant_details'
    
    id = db.Column(db.Integer, primary_key=True)
    formulation_id = db.Column(db.Integer, db.ForeignKey('formulations.id'), nullable=False)
    colorant_name = db.Column(db.String(255), nullable=False)
    weight_g = db.Column(db.Numeric(10, 5))
    volume_ml = db.Column(db.Numeric(10, 8))
    
    __table_args__ = (
        db.UniqueConstraint('formulation_id', 'colorant_name', name='uq_formulation_colorant'),
    )
    
    def __repr__(self):
        return f'<ColorantDetail {self.colorant_name} for {self.formulation_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'colorant_name': self.colorant_name,
            'weight_g': float(self.weight_g) if self.weight_g else None,
            'volume_ml': float(self.volume_ml) if self.volume_ml else None
        }

# Pydantic models for API request/response serialization

class ColorantDetailBase(BaseModel):
    """Pydantic model for colorant details in a formulation"""
    colorant_name: str
    weight_g: Optional[float] = Field(None, description="Weight in grams")
    volume_ml: Optional[float] = Field(None, description="Volume in milliliters")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "colorant_name": "BLACK",
                "weight_g": 12.5,
                "volume_ml": 10.75
            }
        }

class FormulationBase(BaseModel):
    """Base Pydantic model with common formulation attributes"""
    color_code: str
    color_series: Optional[str] = None
    color_card: Optional[str] = None
    colorant_type: Optional[str] = None
    paint_type: Optional[str] = None
    base_paint: Optional[str] = None
    packaging_spec: Optional[str] = None
    
    class Config:
        orm_mode = True

class FormulationDetail(FormulationBase):
    """Complete formulation model including colorant details for API responses"""
    id: int
    colorants: List[ColorantDetailBase]
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "color_code": "BC0001-4",
                "color_series": "Blue Collection",
                "color_card": "Designer Series",
                "colorant_type": "Universal",
                "paint_type": "Emulsion",
                "base_paint": "White Base",
                "packaging_spec": "1L",
                "colorants": [
                    {
                        "colorant_name": "BLACK",
                        "weight_g": 12.5,
                        "volume_ml": 10.75
                    },
                    {
                        "colorant_name": "BLUE",
                        "weight_g": 25.0,
                        "volume_ml": 22.5
                    }
                ]
            }
        }

class FormulationCreate(FormulationBase):
    """Pydantic model for creating a new formulation"""
    colorants: List[ColorantDetailBase]

class SearchResponse(BaseModel):
    """API response model for search results"""
    formulation: FormulationDetail