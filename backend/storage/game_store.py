from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Set
from uuid import uuid4
from PIL import Image
from pathlib import Path

OPPOSITE = {
    "N": "S",
    "S": "N",
    "E": "W",
    "W": "E",
}

DIRS = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
}

@dataclass(frozen=True)
class TileInstance:
    rotation: int  # 0,1,2,3
    file_name: str

    def rotated(self, rotation: int) -> "TileInstance":
        return TileInstance(
            rotation=(self.rotation + rotation) % 4,
            file_name=self.file_name
        )


# -----------------------------
# Game instance
# -----------------------------

class GameInstance:
    """
    Stores the current Carcassonne board state.
    Board coordinates are integer grid positions (x, y).
    """

    def __init__(self, tile_img_directory):
        self.board: Dict[Tuple[int, int], TileInstance] = {}
        self.players = []
        self.move_history = []
        self.turn = 0
        self.tile_images = {}
        self.tile_size = None


        tile_dir = Path(tile_img_directory)
        print(tile_dir)
        print("!!!")
        for tile_path in tile_dir.glob("*.png"):
            print(tile_path)
            tile_id = tile_path.stem  # filename without extension
            img = Image.open(tile_path).convert("RGBA")
            self.tile_images[tile_id] = img

            if self.tile_size is None:
                self.tile_size = img.size  # (width, height)


    # ---------- Board queries ----------

    def get_tile(self, pos: Tuple[int, int]) -> Optional[TileInstance]:
        return self.board.get(pos)

    def append_move(self, move):
        self.move_history.append(move)
        return

    def increment_turn(self):
        self.turn += 1
        return

    def occupied_positions(self) -> Set[Tuple[int, int]]:
        return set(self.board.keys())

    def open_positions(self) -> Set[Tuple[int, int]]:
        """
        Returns all empty positions adjacent to existing tiles.
        """
        if not self.board:
            return {(0, 0)}

        candidates = set()
        for (x, y) in self.board:
            for dx, dy in DIRS.values():
                pos = (x + dx, y + dy)
                if pos not in self.board:
                    candidates.add(pos)
        return candidates

    def draw(self):

        if not self.board:
            # Return an empty canvas or None
            return Image.new("RGBA", (tile_size, tile_size), (0,0,0,0))


        rows = [r for r, _ in self.board.keys()]
        cols = [c for _, c in self.board.keys()]
        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)

        width = (max_col - min_col + 1) * self.tile_size[0]
        height = (max_row - min_row + 1) * self.tile_size[1]
        canvas = Image.new("RGBA", (width, height), (0,0,0,0))

        for (r, c), tile in self.board.items():
            if tile is None:
                continue
            tile_img = self.tile_images[tile.file_name]  # assume TileInstance has tile_id
            x = (c - min_col) * self.tile_size[0]
            y = (r - min_row) * self.tile_size[1]
            canvas.paste(tile_img, (x, y), tile_img)

        return canvas

    # ---------- Placement logic ----------

    def fits(self, pos: Tuple[int, int], tile: TileInstance) -> bool:
        """
        Check if a tile fits legally at position `pos`
        by matching edges with neighbors.
        """
        x, y = pos
        for d, (dx, dy) in DIRS.items():
            neighbor = self.board.get((x + dx, y + dy))
            if neighbor:
                if tile.edges[d] != neighbor.edges[OPPOSITE[d]]:
                    return False
        return True

    def legal_placements(self, tile: TileInstance):
        """
        Enumerate all legal (pos, rotation) placements for a tile.
        """
        placements = []
        for pos in self.open_positions():
            for r in range(4):
                rotated = tile.rotated(r)
                if self.fits(pos, rotated):
                    placements.append((pos, rotated))
        return placements

    #def place_tile(self, pos: Tuple[int, int], tile: TileInstance):
    def place_tile(self, pos: Tuple[int, int], tile_name: str, rotation: int):
        """
        Place a tile on the board (assumes legality already checked).
        """
        new_tile = TileInstance(rotation = rotation, file_name = tile_name)

        if pos in self.board:
            raise ValueError("Position already occupied")

        if not self.fits(pos, new_tile):
            raise ValueError("Illegal placement")

        self.board[pos] = new_tile

    # ---------- Debug ----------

    def __repr__(self):
        return f"<GameInstance tiles={len(self.board)}>"

class GameStore:
    def __init__(self):
        self.games: Dict[str, GameInstance] = dict()

    def create_game(self):
        game_id = uuid4().hex
        self.games[game_id] = GameInstance(tile_img_directory = "assets/tiles/")
        return game_id

    def get_game(self, game_id):
        return self.games.get(game_id)

    def add_player(self, game_id):
        player_id = uuid4().hex[:6]
        game = self.games[game_id]
        game.players.append(player_id)
        return player_id

game_store = GameStore()