from sqlalchemy import create_engine, text
import sys
import os

# Update this with your database connection string
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://username:password@localhost/dbname')

def verify_rgb_data(color_code):
    """Verify RGB data exists for a color code directly in the database"""
    engine = create_engine(DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # Check formulations
            form_result = connection.execute(
                text(f"SELECT id, color_code, color_card FROM formulations WHERE color_code = :code"),
                {"code": color_code}
            )
            formulations = form_result.fetchall()
            
            print(f"Found {len(formulations)} formulations for color code '{color_code}'")
            
            # Check RGB values
            rgb_result = connection.execute(
                text(f"SELECT color_code, color_card, red, green, blue FROM color_rgb_values WHERE color_code = :code"),
                {"code": color_code}
            )
            rgb_values = rgb_result.fetchall()
            
            print(f"Found {len(rgb_values)} RGB values for color code '{color_code}'")
            
            # Check matches
            if formulations and rgb_values:
                print("\nChecking matches between formulations and RGB values:")
                form_cards = {row[2] for row in formulations if row[2]}  # color_card is at index 2
                rgb_cards = {row[1] for row in rgb_values}  # color_card is at index 1
                
                print(f"  Color cards in formulations: {form_cards}")
                print(f"  Color cards in RGB values: {rgb_cards}")
                
                matching_cards = form_cards.intersection(rgb_cards)
                print(f"\n  Matching color cards: {matching_cards}")
                print(f"  Cards in formulations but not in RGB: {form_cards - rgb_cards}")
                print(f"  Cards in RGB but not in formulations: {rgb_cards - form_cards}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        verify_rgb_data(sys.argv[1])
    else:
        print("Please provide a color code to verify")
        print("Usage: python verify_rgb_data.py <color_code>")
