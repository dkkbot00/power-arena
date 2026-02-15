from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import random
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'power-arena-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

online_count = 0
waiting_player = None
rooms = {}

# ================= ROUTE ================= #

@app.route("/")
def index():
    return render_template("index.html")

# ================= SOCKET ================= #

@socketio.on("connect")
def handle_connect():
    global online_count
    online_count += 1
    emit("online_count", online_count, broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    global online_count, waiting_player
    online_count -= 1
    emit("online_count", online_count, broadcast=True)

    if waiting_player == request.sid:
        waiting_player = None

# ================= MATCHMAKING ================= #

@socketio.on("join_game")
def handle_join():
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

        emit("game_start", {"room": room, "symbol": "O"})
        socketio.emit("game_start",
                      {"room": room, "symbol": "X"},
                      room=waiting_player)

        waiting_player = None

    else:
        waiting_player = sid
        emit("waiting")

        # 5 sec AI fallback
        threading.Thread(target=ai_fallback_timer, args=(sid,)).start()


def ai_fallback_timer(sid):
    global waiting_player

    time.sleep(5)

    if waiting_player == sid:
        room = f"ai_room_{sid}"
        rooms[room] = {
            "board": [""] * 9,
            "turn": "X",
            "ai": True
        }

        socketio.emit("game_start",
                      {"room": room, "symbol": "X", "ai": True},
                      room=sid)

        waiting_player = None

# ================= MOVE ================= #

@socketio.on("make_move")
def handle_move(data):
    room = data["room"]
    index = data["index"]
    symbol = data["symbol"]

    if room not in rooms:
        return

    game = rooms[room]

    if game["board"][index] == "" and game["turn"] == symbol:
        game["board"][index] = symbol
        game["turn"] = "O" if symbol == "X" else "X"

        socketio.emit("update_board",
                      {"board": game["board"], "turn": game["turn"]},
                      room=room)

        # AI Move
        if game["ai"] and game["turn"] == "O":
            time.sleep(1.5)
            ai_move(room)


def ai_move(room):
    game = rooms[room]
    board = game["board"]

    # Hard AI: try win
    move = best_move(board, "O")
    if move is None:
        move = best_move(board, "X")  # block
    if move is None:
        empty = [i for i in range(9) if board[i] == ""]
        move = random.choice(empty)

    board[move] = "O"
    game["turn"] = "X"

    socketio.emit("update_board",
                  {"board": board, "turn": "X"},
                  room=room)


def best_move(board, player):
    wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]

    for combo in wins:
        values = [board[i] for i in combo]
        if values.count(player) == 2 and values.count("") == 1:
            return combo[values.index("")]
    return None


# ================= RUN ================= #

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
