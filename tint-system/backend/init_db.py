import psycopg2
import os
from dotenv import load_dotenv

def init_database():
    """Initialize the database with required tables"""
    load_dotenv()
    
    # Get database connection string from environment variable
    db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/tint_system")
    
    # Extract database name from connection string to check if it exists
    db_name = db_url.split('/')[-1]
    
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            db_url.replace(db_name, 'postgres')  # Connect to default db first
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if database exists, create if it doesn't
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if not cur.fetchone():
            print(f"Creating database '{db_name}'...")
            cur.execute(f"CREATE DATABASE {db_name}")
        
        # Close connection to postgres db
        cur.close()
        conn.close()
        
        # Connect to our actual database
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Create tables
        print("Creating tables...")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS formulations (
            id SERIAL PRIMARY KEY,
            color_code VARCHAR(50) UNIQUE NOT NULL,
            colorant_type VARCHAR(100),
            color_series VARCHAR(100),
            color_card VARCHAR(100),
            paint_type VARCHAR(100),
            base_paint VARCHAR(100),
            packaging_spec VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        cur.execute("""
        CREATE TABLE IF NOT EXISTS colorant_details (
            id SERIAL PRIMARY KEY,
            formulation_id INTEGER REFERENCES formulations(id) ON DELETE CASCADE,
            colorant_name VARCHAR(100) NOT NULL,
            weight_g DECIMAL(10,6),
            volume_ml DECIMAL(10,6),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            -- Ensure each colorant is only listed once per formulation
            UNIQUE (formulation_id, colorant_name)
        );
        """)
        
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_formulations_color_code ON formulations(color_code);
        """)
        
        cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_colorant_details_formulation_id ON colorant_details(formulation_id);
        """)
        
        print("Database setup complete!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    init_database()
