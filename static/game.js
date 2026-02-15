const socket = io();

let room = null;
let symbol = null;
let board = [];
let turn = null;

const boardDiv = document.getElementById("board");
const statusDiv = document.getElementById("status");
const onlineDiv = document.getElementById("onlineCount");

socket.on("connect", () => {
    socket.emit("join_game");
});

socket.on("online_count", (count) => {
    onlineDiv.innerText = "🟢 Online: " + count;
});

socket.on("waiting", () => {
    statusDiv.innerText = "⏳ Waiting for player (5 sec)...";
});

socket.on("game_start", (data) => {
    room = data.room;
    symbol = data.symbol;
    board = ["","","","","","","","",""];
    turn = "X";
    statusDiv.innerText = data.ai ? "🤖 AI Mode" : "🎮 Multiplayer";
    drawBoard();
});

socket.on("update_board", (data) => {
    board = data.board;
    turn = data.turn;
    drawBoard();
});

function drawBoard(){
    boardDiv.innerHTML = "";
    board.forEach((cell,i)=>{
        const div = document.createElement("div");
        div.classList.add("cell");
        if(cell) div.classList.add(cell);
        div.innerText = cell;
        div.onclick = ()=>makeMove(i);
        boardDiv.appendChild(div);
    });
}

function makeMove(i){
    if(!room) return;
    if(board[i] !== "") return;
    if(turn !== symbol) return;

    socket.emit("make_move", {
        room: room,
        index: i,
        symbol: symbol
    });
}
