import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv('../backend/.env')  # Load DB connection string

# --- Database Connection ---
DB_URL = "postgresql:///tinti-sys-db"  # Use peer authentication
conn = psycopg2.connect(DB_URL)
cur = conn.cursor()

# --- Load Data ---
try:
    # Get CSV file path
    csv_file = os.path.join(os.path.dirname(__file__), 'sekabiao16.csv')
    print(f"Reading data from {csv_file}")
    
    # Read the CSV file with explicit delimiter and encoding, skip the second row (descriptive names)
    df = pd.read_csv(csv_file, delimiter=',', encoding='utf-8', header=0, skiprows=[1])
    
    print(f"Loaded {len(df)} rows from CSV file")
    print(f"DataFrame columns: {df.columns.tolist()}")
    print("\nDataframe Info:")
    df.info()
    print("\nSample data (first 5 rows):")
    print(df.head())
    
    # --- Process and Insert ---
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    for index, row in df.iterrows():
        # Skip rows with missing color code
        if pd.isna(row['H']):
            print(f"Skipping row {index+1} due to missing color_code")
            skipped_count += 1
            continue

        color_code = str(row['H']).strip()
        
        try:
            # Insert into formulations table
            cur.execute(
                """
                INSERT INTO formulations (color_code, colorant_type, color_series, color_card, paint_type, base_paint, packaging_spec)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (color_code) DO NOTHING
                RETURNING id;
                """,
                (
                    color_code,
                    None if pd.isna(row['A']) else str(row['A']),  # colorant_type
                    None if pd.isna(row['B']) else str(row['B']),  # color_series
                    None if pd.isna(row['C']) else str(row['C']),  # color_card
                    None if pd.isna(row['D']) else str(row['D']),  # paint_type
                    None if pd.isna(row['E']) else str(row['E']),  # base_paint
                    None if pd.isna(row['G']) else str(row['G'])   # packaging_spec
                )
            )
            result = cur.fetchone()
            if result:
                formulation_id = result[0]
            else:
                # If conflict and DO NOTHING, fetch the existing ID
                cur.execute("SELECT id FROM formulations WHERE color_code = %s", (color_code,))
                formulation_id = cur.fetchone()[0]

            # Process colorant details - we have up to 5 colorants per formulation
            colorant_columns = [
                ('I', 'J', 'K'),   # (name_col, weight_col, volume_col)
                ('L', 'M', 'N'),
                ('O', 'P', 'Q'),
                ('R', 'S', 'T'),
                ('U', 'V', 'W')
            ]
            
            for name_col, weight_col, volume_col in colorant_columns:
                if name_col in df.columns and pd.notna(row[name_col]):
                    name = str(row[name_col]).strip()
                    
                    # Convert weight and volume to float, handling possible missing values
                    weight = pd.to_numeric(row.get(weight_col), errors='coerce') if weight_col in df.columns else None
                    volume = pd.to_numeric(row.get(volume_col), errors='coerce') if volume_col in df.columns else None
                    
                    if name:  # Only insert if colorant name exists
                        cur.execute(
                            """
                            INSERT INTO colorant_details (formulation_id, colorant_name, weight_g, volume_ml)
                            VALUES (%s, %s, %s, %s)
                            ON CONFLICT (formulation_id, colorant_name) DO UPDATE SET
                                weight_g = EXCLUDED.weight_g,
                                volume_ml = EXCLUDED.volume_ml;
                            """,
                            (formulation_id, name, weight, volume)
                        )

            conn.commit()  # Commit successful transaction
            processed_count += 1
            
            if processed_count % 50 == 0:
                print(f"Processed {processed_count} formulations...")
                
        except psycopg2.Error as e:
            conn.rollback()  # Rollback on database error
            print(f"Database error processing row {index+1} (Color Code: {color_code}): {e}")
            error_count += 1
        except Exception as e:
            conn.rollback()  # Rollback on any other error
            print(f"General error processing row {index+1} (Color Code: {color_code}): {e}")
            error_count += 1
    
    print(f"\nData loading summary:")
    print(f"- Total rows processed: {processed_count}")
    print(f"- Rows skipped: {skipped_count}")
    print(f"- Errors encountered: {error_count}")
            
except FileNotFoundError:
    print(f"Error: CSV file not found at {os.path.join(os.getcwd(), 'sekabiao16.csv')}")
except Exception as e:
    print(f"An error occurred during data loading: {e}")
finally:
    if 'cur' in locals() and cur:
        cur.close()
    if 'conn' in locals() and conn:
        conn.close()

print("Data loading script finished.")