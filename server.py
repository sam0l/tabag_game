import socket
import threading
import random
import json

# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 5555))
server.listen()

games = {}  # {game_code: [player1_conn, player2_conn, game_state]}

def generate_code():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))

def handle_client(conn, addr, game_code):
    if game_code not in games:
        games[game_code] = [conn, None, {"balls": [{"x": 400, "y": 300, "dx": 7, "dy": 7}], "p1_y": 240, "p2_y": 240, "score1": 0, "score2": 0}]
        print(f"New game started with code: {game_code}")
    elif games[game_code][1] is None:
        games[game_code][1] = conn
        print(f"Player 2 joined game: {game_code}")
    else:
        conn.send(json.dumps({"type": "error", "msg": "Game full"}).encode())
        conn.close()
        return

    player_idx = 0 if games[game_code][0] == conn else 1
    opponent_idx = 1 - player_idx

    conn.send(json.dumps({"type": "start", "player": player_idx}).encode())

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                break
            msg = json.loads(data)
            game = games[game_code][2]

            if msg["type"] == "move":
                if player_idx == 0:
                    game["p1_y"] = msg["y"]
                else:
                    game["p2_y"] = msg["y"]

            # Send game state to both players
            for i, c in enumerate(games[game_code][:2]):
                if c:
                    c.send(json.dumps({"type": "update", "state": game, "player": i}).encode())
        except:
            break

    # Clean up
    if game_code in games:
        for c in games[game_code][:2]:
            if c and c != conn:
                c.send(json.dumps({"type": "error", "msg": "Opponent disconnected"}).encode())
        del games[game_code]
    conn.close()

print("Server running...")
while True:
    conn, addr = server.accept()
    game_code = conn.recv(1024).decode().strip()
    threading.Thread(target=handle_client, args=(conn, addr, game_code)).start()