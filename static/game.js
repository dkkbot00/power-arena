const socket = io();

let room = null;
let symbol = null;
let board = ["","","","","","","","",""];
let myTurn = false;

const boardDiv = document.getElementById("board");
const statusDiv = document.getElementById("status");
const onlineDiv = document.getElementById("onlineCount");

// Join game
socket.on("connect", () => {
    socket.emit("join_game");
});

// Online count
socket.on("online_count", (count) => {
    onlineDiv.innerText = "🟢 Online: " + count;
});

// Waiting
socket.on("waiting", () => {
    statusDiv.innerText = "⏳ Waiting for player...";
});

// Game start
socket.on("game_start", (data) => {
    room = data.room;
    symbol = data.symbol;
    board = ["","","","","","","","",""];

    myTurn = (symbol === "X"); // X always start

    statusDiv.innerText = myTurn ? "🟢 Your Turn" : "⏳ Opponent Turn";

    drawBoard();
});

// Board update
socket.on("update_board", (data) => {
    board = data.board;

    // Turn check
    myTurn = (data.turn === symbol);

    statusDiv.innerText = myTurn ? "🟢 Your Turn" : "⏳ Opponent Turn";

    drawBoard();

    checkWinner();
});

// Draw board
function drawBoard(){
    boardDiv.innerHTML = "";

    board.forEach((cell, i) => {
        const div = document.createElement("div");
        div.classList.add("cell");
        div.innerText = cell;
        div.onclick = () => makeMove(i);
        boardDiv.appendChild(div);
    });
}

// Click move
function makeMove(i){

    if (!myTurn) return;
    if (board[i] !== "") return;

    socket.emit("make_move", {
        room: room,
        index: i,
        symbol: symbol
    });
}

// Winner check
function checkWinner(){
    const winPatterns = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ];

    for (let pattern of winPatterns) {
        const [a,b,c] = pattern;
        if (board[a] && board[a] === board[b] && board[a] === board[c]) {

            if (board[a] === symbol) {
                statusDiv.innerText = "🏆 You Win!";
            } else {
                statusDiv.innerText = "❌ You Lose!";
            }

            setTimeout(() => {
                socket.emit("join_game");
            }, 2000);

            return;
        }
    }

    // Draw
    if (!board.includes("")) {
        statusDiv.innerText = "🤝 Draw!";
        setTimeout(() => {
            socket.emit("join_game");
        }, 2000);
    }
}
