from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
import json
import aioredis

from . import crud, models, database

app = FastAPI(title="Color Code Search API")

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Lifespan Events ---
@app.on_event("startup")
async def startup_event():
    await database.connect_db()

@app.on_event("shutdown")
async def shutdown_event():
    await database.disconnect_db()

# --- API Endpoints ---
@app.get("/api/search", response_model=models.FormulationDetail)
async def search_color_code(
    color_code: str = Query(..., description="The color code to search for (e.g., BC0001-4)"),
    redis: aioredis.Redis = Depends(database.get_redis)
):
    """
    Search for a paint formulation by its color code.
    Checks cache first, then queries the database.
    """
    cache_key = f"color_code:{color_code}"
    try:
        # 1. Check Cache
        cached_result = await redis.get(cache_key)
        if cached_result:
            print(f"Cache HIT for {color_code}")
            return models.FormulationDetail(**json.loads(cached_result))
    except aioredis.RedisError as e:
        print(f"Redis error on GET: {e}")  # Log error but continue to DB

    print(f"Cache MISS for {color_code}")
    # 2. Query Database
    db_result = await crud.get_formulation_by_color_code(color_code)
    
    if db_result is None:
        raise HTTPException(status_code=404, detail=f"Color code '{color_code}' not found.")

    # Convert DB result dict to Pydantic model instance
    formulation_detail = models.FormulationDetail(**db_result)

    try:
        # 3. Store in Cache (serialize Pydantic model to JSON string)
        await redis.set(cache_key, formulation_detail.json(), ex=3600)  # Cache for 1 hour
    except aioredis.RedisError as e:
        print(f"Redis error on SET: {e}")  # Log error but return data anyway

    return formulation_detail

@app.post("/api/formulations", response_model=models.FormulationDetail)
async def create_formulation(formulation: models.FormulationDetail):
    """
    Create a new formulation with its colorant details.
    """
    # Convert Pydantic model to dict for database insertion
    formulation_data = formulation.model_dump()
    result = await crud.create_formulation(formulation_data)
    
    if result is None:
        raise HTTPException(status_code=500, detail="Failed to create formulation")
    
    return models.FormulationDetail(**result)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Color Code Search API"}