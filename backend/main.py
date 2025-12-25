from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.responses import FileResponse
from io import BytesIO
from PIL import Image

app = FastAPI()

from backend.api.games import router as games_router
app.include_router(games_router, prefix="/games", tags=["games"])

@app.get("/")
def display():
    # generate or load your PIL Image
    image_path = "board.png"  # path to your saved board
    return FileResponse(image_path, media_type="image/png")