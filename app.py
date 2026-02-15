from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app, cors_allowed_origins="*")

waiting_player = None
online_users = 0
games = {}

@app.route("/")
def index():
    return render_template("index.html")


# Online counter
@socketio.on("connect")
def on_connect():
    global online_users
    online_users += 1
    socketio.emit("online_count", online_users)


@socketio.on("disconnect")
def on_disconnect():
    global online_users
    online_users -= 1
    socketio.emit("online_count", online_users)


# Join game
@socketio.on("join_game")
def join_game():

    global waiting_player

    sid = request.sid

    if waiting_player is None:
        waiting_player = sid
        emit("waiting")
    else:
        room = waiting_player + sid
        join_room(room)
        socketio.server.enter_room(sid, room)

        games[room] = {
            "board": [""] * 9,
            "turn": "X"
        }

        socketio.emit("game_start", {
            "room": room,
            "symbol": "X"
        }, room=waiting_player)

        socketio.emit("game_start", {
            "room": room,
            "symbol": "O"
        }, room=sid)

        waiting_player = None


# Move
@socketio.on("make_move")
def make_move(data):

    room = data["room"]
    index = data["index"]
    symbol = data["symbol"]

    game = games.get(room)

    if not game:
        return

    if game["board"][index] == "" and game["turn"] == symbol:
        game["board"][index] = symbol
        game["turn"] = "O" if symbol == "X" else "X"

        socketio.emit("update_board", {
            "board": game["board"],
            "turn": game["turn"]
        }, room=room)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
