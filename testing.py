import requests
import time
from PIL import Image
from pathlib import Path

BASE_URL = "https://viviana-unfeminine-bedazzlingly.ngrok-free.dev"

# 1. Create a game
resp = requests.post(f"{BASE_URL}/games/create")
print("Create response status:", resp.status_code)
print("Raw response text:", resp.text)

if resp.status_code == 200:
    try:
        game_id = resp.json()["game_id"]
        print(f"Created game: {game_id}")
    except (ValueError, KeyError) as e:
        print("Error parsing JSON or missing 'game_id':", e)
        exit(1)
else:
    print("Failed to create game")
    exit(1)

# 2️⃣ Join two players
print(game_id)
player1 = requests.post(f"{BASE_URL}/games/{game_id}/join").json()["player_id"]
player2 = requests.post(f"{BASE_URL}/games/{game_id}/join").json()["player_id"]
players = [player1, player2]
print(f"Players joined: {players}")
# 3️⃣ Simulate turns

# Simple loop of 4 moves

predefined_tile_moves = ["city_cap_with_straight", "city_cap_with_straight", "separator", "triple_city"]

for turn in range(4):
    print("starting turn")

    resp = requests.get(f"{BASE_URL}/games/{game_id}/current_move").json()
    curr_player, curr_tile = resp['curr_player'], resp['curr_tile']
    print(f"current player: {curr_player}, current tile: {curr_tile}")

    current_player = players[(turn) % len(players)]
    # setting placements to the turn so that they don't overlap, eventually will check the legality
    move_data = {
        "pos": (turn,turn),
        "rotation": turn,
        "player": current_player
    }

    resp = requests.post(f"{BASE_URL}/games/{game_id}/move", json=move_data)

    if resp.status_code == 200:
        data = resp.json()
        print(f"Turn {turn}: Player {current_player} moved.")
    else:
        try:
            error = resp.json()
        except Exception:
            error = {"error": "Invalid JSON", "raw_text": resp.text}

        print(f"Turn {turn+1}: Player {current_player} failed to move:", error)

    time.sleep(0.5)  # simulate small delay

# get the final game
draw_successful = requests.get(f"{BASE_URL}/games/{game_id}/draw").json()["img_saved"]
print(f"draw succesful? {draw_successful}")
