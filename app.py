import os
import random
import time
from threading import Timer
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'power-arena-secret'

socketio = SocketIO(app, cors_allowed_origins="*")

waiting_player = None
rooms = {}
online_users = 0


# ================== ROUTE ==================
@app.route("/")
def home():
    return render_template("index.html")


# ================== ONLINE COUNT ==================
@socketio.on("connect")
def handle_connect():
    global online_users
    online_users += 1
    emit("online_count", online_users, broadcast=True)


@socketio.on("disconnect")
def handle_disconnect():
    global online_users
    online_users -= 1
    emit("online_count", online_users, broadcast=True)


# ================== JOIN GAME ==================
@socketio.on("join_game")
def join_game():
    global waiting_player

    if waiting_player is None:
        waiting_player = request.sid
        emit("waiting")

        # 2 sec timer for AI fallback
        def start_ai():
            global waiting_player
            if waiting_player == request.sid:
                room = request.sid
                join_room(room)
                rooms[room] = {
                    "board": [""] * 9,
                    "turn": "X",
                    "ai": True
                }
                emit("game_start", {
                    "room": room,
                    "symbol": "X",
                    "ai": True
                })
                waiting_player = None

        Timer(2.0, start_ai).start()

    else:
        player1 = waiting_player
        player2 = request.sid
        room = player1 + player2

        join_room(room)
        socketio.emit("game_start", {
            "room": room,
            "symbol": "X",
            "ai": False
        }, room=player1)

        socketio.emit("game_start", {
            "room": room,
            "symbol": "O",
            "ai": False
        }, room=player2)

        rooms[room] = {
            "board": [""] * 9,
            "turn": "X",
            "ai": False
        }

        waiting_player = None


# ================== MOVE ==================
@socketio.on("make_move")
def make_move(data):
    room = data["room"]
    index = data["index"]
    symbol = data["symbol"]

    game = rooms.get(room)
    if not game:
        return

    if game["board"][index] != "":
        return

    if game["turn"] != symbol:
        return

    game["board"][index] = symbol
    game["turn"] = "O" if symbol == "X" else "X"

    socketio.emit("update_board", {
        "board": game["board"],
        "turn": game["turn"]
    }, room=room)

    # AI Move after 1.5 sec
    if game["ai"] and game["turn"] == "O":
        def ai_move():
            empty = [i for i, v in enumerate(game["board"]) if v == ""]
            if not empty:
                return
            move = random.choice(empty)
            game["board"][move] = "O"
            game["turn"] = "X"

            socketio.emit("update_board", {
                "board": game["board"],
                "turn": "X"
            }, room=room)

        Timer(1.5, ai_move).start()


# ================== RUN ==================
if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        allow_unsafe_werkzeug=True
    )
