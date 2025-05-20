#!/bin/bash
set -e

cd /home/wsl-jibu7/projects/tinting-system/backend 
export SYNC_DATABASE_URL="postgresql://postgres:@localhost:5432/paint_db?trust_auth=true"
export DATABASE_URL="postgresql+asyncpg://postgres:@localhost:5432/paint_db?trust_auth=true"
export PGPASSWORD=""

echo "Testing database connection..."
psql -h localhost -U postgres -d paint_db -c "SELECT 1" || { echo "Database connection failed"; exit 1; }

echo "Running Alembic migration..."
../venv/bin/alembic revision --autogenerate -m "Update formulation unique constraint and not-null fields"
