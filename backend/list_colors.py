import asyncio
from sqlalchemy import select
from database import async_session
from models import Formulation

async def list_color_codes():
    print("Connecting to database...")
    async with async_session() as session:
        try:
            # First check if there are any rows in the table
            count_query = select(Formulation)
            count_result = await session.execute(count_query)
            all_formulations = count_result.scalars().all()
            print(f"Found {len(all_formulations)} total formulations")
            
            # Query the database for all color codes
            query = select(Formulation.color_code).distinct()
            result = await session.execute(query)
            color_codes = result.scalars().all()
            print("Query executed successfully")
            return color_codes
        except Exception as e:
            print(f"Error accessing database: {e}")
            return []
        
        if color_codes:
            print("Available color codes in the database:")
            for code in color_codes[:10]:  # Show first 10 codes
                print(f"- {code}")
            print(f"\nTotal number of color codes: {len(color_codes)}")
        else:
            print("No color codes found in the database.")

async def main():
    await list_color_codes()

if __name__ == "__main__":
    asyncio.run(main())
