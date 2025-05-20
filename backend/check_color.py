import asyncio
from sqlalchemy import select
from database import async_session
from models import Formulation

async def check_color_code(color_code: str):
    async with async_session() as session:
        # Query the database for the color code
        query = select(Formulation).where(Formulation.color_code == color_code)
        result = await session.execute(query)
        formulation = result.scalars().first()
        
        if formulation:
            print(f"Color code '{color_code}' exists in the database!")
            print(f"Details:")
            print(f"- Color Series: {formulation.color_series}")
            print(f"- Paint Type: {formulation.paint_type}")
            print(f"- Base Paint: {formulation.base_paint}")
        else:
            print(f"Color code '{color_code}' does not exist in the database.")

async def main():
    # Check for color code '0011P'
    await check_color_code('0011P')

if __name__ == "__main__":
    asyncio.run(main())
