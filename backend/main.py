
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import router as corrections_router # Your router
from src.utils import init_db, engine # Your DB init
from src.models import Base # Your SQLAlchemy Base

# Optional: Create DB tables if they don't exist (for development)
# In production, you'd use migrations (e.g., Alembic)
# Base.metadata.create_all(bind=engine) # Or call init_db()
# init_db() # If you prefer your function

app = FastAPI(
    title="LLM Editor Backend",
    description="API for managing text corrections using LLM prompts.",
    version="0.1.0"
)

app.include_router(corrections_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Keep for local frontend development (if applicable)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to the LLM Editor API!"}