import asyncio
from sqlalchemy import text
from database import async_session

async def verify_rgb_data(color_code: str):
    """Verify RGB data exists for a color code directly in the database"""
    print(f"\nVerifying RGB data for color code: {color_code}")
    
    async with async_session() as session:
        # Check formulations
        result = await session.execute(
            text("SELECT id, color_code, color_card FROM formulations WHERE color_code = :code"),
            {"code": color_code}
        )
        formulations = result.fetchall()
        
        print(f"\nFound {len(formulations)} formulations for color code '{color_code}'")
        
        # Check RGB values
        result = await session.execute(
            text("SELECT color_code, color_card, red, green, blue FROM color_rgb_values WHERE color_code = :code"),
            {"code": color_code}
        )
        rgb_values = result.fetchall()
        
        print(f"Found {len(rgb_values)} RGB values for color code '{color_code}'")
        
        # Check matches
        if formulations and rgb_values:
            print("\nChecking matches between formulations and RGB values:")
            form_cards = {row[2] for row in formulations if row[2]}  # color_card is at index 2
            rgb_cards = {row[1] for row in rgb_values}  # color_card is at index 1
            
            print(f"  Color cards in formulations: {form_cards}")
            print(f"  Color cards in RGB values: {rgb_cards}")
            
            matching_cards = form_cards.intersection(rgb_cards)
            if matching_cards:
                print(f"\nMatching color cards: {matching_cards}")
                
                # Show the actual RGB values for matching cards
                for color_card in matching_cards:
                    rgb = next((r for r in rgb_values if r[1] == color_card), None)
                    if rgb:
                        print(f"\nRGB values for {color_card}:")
                        print(f"  R: {rgb[2]}, G: {rgb[3]}, B: {rgb[4]}")
            else:
                print("\nNo matching color cards found!")
            
            print(f"\nCards in formulations but not in RGB: {form_cards - rgb_cards}")
            print(f"Cards in RGB but not in formulations: {rgb_cards - form_cards}")
        elif not formulations:
            print("\nNo formulations found in database!")
        elif not rgb_values:
            print("\nNo RGB values found in database!")

async def main():
    await verify_rgb_data('0011P')

if __name__ == "__main__":
    asyncio.run(main())
