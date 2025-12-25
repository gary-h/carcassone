# backend/api/moves.py

from fastapi import APIRouter, HTTPException

# from pydantic import BaseModel
# from typing import List, Optional
# from backend.storage.game_store import game_store
# # from backend.core.game_rules import is_move_legal

# router = APIRouter()


# # @router.post("/place_tile")
# # async def place_tile():
# #     # TO DO: implement placing tile logic
# #     return {"status": "ok"}

# @router.post("/{game_id}/submit")
# def submit_move(game_id: str, move: Move):
#     # TO DO: implement
#     game_instance = game_store.get_game(game_id)

#     if not game_instance :
#         raise HTTPException(404, "Game not found")

#     # Apply move
#     game_instance.append_move(move.dict())
#     # Advance turn
#     game_instance.increment_turn()

#     return {"status": "ok"}