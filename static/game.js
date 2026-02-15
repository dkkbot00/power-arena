const socket = io();
let room = null;
let symbol = null;
let board = [];
let turn = null;

const boardDiv = document.getElementById("board");
const statusDiv = document.getElementById("status");
const onlineDiv = document.getElementById("onlineCount");

const bgMusic = document.getElementById("bgMusic");
const clickSound = document.getElementById("clickSound");
const winSound = document.getElementById("winSound");
const loseSound = document.getElementById("loseSound");

document.body.addEventListener("click", ()=> bgMusic.play());

socket.on("connect", ()=> {
    socket.emit("join_game");
});

socket.on("online_count", (count)=>{
    onlineDiv.innerText = "🟢 Online: " + count;
});

socket.on("waiting", ()=>{
    statusDiv.innerText = "⏳ Matching...";
});

socket.on("game_start", (data)=>{
    room = data.room;
    symbol = data.symbol;
    board = ["","","","","","","","",""];
    turn = "X";
    statusDiv.innerText = symbol==="X"?"🟢 Your Turn":"⏳ Opponent Turn";
    drawBoard();
});

socket.on("update_board", (data)=>{
    board = data.board;
    turn = data.turn;
    drawBoard();

    if(data.winner){
        if(data.winner==="draw"){
            statusDiv.innerText="🤝 Draw!";
        }
        else if(data.winner===symbol){
            statusDiv.innerText="🎉 You Win!";
            winSound.play();
        }
        else{
            statusDiv.innerText="😢 You Lose!";
            loseSound.play();
        }

        setTimeout(()=>{
            socket.emit("join_game");
        },2000);
    }else{
        statusDiv.innerText = turn===symbol?"🟢 Your Turn":"⏳ Opponent Turn";
    }
});

function drawBoard(){
    boardDiv.innerHTML="";
    board.forEach((cell,i)=>{
        const div=document.createElement("div");
        div.classList.add("cell");
        if(cell) div.classList.add(cell);
        div.innerText=cell;
        div.onclick=()=>makeMove(i);
        boardDiv.appendChild(div);
    });
}

function makeMove(i){
    if(board[i]!==""||turn!==symbol) return;
    clickSound.play();
    socket.emit("make_move",{room,index:i,symbol});
    }
