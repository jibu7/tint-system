import pandas as pd
import os
from sqlalchemy.ext.asyncio import AsyncSession
from models import Formulation, ColorantDetail
from sqlalchemy import text
from decimal import Decimal

async def load_initial_data(session: AsyncSession):
    # Check if data already exists
    result = await session.execute(text("SELECT COUNT(*) FROM formulations"))
    count = result.scalar()
    
    if count > 0:
        print("Clearing existing data...")
        await session.execute(text("TRUNCATE TABLE colorant_details CASCADE"))
        await session.execute(text("TRUNCATE TABLE formulations CASCADE"))
        await session.commit()

    try:
        # Load color data from CSV
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'sekabiaoOG.csv')
        df = pd.read_csv(csv_path)
        
        # Group by color_code, paint_type, and base_paint to handle duplicates
        grouped = df.groupby(['H', 'D', 'E']).first().reset_index()
        
        # Keep track of processed formulations
        processed_formulations = {}

        # Process and insert data
        for _, row in df.iterrows():
            # Create a unique key for the formulation using all primary key fields
            formulation_key = (
                row['H'].strip(),  # color_code
                row['C'].strip(),  # color_card
                row['D'].strip(),  # paint_type
                row['E'].strip(),  # base_paint
                row['G'].strip()   # packaging_spec
            )
            
            # Only create new formulation if we haven't seen this combination before
            if formulation_key not in processed_formulations:
                formulation = Formulation(
                    color_code=formulation_key[0],
                    color_card=formulation_key[1],
                    paint_type=formulation_key[2],
                    base_paint=formulation_key[3],
                    packaging_spec=formulation_key[4],
                    colorant_type=row['A'].strip(),
                    color_series=row['B'].strip()
                )
                session.add(formulation)
                await session.flush()  # Get the formulation ID
                processed_formulations[formulation_key] = formulation
            else:
                formulation = processed_formulations[formulation_key]

            # Process colorant details
            # Handle up to 5 colorants (I,J,K through U,V,W)
            colorant_positions = [
                ('I', 'J', 'K'),  # Colorant 1
                ('L', 'M', 'N'),  # Colorant 2
                ('O', 'P', 'Q'),  # Colorant 3
                ('R', 'S', 'T'),  # Colorant 4
                ('U', 'V', 'W')   # Colorant 5
            ]

            existing_colorants = set()  # Track colorants we've already added
            
            for name_col, weight_col, volume_col in colorant_positions:
                if pd.notna(row[name_col]) and row[name_col] != '0' and row[name_col] != '':
                    colorant_name = row[name_col].strip()
                    
                    # Skip if we've already added this colorant
                    if colorant_name in existing_colorants:
                        continue
                        
                    weight = Decimal(str(row[weight_col])) if pd.notna(row[weight_col]) else None
                    volume = Decimal(str(row[volume_col])) if pd.notna(row[volume_col]) else None
                    
                    if weight == 0 and volume == 0:
                        continue

                    colorant_detail = ColorantDetail(
                        color_code=formulation.color_code,
                        color_card=formulation.color_card,
                        paint_type=formulation.paint_type,
                        base_paint=formulation.base_paint,
                        packaging_spec=formulation.packaging_spec,
                        colorant_name=colorant_name,
                        weight_g=weight,
                        volume_ml=volume
                    )
                    session.add(colorant_detail)
                    existing_colorants.add(colorant_name)

        await session.commit()
        print("Initial data loaded successfully")
        print(f"Loaded {len(processed_formulations)} unique formulations")
        
    except Exception as e:
        await session.rollback()
        print(f"Error loading initial data: {str(e)}")
        raise
