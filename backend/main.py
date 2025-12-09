# backend/main.py

from fastapi import FastAPI

app = FastAPI(title="Carcassonne Backend")

from backend.api.games import router as games_router
from backend.api.moves import router as moves_router

app.include_router(games_router, prefix="/games", tags=["games"])
app.include_router(moves_router, prefix="/moves", tags=["moves"])