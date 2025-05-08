FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run migrations on startup
CMD ["sh", "-c", "alembic upgrade head && python start_prod.py"]
