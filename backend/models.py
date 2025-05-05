from sqlalchemy import (
    Column, String, Float, Integer, ForeignKey, Index, UniqueConstraint, TIMESTAMP, Numeric
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

    id = Column(Integer, primary_key=True, index=True)
    color_code = Column(String(50), nullable=False, index=True)  # H - Removed unique=True, added index
    colorant_type = Column(String(100), nullable=True)       # A
    color_series = Column(String(100), nullable=True)        # B
    color_card = Column(String(100), nullable=True)          # C
    paint_type = Column(String(100), nullable=True, index=True) # D - Added index
    base_paint = Column(String(100), nullable=True, index=True) # E - Added index
    packaging_spec = Column(String(100), nullable=True)      # G
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    colorant_details = relationship("ColorantDetail",
                                    back_populates="formulation",
                                    cascade="all, delete-orphan",
                                    lazy="selectin")  # Efficient loading strategy

    __table_args__ = (
        UniqueConstraint('color_code', 'paint_type', 'base_paint', name='uq_formulation_key'),
    )

    def __repr__(self):
        return f"<Formulation(id={self.id}, color_code='{self.color_code}', paint_type='{self.paint_type}', base_paint='{self.base_paint}')>"

class ColorantDetail(Base):
    __tablename__ = "colorant_details"

    id = Column(Integer, primary_key=True, index=True)
    formulation_id = Column(Integer, ForeignKey("formulations.id", ondelete="CASCADE"), nullable=False, index=True)
    colorant_name = Column(String(100), nullable=False)
    weight_g = Column(Numeric(12, 7), nullable=True)
    volume_ml = Column(Numeric(12, 7), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    formulation = relationship("Formulation", back_populates="colorant_details")

    __table_args__ = (
        UniqueConstraint('formulation_id', 'colorant_name', name='colorant_details_formulation_id_colorant_name_key'),
        Index('idx_colorant_details_formulation_id', 'formulation_id'),
    )

    def __repr__(self):
        return f"<ColorantDetail(formulation_id={self.formulation_id}, colorant_name='{self.colorant_name}', weight={self.weight_g}g)>"