const socket = io();

let room = null;
let symbol = null;
let board = ["","","","","","","","",""];
let myTurn = false;

// Sounds
const bgMusic = new Audio("/static/bg.mp3");
const clickSound = new Audio("/static/click.mp3");
const xSound = new Audio("/static/x.mp3");
const oSound = new Audio("/static/o.mp3");
const winSound = new Audio("/static/win.mp3");
const loseSound = new Audio("/static/lose.mp3");

bgMusic.loop = true;
bgMusic.volume = 0.2;

const boardDiv = document.getElementById("board");
const statusDiv = document.getElementById("status");
const onlineDiv = document.getElementById("onlineCount");
const musicBtn = document.getElementById("musicToggle");

// Start bg music after first touch (mobile rule)
document.body.addEventListener("click", () => {
    bgMusic.play().catch(()=>{});
}, { once: true });

// Toggle music
musicBtn.onclick = () => {
    if (bgMusic.paused) {
        bgMusic.play();
        musicBtn.innerText = "🔊";
    } else {
        bgMusic.pause();
        musicBtn.innerText = "🔇";
    }
};

// Join
socket.on("connect", () => {
    socket.emit("join_game");
});

// Online
socket.on("online_count", (count) => {
    onlineDiv.innerText = "🟢 Online: " + count;
});

// Waiting
socket.on("waiting", () => {
    statusDiv.innerText = "⏳ Waiting for player...";
});

// Game Start
socket.on("game_start", (data) => {
    room = data.room;
    symbol = data.symbol;
    board = ["","","","","","","","",""];

    myTurn = (symbol === "X");

    statusDiv.innerText = myTurn ? "🟢 Your Turn" : "⏳ Opponent Turn";

    drawBoard();
});

// Update Board
socket.on("update_board", (data) => {

    // detect new move for sound
    for (let i = 0; i < 9; i++) {
        if (board[i] !== data.board[i] && data.board[i] !== "") {
            if (data.board[i] === "X") xSound.play();
            else oSound.play();
        }
    }

    board = data.board;
    myTurn = (data.turn === symbol);

    statusDiv.innerText = myTurn ? "🟢 Your Turn" : "⏳ Opponent Turn";

    drawBoard();
    checkWinner();
});

// Draw
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

// Move
function makeMove(i){

    if (!myTurn) return;
    if (board[i] !== "") return;

    clickSound.play();

    socket.emit("make_move", {
        room: room,
        index: i,
        symbol: symbol
    });
}

// Winner
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
                winSound.play();
            } else {
                statusDiv.innerText = "❌ You Lose!";
                loseSound.play();
            }

            setTimeout(() => {
                socket.emit("join_game");
            }, 2000);

            return;
        }
    }

    if (!board.includes("")) {
        statusDiv.innerText = "🤝 Draw!";
        setTimeout(() => {
            socket.emit("join_game");
        }, 2000);
    }
}
