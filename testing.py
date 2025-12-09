import requests
import time

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
player1 = requests.post(f"{BASE_URL}/games/{game_id}/join").json()["player_id"]
player2 = requests.post(f"{BASE_URL}/games/{game_id}/join").json()["player_id"]
players = [player1, player2]
print(f"Players joined: {players}")
# 3️⃣ Simulate turns

# Simple loop of 4 moves
for turn in range(4):
    print("starting turn")
    current_player = players[turn % len(players)]
    # setting placements to the turn so that they don't overlap, eventually will check the legality
    move_data = {
        "player_id": current_player,
        "tile": f"T{turn+1}",
        "x": turn,
        "y": turn,
        "rotation": 0
    }

    resp = requests.post(f"{BASE_URL}/moves/{game_id}/submit", json=move_data)

    if resp.status_code == 200:
        data = resp.json()
        print(f"Turn {turn+1}: Player {current_player} moved. Game state:")
        print(data["game"])
    else:
        try:
            error = resp.json()
        except Exception:
            error = {"error": "Invalid JSON", "raw_text": resp.text}

        print(f"Turn {turn+1}: Player {current_player} failed to move:", error)

    time.sleep(0.5)  # simulate small delay