import csv
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database import async_session, init_db

async def load_rgb_values():
    print("Initializing database...")
    try:
        # Initialize the database and create tables
        await init_db()
                
        async with async_session() as session:
            async with session.begin():
                # Create color_rgb_values table if it doesn't exist
                await session.execute(text("""
                CREATE TABLE IF NOT EXISTS color_rgb_values (
                    color_code VARCHAR(50),
                    color_card VARCHAR(50),
                    red INTEGER NOT NULL,
                    green INTEGER NOT NULL,
                    blue INTEGER NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (color_code, color_card)
                )
                """))
                
                print("Creating temporary table...")
                await session.execute(text("""
                CREATE TEMP TABLE temp_rgb_values (
                    color_card VARCHAR(50),
                    color_code VARCHAR(50),
                    red INTEGER,
                    green INTEGER,
                    blue INTEGER
                )
                """))
                
                print("Reading CSV file...")
                # Read and process CSV file
                with open('data/colorOG_deduplicated.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    batch_size = 1000
                    batch = []
                    row_count = 0
                    error_count = 0
                    
                    for row in reader:
                        try:
                            row_count += 1
                            color_code = row['color_card'].strip()  # Second column becomes color_code
                            color_card = row['color_code'].strip()  # First column becomes color_card
                            red = int(row['red'])
                            green = int(row['green'])
                            blue = int(row['blue'])
                            
                            # Add to batch
                            batch.append({
                                'color_card': color_card,
                                'color_code': color_code,
                                'red': red,
                                'green': green,
                                'blue': blue
                            })
                            
                            # Process batch if it reaches batch_size
                            if len(batch) >= batch_size:
                                print(f"Processing batch of {len(batch)} records...")
                                await session.execute(
                                    text("""
                                    INSERT INTO temp_rgb_values (color_card, color_code, red, green, blue)
                                    VALUES (:color_card, :color_code, :red, :green, :blue)
                                    """),
                                    batch
                                )
                                batch = []
                        
                        except (ValueError, KeyError) as e:
                            error_count += 1
                            print(f"Error processing row {row_count}: {row}. Error: {e}")
                            continue
                    
                    # Process any remaining records
                    if batch:
                        print(f"Processing final batch of {len(batch)} records...")
                        await session.execute(
                            text("""
                            INSERT INTO temp_rgb_values (color_card, color_code, red, green, blue)
                            VALUES (:color_card, :color_code, :red, :green, :blue)
                            """),
                            batch
                        )
                
                print("Copying data from temporary to permanent table...")
                # Insert from temporary table to actual table
                await session.execute(text("""
                INSERT INTO color_rgb_values (color_code, color_card, red, green, blue)
                SELECT color_code, color_card, red, green, blue
                FROM temp_rgb_values
                ON CONFLICT (color_code, color_card) DO NOTHING
                """))
                
                # Get counts
                result = await session.execute(text("SELECT COUNT(*) FROM temp_rgb_values"))
                temp_count = result.scalar()
                
                result = await session.execute(text("SELECT COUNT(*) FROM color_rgb_values"))
                final_count = result.scalar()
                
                print(f"Processed {temp_count} RGB values")
                print(f"Failed to process {error_count} rows")
                print(f"Final table contains {final_count} RGB values")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(load_rgb_values())
