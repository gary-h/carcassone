from fastapi import APIRouter, HTTPException
from backend.storage.game_store import game_store
from PIL import Image
from pydantic import BaseModel


router = APIRouter()

class Move(BaseModel):
    tile_name: str
    pos: tuple[int, int]
    rotation: int = 0


@router.post("/create")
def create_game():
    game_id = game_store.create_game()
    return {"game_id": game_id}

@router.post("/{game_id}/join")
def join_game(game_id: str):
    if game_id is None:
        raise HTTPException(404, "Game not found")

    player_id = game_store.add_player(game_id)
    return {"player_id": player_id, "game": game_id}

@router.get("/{game_id}")
def get_game(game_id: str):
    game = game_store.get_game(game_id)
    if game is None:
        raise HTTPException(404, "Game not found")
    return {'game_id': game}

@router.get("/{game_id}/draw")
def draw_game(game_id: str):
    game = game_store.get_game(game_id)
    if game is None:
        raise HTTPException(404, "Game not found")
    gameboard_canvas = game.draw()
    gameboard_canvas.save("board.png")
    return {'img_saved': True}

@router.post("/{game_id}/move")
def place_tile(game_id: str, move: Move):
    game = game_store.get_game(game_id)
    if game is None:
        raise HTTPException(404, "Game not found")

    game.place_tile(
        pos=tuple(move.pos),
        tile_name=move.tile_name,
        rotation=move.rotation
    )

    return {"success": True}