-- SQL script to load RGB values from CSV file into the color_rgb_values table
BEGIN;

-- Create a temporary table to hold the imported data
CREATE TEMP TABLE temp_rgb_values (
    color_card VARCHAR(50),
    color_code VARCHAR(50),
    red INTEGER,
    green INTEGER,
    blue INTEGER
);

-- Copy data from the CSV file into the temporary table
-- Note: When using psycopg2 to execute this script, the COPY command will need 
-- proper permissions or we can use the Python csv module to handle this instead.
-- The path will be resolved by the database server.
COPY temp_rgb_values(color_card, color_code, red, green, blue) 
FROM '/tmp/rgb_values.csv' 
WITH (FORMAT CSV, HEADER true, DELIMITER ',');

-- Insert data from temporary table into the actual table
-- This respects the schema with created_at and updated_at timestamps
INSERT INTO public.color_rgb_values(color_card, color_code, red, green, blue)
SELECT color_card, color_code, red, green, blue
FROM temp_rgb_values
ON CONFLICT (color_code, color_card) DO NOTHING;

-- Report the number of rows inserted
DO $$
DECLARE
    temp_count INTEGER;
    inserted_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO temp_count FROM temp_rgb_values;
    GET DIAGNOSTICS inserted_count = ROW_COUNT;
    RAISE NOTICE 'Imported % records from CSV. % new records inserted.', temp_count, inserted_count;
END $$;

-- Clean up the temporary table
DROP TABLE temp_rgb_values;

COMMIT;
