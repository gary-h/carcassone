from fastapi import APIRouter, HTTPException
from backend.storage.game_store import game_store

router = APIRouter()

@router.post("/create")
def create_game():
    game_id = game_store.create_game()
    return {"game_id": game_id}

@router.post("/{game_id}/join")
def join_game(game_id: str):
    game = game_store.get_game(game_id)
    if game is None:
        raise HTTPException(404, "Game not found")
    
    player_id = game_store.add_player(game_id)
    return {"player_id": player_id, "game": game}

@router.get("/{game_id}")
def get_game(game_id: str):
    game = game_store.get_game(game_id)
    if game is None:
        raise HTTPException(404, "Game not found")
    return game