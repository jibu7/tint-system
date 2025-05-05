#!/usr/bin/env python
"""
Script to import RGB values from CSV file into PostgreSQL database
"""

import os
import csv
import psycopg2
import argparse
from pathlib import Path
import io
import sys

def import_rgb_values(db_params, csv_file):
    """Import RGB values from CSV file into PostgreSQL database"""
    try:
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(**db_params)
        connection.autocommit = False
        cursor = connection.cursor()
        
        print(f"Connected to PostgreSQL database: {db_params['dbname']}")
        print(f"Processing CSV file: {csv_file}")
        
        # First, ensure the table exists using the create_color_rgb_table.sql
        sql_dir = Path(csv_file).parent.parent / 'sql'
        create_table_sql_path = sql_dir / 'create_color_rgb_table.sql'
        
        if os.path.exists(create_table_sql_path):
            print(f"Creating/verifying table schema from: {create_table_sql_path}")
            with open(create_table_sql_path, 'r') as f:
                create_table_sql = f.read()
                cursor.execute(create_table_sql)
                connection.commit()
        else:
            print(f"Warning: Table schema file not found: {create_table_sql_path}")
            print("Make sure the color_rgb_values table exists before importing data.")
        
        # Create temporary table
        cursor.execute("""
        CREATE TEMP TABLE temp_rgb_values (
            color_card VARCHAR(50),
            color_code VARCHAR(50),
            red INTEGER,
            green INTEGER,
            blue INTEGER
        )
        """)
        
        # Read and process CSV file
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            
            # Prepare data for insertion
            rows = []
            for row in reader:
                if len(row) >= 5:  # Ensure row has enough columns
                    try:
                        # Parse and validate values - SWAPPED order of color_code and color_card
                        color_code = row[0].strip()  # This was previously color_card
                        color_card = row[1].strip()  # This was previously color_code
                        red = int(row[2])
                        green = int(row[3])
                        blue = int(row[4])
                        
                        # Validate RGB values are in range 0-255
                        if 0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255:
                            rows.append((color_card, color_code, red, green, blue))
                        else:
                            print(f"Warning: Invalid RGB values in row: {row}")
                    except (ValueError, IndexError) as e:
                        print(f"Error processing row: {row}, Error: {e}")
            
            print(f"Processed {len(rows)} valid RGB entries from CSV")
            
            # Batch insert data into temp table in chunks of 1000
            chunk_size = 1000
            for i in range(0, len(rows), chunk_size):
                chunk = rows[i:i+chunk_size]
                args_str = ','.join(cursor.mogrify("(%s,%s,%s,%s,%s)", row).decode('utf-8') for row in chunk)
                if args_str:
                    cursor.execute(f"INSERT INTO temp_rgb_values (color_card, color_code, red, green, blue) VALUES {args_str}")
                    print(f"Inserted chunk {i//chunk_size + 1} ({len(chunk)} records)")
        
        # Insert data from temporary table into the actual table
        cursor.execute("""
        INSERT INTO public.color_rgb_values(color_card, color_code, red, green, blue)
        SELECT color_card, color_code, red, green, blue
        FROM temp_rgb_values
        ON CONFLICT (color_code, color_card) DO NOTHING
        """)
        
        # Get counts for reporting
        cursor.execute("SELECT COUNT(*) FROM temp_rgb_values")
        temp_count = cursor.fetchone()[0]
        
        # Get number of rows affected by last insert
        inserted_count = cursor.rowcount
        
        # Get total number of rows in the table
        cursor.execute("SELECT COUNT(*) FROM public.color_rgb_values")
        total_rows = cursor.fetchone()[0]
        
        # Commit the transaction
        connection.commit()
        
        print(f"\nRGB values imported successfully!")
        print(f"Processed {temp_count} records from CSV file")
        print(f"Inserted {inserted_count} new records")
        print(f"Total records in color_rgb_values table: {total_rows}")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error: {error}")
        if connection:
            connection.rollback()
            print("Transaction rolled back")
        sys.exit(1)
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("Database connection closed.")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Import RGB values from CSV to PostgreSQL")
    parser.add_argument('--host', default='localhost', help='Database host (default: localhost)')
    parser.add_argument('--port', type=int, default=5432, help='Database port (default: 5432)')
    parser.add_argument('--dbname', required=True, help='Database name')
    parser.add_argument('--user', required=True, help='Database user')
    parser.add_argument('--password', help='Database password')
    parser.add_argument('--csv-file', help='Path to CSV file (default: data/rgb_values.csv)')

    args = parser.parse_args()

    # Database connection parameters
    db_params = {
        'host': args.host,
        'port': args.port,
        'dbname': args.dbname,
        'user': args.user
    }
    
    # Add password only if provided
    if args.password:
        db_params['password'] = args.password

    # Path to CSV file
    csv_file = args.csv_file
    if not csv_file:
        # Default path
        current_dir = Path(__file__).parent
        csv_file = current_dir.parent / 'data' / 'rgb_values.csv'

    if not os.path.exists(csv_file):
        print(f"Error: CSV file not found at {csv_file}")
        return

    import_rgb_values(db_params, csv_file)

if __name__ == "__main__":
    main()
