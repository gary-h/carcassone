from typing import Dict
from uuid import uuid4

class GameStore:
    def __init__(self):
        self.games: Dict[str, dict] = {}

    def create_game(self):
        game_id = uuid4().hex
        self.games[game_id] = {
            "players": [],
            "board": [],
            "turn_index": 0
        }
        return game_id

    def get_game(self, game_id):
        return self.games.get(game_id)

    def add_player(self, game_id):
        player_id = uuid4().hex[:6]
        game = self.games[game_id]
        game["players"].append(player_id)
        return player_id

game_store = GameStore()