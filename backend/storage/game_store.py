from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Set
from uuid import uuid4
from PIL import Image
from pathlib import Path
import random
import numpy as np

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

    def __init__(self, tile_img_directory, feature_map_directory):
        self.board: Dict[Tuple[int, int], TileInstance] = {}
        self.players = []
        self.turn = 0
        self.tile_images = {}
        self.feature_map_images = {}
        self.tile_size = (100,100) # should allow to set this automatically later on
        self.deck = []

        # add all images to a dictionary with key = tile name
        tile_dir = Path(tile_img_directory)
        for tile_path in tile_dir.glob("*.png"):
            tile_id = tile_path.stem  # filename without extension
            img = Image.open(tile_path).convert("RGBA")

            # Resize while keeping aspect ratio
            img.thumbnail(self.tile_size, Image.LANCZOS)
            self.tile_images[tile_id] = img

            # add this to the deck
            self.deck.append(tile_id)

        # same thing, but for the feature map images
        tile_dir = Path(feature_map_directory)
        for tile_path in tile_dir.glob("*.png"):
            tile_id = tile_path.stem  # filename without extension
            tile_id = tile_id[len("_feature_map_"):] # get rid of the prefix
            img = Image.open(tile_path).convert("RGBA")

            # Resize while keeping aspect ratio
            img.thumbnail(self.tile_size, Image.LANCZOS)
            self.feature_map_images[tile_id] = img

        random.shuffle(self.deck)

    # ---------- Board queries ----------

    def get_tile(self, pos: Tuple[int, int]) -> Optional[TileInstance]:
        return self.board.get(pos)

    def get_current_move(self):
        curr_tile = self.deck[-1]
        curr_player = self.players[self.turn % len(self.players)]
        return curr_tile, curr_player

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
            return Image.new("RGBA", (self.tile_size[0], self.tile_size[1]), (0,0,0,0))

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
            tile_img = self.tile_images[tile.file_name]

            # rotate tile according to tile.rotation
            if hasattr(tile, "rotation") and tile.rotation:
                tile_img = tile_img.rotate(tile.rotation * 90, expand=True)

            x = (c - min_col) * self.tile_size[0]
            y = (r - min_row) * self.tile_size[1]
            canvas.paste(tile_img, (x,y), tile_img)

        return canvas

    def check_borders(self, new_tile: TileInstance, tile_to_check: TileInstance, relative_loc: Tuple[int, int]) -> bool:
        img_a = self.feature_map_images[new_tile.file_name]
        img_a = img_a.rotate(new_tile.rotation * 90, expand=True)
        img_b = self.feature_map_images[tile_to_check.file_name]
        img_b = img_b.rotate(tile_to_check.rotation * 90, expand=True)

        img_a, img_b = np.asarray(img_a), np.asarray(img_b)

        threshold = 0.6

        h, w = img_a.shape[:2]

        dr, dc = relative_loc

        if (dr, dc) == (0, 1):          # new tile is RIGHT of existing
            edge_b = img_b[:, 0]       # left edge of new
            edge_a = img_a[:, -1]      # right edge of existing

        elif (dr, dc) == (0, -1):       # new tile is LEFT of existing
            edge_b = img_b[:, -1]
            edge_a = img_a[:, 0]

        elif (dr, dc) == (1, 0):        # new tile is BELOW existing
            edge_b = img_b[0, :]
            edge_a = img_a[-1, :]

        elif (dr, dc) == (-1, 0):       # new tile is ABOVE existing
            edge_b = img_b[-1, :]
            edge_a = img_a[0, :]

        else:
            raise ValueError(f"Invalid relative_loc: {relative_loc}")

        # pixel-wise comparison

        min_len = min(len(edge_a), len(edge_b))
        edge_a = edge_a[:min_len]
        edge_b = edge_b[:min_len]

        matches = np.all(edge_a == edge_b, axis=-1)
        match_ratio = matches.mean()

        return match_ratio >= threshold


    def check_placement(self, pos: Tuple[int, int], tile: TileInstance) -> bool:
        """
        Check if a tile fits legally at position `pos`
        by matching edges with neighbors.
        """

        # check all adjacent tiles
        adjacents = [(1,0), (-1,0), (0, 1), (0, -1)]

        empty = True

        for d in adjacents:
            loc = (pos[0] + d[0], pos[1] + d[1])

            if loc in self.board:
                empty = False

                if not self.check_borders(tile, self.board[loc], d):
                    return False

        if empty and self.turn > 0:
            return False

        return True

    def get_legal_placements(self, tile: TileInstance):
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

    def place_tile(self, pos: Tuple[int, int], rotation: int, player: str):
        """
        Place a tile on the board (assumes legality already checked).
        """
        new_tile = TileInstance(rotation = rotation, file_name = self.deck[-1])

        if pos in self.board:
            raise ValueError("Position already occupied")

        elif player != self.players[self.turn % len(self.players)]:
            raise ValueError("Not this player's turn")

        elif self.check_placement(pos, new_tile) == False:
            raise ValueError("Illegal placement")

        else:
            self.board[pos] = new_tile
            self.deck.pop()
            self.turn += 1

    # ---------- Debug ----------

    def __repr__(self):
        return f"<GameInstance tiles={len(self.board)}>"

class GameStore:
    def __init__(self):
        self.games: Dict[str, GameInstance] = dict()

    def create_game(self):
        game_id = uuid4().hex
        self.games[game_id] = GameInstance(tile_img_directory = "assets/tiles/", feature_map_directory= "assets/feature_maps/")
        return game_id

    def get_game(self, game_id):
        return self.games.get(game_id)

    def add_player(self, game_id):
        player_id = uuid4().hex[:6]
        game = self.games[game_id]
        game.players.append(player_id)
        return player_id

game_store = GameStore()