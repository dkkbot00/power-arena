import os
import random
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'powerarena123'

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

waiting_player = None
online_users = 0
rooms = {}

@app.route("/")
def index():
    return render_template("index.html")

# =========================
# WIN CHECK
# =========================
def check_winner(board):
    patterns = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for p in patterns:
        a,b,c = p
        if board[a] and board[a]==board[b]==board[c]:
            return board[a]
    if "" not in board:
        return "Draw"
    return None

# =========================
# HARD AI
# =========================
def get_ai_move(board, ai, player):

    # 1. Win if possible
    for i in range(9):
        if board[i]=="":
            board[i]=ai
            if check_winner(board)==ai:
                board[i]=""
                return i
            board[i]=""

    # 2. Block player
    for i in range(9):
        if board[i]=="":
            board[i]=player
            if check_winner(board)==player:
                board[i]=""
                return i
            board[i]=""

    # 3. Center
    if board[4]=="":
        return 4

    # 4. Corners
    for i in [0,2,6,8]:
        if board[i]=="":
            return i

    # 5. Sides
    for i in [1,3,5,7]:
        if board[i]=="":
            return i

    return None

# =========================
# SOCKET EVENTS
# =========================

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

        socketio.sleep(2)

        if waiting_player == request.sid:
            room = request.sid
            join_room(room)

            rooms[room] = {
                "board": [""]*9,
                "turn": "X",
                "ai": True
            }

            emit("game_start", {"room":room,"symbol":"X","ai":True})
            waiting_player = None
    else:
        room = waiting_player
        join_room(room)
        join_room(request.sid)

        rooms[room] = {
            "board": [""]*9,
            "turn": "X",
            "ai": False
        }

        emit("game_start", {"room":room,"symbol":"X","ai":False}, room=room)
        emit("game_start", {"room":room,"symbol":"O","ai":False}, room=request.sid)

        waiting_player = None

@socketio.on("make_move")
def make_move(data):
    room = data["room"]
    index = data["index"]
    symbol = data["symbol"]

    game = rooms.get(room)
    if not game:
        return

    board = game["board"]

    if board[index]=="" and game["turn"]==symbol:
        board[index]=symbol
        game["turn"]="O" if symbol=="X" else "X"

        emit("update_board", {
            "board":board,
            "turn":game["turn"]
        }, room=room)

        winner = check_winner(board)

        if winner:
            emit("game_over", {"winner":winner}, room=room)
            return

        # AI Move
        if game["ai"] and game["turn"]=="O":
            socketio.sleep(1.5)

            ai_move = get_ai_move(board,"O","X")
            if ai_move is not None:
                board[ai_move]="O"
                game["turn"]="X"

                emit("update_board", {
                    "board":board,
                    "turn":"X"
                }, room=room)

                winner = check_winner(board)
                if winner:
                    emit("game_over", {"winner":winner}, room=room)

@socketio.on("restart_game")
def restart(data):
    room = data["room"]
    if room in rooms:
        rooms[room]["board"]=[""]*9
        rooms[room]["turn"]="X"
        emit("update_board", {
            "board":[""]*9,
            "turn":"X"
        }, room=room)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT",5000)))
