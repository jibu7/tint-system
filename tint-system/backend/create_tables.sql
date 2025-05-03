-- Create database (run this separately if you haven't created the database yet)
-- CREATE DATABASE tint_system;

-- Connect to the database
\c tinti-sys-db

-- Create formulations table
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

-- Create colorant_details table
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

-- Add indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_formulations_color_code ON formulations(color_code);
CREATE INDEX IF NOT EXISTS idx_colorant_details_formulation_id ON colorant_details(formulation_id);
