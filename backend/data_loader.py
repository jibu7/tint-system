import pandas as pd
import os
from sqlalchemy.ext.asyncio import AsyncSession
from models import Formulation, ColorantDetail
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text

async def load_initial_data(session: AsyncSession):
    # Check if data already exists
    result = await session.execute(text("SELECT COUNT(*) FROM formulations"))
    count = result.scalar()
    
    if count > 0:
        print("Data already exists in the database. Skipping initial load.")
        return

    try:
        # Load color data from CSV
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'colorOG_cleaned.csv')
        df = pd.read_csv(csv_path)

        # Process and insert data
        for _, row in df.iterrows():
            # Create formulation
            formulation = Formulation(
                color_code=row['color_code'].strip() if 'color_code' in row else None,
                paint_type=row['paint_type'].strip() if 'paint_type' in row else None,
                base_paint=row['base_paint'].strip() if 'base_paint' in row else None,
                colorant_type=row['colorant_type'].strip() if 'colorant_type' in row else None,
                color_series=row['color_series'].strip() if 'color_series' in row else None,
                color_card=row['color_card'].strip() if 'color_card' in row else None,
                packaging_spec=row['packaging_spec'].strip() if 'packaging_spec' in row else None,
            )
            session.add(formulation)
            await session.flush()  # Get the formulation ID

            # Add colorant details if they exist in the CSV
            colorant_columns = [col for col in df.columns if col.endswith('_weight') or col.endswith('_volume')]
            for col in colorant_columns:
                if pd.notna(row[col]) and float(row[col]) > 0:
                    colorant_name = col.replace('_weight', '').replace('_volume', '')
                    weight_col = f"{colorant_name}_weight"
                    volume_col = f"{colorant_name}_volume"
                    
                    colorant_detail = ColorantDetail(
                        formulation_id=formulation.id,
                        colorant_name=colorant_name,
                        weight_g=float(row[weight_col]) if weight_col in row and pd.notna(row[weight_col]) else None,
                        volume_ml=float(row[volume_col]) if volume_col in row and pd.notna(row[volume_col]) else None
                    )
                    session.add(colorant_detail)

        await session.commit()
        print("Initial data loaded successfully")
        
    except Exception as e:
        await session.rollback()
        print(f"Error loading initial data: {str(e)}")
        raise
