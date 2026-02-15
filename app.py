from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import threading
import time
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

online_users = 0
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
    global online_users
    online_users -= 1
    emit("online_count", online_users, broadcast=True)

# ---------------- MATCHMAKING ---------------- #

@socketio.on("join_game")
def join_game():
    sid = request.sid
    emit("waiting")

    def start_game():
        time.sleep(5)

        room = f"ai_{sid}"
        join_room(room)

        rooms[room] = {
            "board": [""] * 9,
            "turn": "X"
        }

        socketio.emit("game_start", {
            "room": room,
            "symbol": "X",
            "ai": True
        }, room=sid)

    threading.Thread(target=start_game).start()

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
        game["turn"] = "O"

        socketio.emit("update_board", {
            "board": board,
            "turn": "O"
        }, room=room)

        # AI MOVE
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

    socketio.emit("update_board", {
        "board": board,
        "turn": "X"
    }, room=room)

# ---------------- RUN ---------------- #

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
