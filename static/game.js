const socket = io();

let room = null;
let symbol = null;
let board = [];
let turn = null;
let gameActive = true;

const boardDiv = document.getElementById("board");
const statusDiv = document.getElementById("status");
const onlineDiv = document.getElementById("onlineCount");

/* SOUND */

const bgMusic = new Audio("/static/bg.mp3");
bgMusic.loop = true;
bgMusic.volume = 0.15;

const xSound = new Audio("/static/x.mp3");
const oSound = new Audio("/static/o.mp3");
const winSound = new Audio("/static/win.mp3");
const loseSound = new Audio("/static/lose.mp3");
const clickSound = new Audio("/static/click.mp3");

let musicOn = true;
let musicStarted = false;

/* SOCKET */

socket.on("connect", () => {
    socket.emit("join_game");
});

socket.on("online_count", (count) => {
    onlineDiv.innerText = "🟢 Online: " + count;
});

socket.on("waiting", () => {
    statusDiv.innerText = "⏳ Waiting 5 sec...";
});

socket.on("game_start", (data) => {
    room = data.room;
    symbol = data.symbol;
    board = ["","","","","","","","",""];
    turn = "X";
    gameActive = true;
    statusDiv.innerText = data.ai ? "🤖 AI Mode" : "🎮 Multiplayer";
    drawBoard();
});

socket.on("update_board", (data) => {
    board = data.board;
    turn = data.turn;
    drawBoard();
    checkWinner();
});

/* DRAW */

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

/* MOVE */

function makeMove(i){
    if(!room || !gameActive) return;
    if(board[i] !== "") return;
    if(turn !== symbol) return;

    if(!musicStarted){
        bgMusic.play();
        musicStarted = true;
    }

    clickSound.play();

    socket.emit("make_move", {
        room: room,
        index: i,
        symbol: symbol
    });

    if(symbol === "X") xSound.play();
    else oSound.play();
}

/* WIN */

function checkWinner(){
    const wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ];

    for(let [a,b,c] of wins){
        if(board[a] && board[a] === board[b] && board[a] === board[c]){
            gameActive = false;

            if(board[a] === symbol){
                statusDiv.innerText = "🥳 You Win!";
                winSound.play();
            } else {
                statusDiv.innerText = "😈 You Lose!";
                loseSound.play();
            }

            setTimeout(restartGame, 2500);
            return;
        }
    }

    if(!board.includes("")){
        statusDiv.innerText = "Draw!";
        setTimeout(restartGame, 2000);
    }
}

function restartGame(){
    board = ["","","","","","","","",""];
    gameActive = true;
    statusDiv.innerText = "New Round!";
    drawBoard();
}

/* MUSIC TOGGLE */

document.getElementById("musicToggle").onclick = function(){
    if(musicOn){
        bgMusic.pause();
        this.innerText="🔇";
        musicOn=false;
    }else{
        bgMusic.play();
        this.innerText="🔊";
        musicOn=true;
    }
};
