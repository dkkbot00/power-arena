from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import threading
import time
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

online_users = 0
waiting_player = None
rooms = {}

@app.route("/")
def home():
    return render_template("index.html")

# ---------------- ONLINE COUNT ---------------- #

@socketio.on("connect")
def on_connect():
    global online_users
    online_users += 1
    emit("online_count", online_users, broadcast=True)

@socketio.on("disconnect")
def on_disconnect():
    global online_users, waiting_player
    online_users -= 1
    emit("online_count", online_users, broadcast=True)

    if waiting_player == request.sid:
        waiting_player = None

# ---------------- MATCHMAKING ---------------- #

@socketio.on("join_game")
def join_game():
    global waiting_player
    sid = request.sid

    if waiting_player and waiting_player != sid:
        room = f"room_{sid}_{waiting_player}"
        join_room(room)
        socketio.server.enter_room(waiting_player, room)

        rooms[room] = {
            "board": [""] * 9,
            "turn": "X",
            "ai": False
        }

        socketio.emit("game_start",
                      {"room": room, "symbol": "X", "ai": False},
                      room=waiting_player)

        emit("game_start",
             {"room": room, "symbol": "O", "ai": False})

        waiting_player = None

    else:
        waiting_player = sid
        emit("waiting")

        threading.Thread(target=ai_fallback, args=(sid,)).start()

def ai_fallback(sid):
    global waiting_player
    time.sleep(5)

    if waiting_player == sid:
        room = f"ai_{sid}"
        rooms[room] = {
            "board": [""] * 9,
            "turn": "X",
            "ai": True
        }

        socketio.emit("game_start",
                      {"room": room, "symbol": "X", "ai": True},
                      room=sid)

        waiting_player = None

# ---------------- MOVE ---------------- #

@socketio.on("make_move")
def make_move(data):
    room = data["room"]
    index = data["index"]
    symbol = data["symbol"]

    if room not in rooms:
        return

    game = rooms[room]
    board = game["board"]

    if board[index] == "" and game["turn"] == symbol:
        board[index] = symbol
        game["turn"] = "O" if symbol == "X" else "X"

        socketio.emit("update_board",
                      {"board": board, "turn": game["turn"]},
                      room=room)

        if game["ai"] and game["turn"] == "O":
            time.sleep(1.5)
            ai_move(room)

def ai_move(room):
    game = rooms[room]
    board = game["board"]

    empty = [i for i in range(9) if board[i] == ""]
    if not empty:
        return

    move = random.choice(empty)
    board[move] = "O"
    game["turn"] = "X"

    socketio.emit("update_board",
                  {"board": board, "turn": "X"},
                  room=room)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
