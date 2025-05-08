import uvicorn
import os

if __name__ == "__main__":
    # Use environment variables or default to production settings
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    # Use multiple workers for better performance in production
    workers = int(os.getenv("WORKERS", "4"))
    
    uvicorn.run("main:app", host=host, port=port, workers=workers)
