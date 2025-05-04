import csv
import asyncio
import logging
from sqlalchemy import select, delete, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session, init_db
from models import Formulation, ColorantDetail
from sqlalchemy.dialects.postgresql import insert as pg_insert

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CSV_FILE_PATH = 'sekabiao16.csv'

# Mapping based on the explanation provided
COLUMN_MAP = {
    'A': 'colorant_type', 'B': 'color_series', 'C': 'color_card',
    'D': 'paint_type', 'E': 'base_paint', 'G': 'packaging_spec',
    'H': 'color_code',
    # Colorant data grouped by the first letter of the group (name column)
    'I': {'name': 'I', 'weight': 'J', 'volume': 'K'},
    'L': {'name': 'L', 'weight': 'M', 'volume': 'N'},
    'O': {'name': 'O', 'weight': 'P', 'volume': 'Q'},
    'R': {'name': 'R', 'weight': 'S', 'volume': 'T'},
    'U': {'name': 'U', 'weight': 'V', 'volume': 'W'},
}
HEADER_TO_INDEX = {}

def safe_float_convert(value, default=0.0):
    if value is None or value.strip() == '':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert '{value}' to float, using default {default}")
        return default

async def load_data():
    logger.info("Initializing database schema...")
    await init_db()
    logger.info("Database schema initialized/verified.")
    
    # Skip clearing existing data to avoid losing existing records

    async with async_session() as session:
        async with session.begin():  # Start a transaction
            logger.info(f"Reading data from {CSV_FILE_PATH}...")
            processed_count = 0
            skipped_count = 0
            updated_count = 0
            
            try:
                with open(CSV_FILE_PATH, mode='r', encoding='utf-8') as infile:
                    reader = csv.reader(infile)
                    header = next(reader)
                    global HEADER_TO_INDEX
                    HEADER_TO_INDEX = {name: idx for idx, name in enumerate(header)}

                    if 'H' not in HEADER_TO_INDEX:
                        raise ValueError("CSV header is missing required 'H' column for color_code.")

                    batch_size = 100
                    current_batch = []
                    batch_count = 0

                    for i, row in enumerate(reader):
                        row_num = i + 2  # Adjust for 0-index and header
                        if not row or not any(field.strip() for field in row):
                            logger.warning(f"Skipping empty row {row_num}")
                            skipped_count += 1
                            continue

                        if len(row) < len(header):
                            logger.warning(f"Row {row_num} has fewer columns ({len(row)}) than header ({len(header)}). Padding with empty strings.")
                            row.extend([''] * (len(header) - len(row)))

                        color_code = row[HEADER_TO_INDEX['H']].strip()
                        if not color_code:
                            logger.warning(f"Skipping row {row_num} due to missing color_code.")
                            skipped_count += 1
                            continue

                        # Check if formulation already exists
                        existing_query = select(Formulation).filter(Formulation.color_code == color_code)
                        result = await session.execute(existing_query)
                        existing_formulation = result.scalars().first()
                        
                        # Prepare Formulation data
                        formulation_data = {'color_code': color_code}
                        for col_letter, field_name in COLUMN_MAP.items():
                            if isinstance(field_name, str) and col_letter in HEADER_TO_INDEX:
                                formulation_data[field_name] = row[HEADER_TO_INDEX[col_letter]].strip() or None
                            elif isinstance(field_name, dict):  # Skip colorant groups here
                                pass

                        # Prepare ColorantDetail data
                        colorant_details = []
                        for group_letter, col_map in COLUMN_MAP.items():
                            if not isinstance(col_map, dict):
                                continue  # Only process colorant groups

                            name_col = col_map['name']
                            weight_col = col_map['weight']
                            volume_col = col_map['volume']

                            if name_col not in HEADER_TO_INDEX or weight_col not in HEADER_TO_INDEX or volume_col not in HEADER_TO_INDEX:
                                logger.warning(f"Row {row_num}: Skipping colorant group '{group_letter}' due to missing columns in header.")
                                continue

                            colorant_name = row[HEADER_TO_INDEX[name_col]].strip()
                            if colorant_name:
                                weight_str = row[HEADER_TO_INDEX[weight_col]].strip()
                                volume_str = row[HEADER_TO_INDEX[volume_col]].strip()
                                weight = safe_float_convert(weight_str)
                                volume = safe_float_convert(volume_str)

                                if weight > 1e-9 or volume > 1e-9:  # Check against small threshold
                                    # Store colorant details
                                    colorant_details.append({
                                        'colorant_name': colorant_name,
                                        'weight_g': weight,
                                        'volume_ml': volume
                                    })
                        
                        if existing_formulation:
                            # Update existing formulation
                            for key, value in formulation_data.items():
                                setattr(existing_formulation, key, value)
                            
                            # Delete existing colorant details and create new ones
                            await session.execute(delete(ColorantDetail).where(
                                ColorantDetail.formulation_id == existing_formulation.id
                            ))
                            
                            # Create new colorant details
                            for detail in colorant_details:
                                new_detail = ColorantDetail(
                                    formulation_id=existing_formulation.id, 
                                    **detail
                                )
                                session.add(new_detail)
                            
                            updated_count += 1
                        else:
                            # Create new formulation
                            new_formulation = Formulation(**formulation_data)
                            new_formulation.colorant_details = [ColorantDetail(**detail) for detail in colorant_details]
                            session.add(new_formulation)
                            processed_count += 1
                        
                        # Commit in batches to avoid memory issues
                        if (processed_count + updated_count) % batch_size == 0:
                            await session.flush()
                            batch_count += 1
                            logger.info(f"Processed batch {batch_count} ({batch_size} records)")

                    # Final flush for any remaining records
                    await session.flush()
                    logger.info(f"Processed final batch")

            except FileNotFoundError:
                logger.error(f"Error: The file {CSV_FILE_PATH} was not found.")
                raise  # Re-raise to abort transaction
            except Exception as e:
                logger.error(f"An unexpected error occurred during data loading: {e}", exc_info=True)
                raise  # Re-raise to abort transaction

            # Commit the transaction if all rows processed without critical error
            logger.info(f"Committing transaction: {processed_count} formulations inserted, {updated_count} formulations updated, {skipped_count} rows skipped.")

    logger.info("Data loading finished.")


if __name__ == "__main__":
    logger.info("Starting data loading process...")
    # Run the init_db and data loading
    asyncio.run(load_data())
    logger.info("Data loading script execution complete.")