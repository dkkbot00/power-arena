import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import random
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'powerarena123'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

online_users = 0
waiting_player = None
games = {}

# ------------------ ROUTE ------------------

@app.route("/")
def index():
    return render_template("index.html")


# ------------------ ONLINE COUNT ------------------

@socketio.on("connect")
def handle_connect():
    global online_users
    online_users += 1
    socketio.emit("online_count", online_users)


@socketio.on("disconnect")
def handle_disconnect():
    global online_users
    online_users -= 1
    socketio.emit("online_count", online_users)


# ------------------ JOIN GAME ------------------

@socketio.on("join_game")
def join_game():
    global waiting_player

    if waiting_player is None:
        waiting_player = request.sid
        emit("waiting")
        eventlet.sleep(2)

        # Agar 2 sec me match nahi mila → AI
        if waiting_player == request.sid:
            room = request.sid
            join_room(room)
            games[room] = {
                "board": [""] * 9,
                "turn": "X",
                "ai": True
            }
            waiting_player = None
            emit("game_start", {
                "room": room,
                "symbol": "X",
                "ai": True
            })
    else:
        room = waiting_player
        join_room(room)
        join_room(request.sid)

        games[room] = {
            "board": [""] * 9,
            "turn": "X",
            "ai": False,
            "players": {
                waiting_player: "X",
                request.sid: "O"
            }
        }

        socketio.emit("game_start", {
            "room": room,
            "symbol": "X",
            "ai": False
        }, room=waiting_player)

        emit("game_start", {
            "room": room,
            "symbol": "O",
            "ai": False
        })

        waiting_player = None


# ------------------ WIN CHECK ------------------

def check_winner(board):
    combos = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for a,b,c in combos:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if "" not in board:
        return "Draw"
    return None


# ------------------ HARD AI ------------------

def hard_ai_move(board):
    # 1. Win move
    for i in range(9):
        if board[i] == "":
            board[i] = "O"
            if check_winner(board) == "O":
                board[i] = ""
                return i
            board[i] = ""

    # 2. Block move
    for i in range(9):
        if board[i] == "":
            board[i] = "X"
            if check_winner(board) == "X":
                board[i] = ""
                return i
            board[i] = ""

    # 3. Center
    if board[4] == "":
        return 4

    # 4. Random
    empty = [i for i in range(9) if board[i] == ""]
    return random.choice(empty)


# ------------------ MAKE MOVE ------------------

@socketio.on("make_move")
def make_move(data):
    room = data["room"]
    index = data["index"]
    symbol = data["symbol"]

    game = games.get(room)
    if not game:
        return

    if game["board"][index] != "" or game["turn"] != symbol:
        return

    game["board"][index] = symbol
    game["turn"] = "O" if symbol == "X" else "X"

    winner = check_winner(game["board"])

    socketio.emit("update_board", {
        "board": game["board"],
        "turn": game["turn"]
    }, room=room)

    if winner:
        socketio.emit("game_over", winner, room=room)
        eventlet.sleep(2)
        games[room]["board"] = [""] * 9
        games[room]["turn"] = "X"
        socketio.emit("update_board", {
            "board": games[room]["board"],
            "turn": "X"
        }, room=room)
        return

    # AI MOVE
    if game.get("ai") and game["turn"] == "O":
        eventlet.sleep(1.5)
        ai_index = hard_ai_move(game["board"])
        game["board"][ai_index] = "O"
        game["turn"] = "X"

        winner = check_winner(game["board"])

        socketio.emit("update_board", {
            "board": game["board"],
            "turn": "X"
        }, room=room)

        if winner:
            socketio.emit("game_over", winner, room=room)
            eventlet.sleep(2)
            games[room]["board"] = [""] * 9
            games[room]["turn"] = "X"
            socketio.emit("update_board", {
                "board": games[room]["board"],
                "turn": "X"
            }, room=room)


# ------------------ RUN ------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
