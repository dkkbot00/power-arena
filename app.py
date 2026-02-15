from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import time
import threading
import random

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

online = 0
rooms = {}

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("connect")
def connect():
    global online
    online += 1
    emit("online_count", online, broadcast=True)

@socketio.on("disconnect")
def disconnect():
    global online
    online -= 1
    emit("online_count", online, broadcast=True)

@socketio.on("join_game")
def join_game():
    sid = request.sid
    emit("waiting")

    def start_ai():
        time.sleep(5)

        room = f"room_{sid}"
        join_room(room)

        rooms[room] = {
            "board": [""] * 9,
            "turn": "X"
        }

        socketio.emit("game_start", {
            "room": room,
            "symbol": "X"
        }, room=sid)

    threading.Thread(target=start_ai).start()

@socketio.on("make_move")
def make_move(data):
    room = data["room"]
    index = data["index"]
    symbol = data["symbol"]

    game = rooms.get(room)
    if not game:
        return

    board = game["board"]

    if board[index] == "" and game["turn"] == symbol:
        board[index] = symbol
        game["turn"] = "O"

        socketio.emit("update_board", {
            "board": board,
            "turn": "O"
        }, room=room)

        # AI move after 1.5 sec
        time.sleep(1.5)
        ai_move(room)

def ai_move(room):
    game = rooms.get(room)
    if not game:
        return

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

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
