from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import random
import time
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

waiting_player = None
rooms = {}
online_users = 0


@app.route("/")
def home():
    return render_template("index.html")


@socketio.on("connect")
def connect():
    global online_users
    online_users += 1
    emit("online_count", online_users, broadcast=True)


@socketio.on("disconnect")
def disconnect():
    global online_users
    online_users -= 1
    emit("online_count", online_users, broadcast=True)


@socketio.on("join_game")
def join_game():
    global waiting_player

    if waiting_player is None:
        waiting_player = request.sid
        emit("waiting")

        socketio.start_background_task(wait_for_player, request.sid)
    else:
        room = str(random.randint(1000, 9999))
        join_room(room)
        emit("game_start", {"room": room, "symbol": "X", "ai": False})
        waiting_player = None


def wait_for_player(player_id):
    time.sleep(2)
    if waiting_player == player_id:
        room = str(random.randint(1000, 9999))
        rooms[room] = ["","","","","","","","",""]
        socketio.emit("game_start",
                      {"room": room, "symbol": "X", "ai": True},
                      to=player_id)


@socketio.on("make_move")
def make_move(data):
    room = data["room"]
    index = data["index"]
    symbol = data["symbol"]

    if room not in rooms:
        rooms[room] = ["","","","","","","","",""]

    board = rooms[room]

    if board[index] == "":
        board[index] = symbol
        emit("update_board", {"board": board, "turn": "O" if symbol=="X" else "X"}, room=room)

        if data.get("ai"):
            socketio.start_background_task(ai_move, room)


def ai_move(room):
    time.sleep(1.5)
    board = rooms[room]

    empty = [i for i,v in enumerate(board) if v==""]
    if not empty:
        return

    move = random.choice(empty)
    board[move] = "O"

    socketio.emit("update_board",
                  {"board": board, "turn": "X"},
                  room=room)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0",
                 port=int(os.environ.get("PORT", 5000)))
