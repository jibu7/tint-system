import asyncio
import os
import asyncpg
from dotenv import load_dotenv

async def test_connection():
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("Error: DATABASE_URL not found in .env file or environment variables.")
        return

    # Adjust URL for direct asyncpg.connect if it contains +asyncpg
    connect_url = database_url
    if "postgresql+asyncpg://" in connect_url:
        print("Adjusting DATABASE_URL for direct asyncpg.connect(): removing '+asyncpg'")
        connect_url = connect_url.replace("postgresql+asyncpg://", "postgresql://")
    
    target_db_address = connect_url.split('@')[-1]
    print(f"Attempting to connect to: {target_db_address}") # Mask credentials for printing

    if ".neon.tech" in target_db_address:
        print("This appears to be a Neon database connection.")
    elif "localhost" in target_db_address or "127.0.0.1" in target_db_address:
        print("This appears to be a local database connection.")
    else:
        print("Unable to determine if this is a Neon or local connection based on the address.")

    conn = None
    try:
        conn = await asyncpg.connect(connect_url) # Use the potentially modified connect_url
        print("Successfully connected to the database!")

        # Option 1: Fetch current server time (always works)
        server_time = await conn.fetchval("SELECT NOW();")
        print(f"Current database server time: {server_time}")

        # Option 2: Fetch data from one of your tables
        # !!! IMPORTANT: Replace 'your_actual_table_name' with a real table name from your database !!!
        table_to_check = "formulations" # <--- !!! REPLACE THIS with a table you expect to exist !!!
        # For example, if you have a 'users' table: table_to_check = "users"

        if table_to_check == "your_actual_table_name":
            print(f"\nINFO: To test data fetching, please edit this script and replace '{table_to_check}' with an actual table name.")
        else:
            print(f"\nAttempting to fetch data from '{table_to_check}'...")
            try:
                # Try to count rows in the specified table
                row_count = await conn.fetchval(f"SELECT COUNT(*) FROM {table_to_check};")
                print(f"Number of rows in '{table_to_check}': {row_count}")

                # Optionally, fetch a sample row
                # first_row = await conn.fetchrow(f"SELECT * FROM {table_to_check} LIMIT 1;")
                # if first_row:
                #     print(f"First row from '{table_to_check}': {dict(first_row)}")
                # else:
                #     print(f"Could not fetch any rows from '{table_to_check}' (it might be empty).")

            except asyncpg.exceptions.UndefinedTableError:
                print(f"Error: Table '{table_to_check}' does not exist in the connected database.")
            except Exception as e_query:
                print(f"Error querying '{table_to_check}': {e_query}")

    except ConnectionRefusedError:
        print("Connection Refused: Please check if the database server is running and accessible.")
    except asyncpg.exceptions.InvalidAuthorizationSpecificationError:
        print("Authentication Failed: Please check your database credentials in the DATABASE_URL.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            await conn.close()
            print("Connection closed.")

if __name__ == "__main__":
    asyncio.run(test_connection())
