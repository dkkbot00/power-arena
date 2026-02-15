from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

players_waiting = []
rooms = {}
online_count = 0

@app.route("/")
def index():
    return render_template("index.html")

@socketio.on("connect")
def handle_connect():
    global online_count
    online_count += 1
    emit("online_count", online_count, broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    global online_count
    online_count -= 1
    emit("online_count", online_count, broadcast=True)

@socketio.on("join_game")
def join_game():
    sid = request.sid

    if players_waiting:
        opponent = players_waiting.pop(0)
        room = f"room_{sid}_{opponent}"
        join_room(room)
        socketio.server.enter_room(opponent, room)
        rooms[room] = ["X", "O"]

        socketio.emit("start_game", {
            "room": room,
            "symbol": "X"
        }, room=opponent)

        emit("start_game", {
            "room": room,
            "symbol": "O"
        })
    else:
        players_waiting.append(sid)
        emit("waiting")

@socketio.on("move")
def handle_move(data):
    socketio.emit("move", data, room=data["room"])

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
