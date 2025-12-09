# backend/api/moves.py

from fastapi import APIRouter, HTTPException

from pydantic import BaseModel
from typing import List, Optional
from backend.storage.game_store import game_store
# from backend.core.game_rules import is_move_legal

router = APIRouter()

# TO DO: this is probably not intelligent to store this stuff here
class Move(BaseModel):
    player_id: str
    tile: str
    x: int
    y: int
    rotation: int = 0
    meeple: Optional[str] = None

def is_move_legal(game: dict, move: Move) -> bool:
    # TODO: check turn
    # TODO: check placement rules, tile matching, meeple rules...
    return True

# @router.post("/place_tile")
# async def place_tile():
#     # TO DO: implement placing tile logic
#     return {"status": "ok"}

@router.post("/{game_id}/submit")
def submit_move(game_id: str, move: Move):
    # TO DO: implement
    game = game_store.get_game(game_id)

    if not game:
        raise HTTPException(404, "Game not found")

    if not is_move_legal(game, move):
        raise HTTPException(400, "Not your turn or illegal move")

    # Apply move
    game["board"].append(move.dict())
    # Advance turn
    game["turn_index"] += 1

    return {"status": "ok", "game": game}