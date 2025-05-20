from sqlalchemy import (
    Column, String, Float, Integer, ForeignKey, Index, UniqueConstraint, 
    TIMESTAMP, Numeric, ForeignKeyConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base  # Import Base from our database module

class Colorant(Base):
    __tablename__ = "colorants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)  # e.g., '6153-T'

    def __repr__(self):
        return f"<Colorant(id={self.id}, name='{self.name}')>"

class Formulation(Base):
    __tablename__ = "formulations"

    # Instead of a single primary key, we'll use a composite primary key
    color_code = Column(String(50), nullable=False, primary_key=True)      # H
    color_card = Column(String(100), nullable=False, primary_key=True)     # C
    paint_type = Column(String(100), nullable=False, primary_key=True)     # D
    base_paint = Column(String(100), nullable=False, primary_key=True)     # E
    packaging_spec = Column(String(100), nullable=False, primary_key=True) # G

    # Other non-key columns
    colorant_type = Column(String(100), nullable=False)      # A
    color_series = Column(String(100), nullable=False)       # B
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    colorant_details = relationship("ColorantDetail",
                                    back_populates="formulation",
                                    cascade="all, delete-orphan",
                                    lazy="selectin")  # Efficient loading strategy

    # Create indexes for better query performance
    __table_args__ = (
        Index('idx_formulation_search', color_code, paint_type, base_paint),
        Index('idx_color_card', color_card),
    )

    def __repr__(self):
        return f"<Formulation(id={self.id}, color_code='{self.color_code}', paint_type='{self.paint_type}', base_paint='{self.base_paint}')>"

class ColorantDetail(Base):
    __tablename__ = "colorant_details"

    id = Column(Integer, primary_key=True)
    # Reference to the parent formulation using composite foreign key
    color_code = Column(String(50), nullable=False)
    color_card = Column(String(100), nullable=False)
    paint_type = Column(String(100), nullable=False)
    base_paint = Column(String(100), nullable=False)
    packaging_spec = Column(String(100), nullable=False)
    
    colorant_name = Column(String(100), nullable=False)
    weight_g = Column(Numeric(12, 7), nullable=True)
    volume_ml = Column(Numeric(12, 7), nullable=True)

    formulation = relationship("Formulation", back_populates="colorant_details")

    __table_args__ = (
        ForeignKeyConstraint(
            ['color_code', 'color_card', 'paint_type', 'base_paint', 'packaging_spec'],
            ['formulations.color_code', 'formulations.color_card', 
             'formulations.paint_type', 'formulations.base_paint',
             'formulations.packaging_spec'],
            ondelete="CASCADE"
        ),
        Index('idx_colorant_formulation', color_code, color_card, paint_type, base_paint, packaging_spec),
    )
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ColorantDetail(color_code='{self.color_code}', colorant_name='{self.colorant_name}', weight={self.weight_g}g)>"

class ColorRgbValue(Base):
    __tablename__ = "color_rgb_values"

    color_code = Column(String(50), primary_key=True)
    color_card = Column(String(50), primary_key=True)
    red = Column(Integer, nullable=False)
    green = Column(Integer, nullable=False)
    blue = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        Index('idx_color_rgb_values_code_card', 'color_code', 'color_card'),  # Add index for faster lookups
    )

    def __repr__(self):
        return f"<ColorRgbValue(id={self.id}, color_code='{self.color_code}', color_card='{self.color_card}', rgb=({self.red},{self.green},{self.blue}))>"