import pandas as pd
import os
from sqlalchemy.ext.asyncio import AsyncSession
from models import ColorRgbValue
from sqlalchemy import text

async def load_rgb_data(session: AsyncSession):
    # Check if RGB data already exists
    result = await session.execute(text("SELECT COUNT(*) FROM color_rgb_values"))
    count = result.scalar()
    
    if count > 0:
        print("RGB data already exists, skipping...")
        return

    try:
        # Load RGB data from CSV
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'colorOG_deduplicated.csv')
        df = pd.read_csv(csv_path)
        
        # Process and insert data
        for _, row in df.iterrows():
            rgb_value = ColorRgbValue(
                color_code=row['color_code'].strip(),
                color_card=row['color_card'].strip(),
                red=int(row['red']),
                green=int(row['green']),
                blue=int(row['blue'])
            )
            session.add(rgb_value)

        await session.commit()
        print("RGB data loaded successfully")
        
    except Exception as e:
        await session.rollback()
        print(f"Error loading RGB data: {str(e)}")
        raise
