import os
import random
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret"

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

waiting_player = None
rooms = {}
online_users = 0

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def connect():
    global online_users
    online_users += 1
    socketio.emit("online_count", online_users)

@socketio.on("disconnect")
def disconnect():
    global online_users
    online_users -= 1
    socketio.emit("online_count", online_users)

@socketio.on("join_game")
def join_game():
    global waiting_player

    sid = request.sid

    if waiting_player is None:
        waiting_player = sid
        emit("waiting")
        socketio.sleep(2)

        if waiting_player == sid:
            room = sid
            join_room(room)
            rooms[room] = {
                "board": [""] * 9,
                "turn": "X",
                "ai": True
            }
            emit("game_start", {"symbol": "X", "room": room, "ai": True})
            waiting_player = None
    else:
        room = waiting_player
        join_room(room)
        join_room(sid)
        rooms[room] = {
            "board": [""] * 9,
            "turn": "X",
            "ai": False
        }
        socketio.emit("game_start", {"symbol": "X", "room": room, "ai": False}, room=room)
        emit("game_start", {"symbol": "O", "room": room, "ai": False})
        waiting_player = None

@socketio.on("make_move")
def make_move(data):
    room = data["room"]
    index = data["index"]
    symbol = data["symbol"]

    game = rooms.get(room)
    if not game:
        return

    if game["board"][index] == "":
        game["board"][index] = symbol
        game["turn"] = "O" if symbol == "X" else "X"

        socketio.emit("update_board", game, room=room)

        if game["ai"] and game["turn"] == "O":
            socketio.sleep(1.5)
            ai_move(room)

def ai_move(room):
    game = rooms.get(room)
    if not game:
        return

    empty = [i for i, v in enumerate(game["board"]) if v == ""]
    if empty:
        move = random.choice(empty)
        game["board"][move] = "O"
        game["turn"] = "X"
        socketio.emit("update_board", game, room=room)

if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
