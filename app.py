@socketio.on("join_game")
def join_game():
    sid = request.sid

    emit("waiting")

    def start_ai():
        time.sleep(5)

        room = f"ai_{sid}"
        join_room(room)

        rooms[room] = [""] * 9

        socketio.emit("game_start", {
            "room": room,
            "symbol": "X",
            "ai": True
        }, room=sid)

    threading.Thread(target=start_ai).start()
