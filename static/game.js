const socket = io();

let room=null;
let symbol=null;
let board=[];
let turn=null;

const boardDiv=document.getElementById("board");
const statusDiv=document.getElementById("status");
const onlineDiv=document.getElementById("onlineCount");
const bgMusic=document.getElementById("bgMusic");
const musicBtn=document.getElementById("musicBtn");

bgMusic.volume=0.2;
bgMusic.play();

musicBtn.onclick=()=>{
    if(bgMusic.paused){
        bgMusic.play();
        musicBtn.innerText="🔊";
    }else{
        bgMusic.pause();
        musicBtn.innerText="🔇";
    }
};

const soundX=new Audio("/static/x.mp3");
const soundO=new Audio("/static/o.mp3");
const winSound=new Audio("/static/win.mp3");
const loseSound=new Audio("/static/lose.mp3");

socket.on("connect",()=>{
    socket.emit("join_game");
});

socket.on("online_count",(c)=>{
    onlineDiv.innerText="🟢 Online: "+c;
});

socket.on("waiting",()=>{
    statusDiv.innerText="⏳ Waiting (2 sec)...";
});

socket.on("game_start",(data)=>{
    room=data.room;
    symbol=data.symbol;
    board=["","","","","","","","",""];
    turn="X";
    statusDiv.innerText="Game Started!";
    drawBoard();
});

socket.on("update_board",(data)=>{
    board=data.board;
    turn=data.turn;
    drawBoard();

    if(turn===symbol){
        statusDiv.innerText="🟢 Your Turn";
    }else{
        statusDiv.innerText="🔴 Opponent Turn";
    }
});

socket.on("game_over",(data)=>{
    if(data.winner==="Draw"){
        statusDiv.innerText="🤝 Draw!";
    }else if(data.winner===symbol){
        statusDiv.innerText="🏆 You Win!";
        winSound.play();
    }else{
        statusDiv.innerText="💀 You Lose!";
        loseSound.play();
    }

    setTimeout(()=>{
        socket.emit("restart_game",{room:room});
    },2000);
});

function drawBoard(){
    boardDiv.innerHTML="";
    board.forEach((cell,i)=>{
        const div=document.createElement("div");
        div.classList.add("cell");
        div.innerText=cell;
        div.onclick=()=>makeMove(i);
        boardDiv.appendChild(div);
    });
}

function makeMove(i){
    if(board[i]!==""||turn!==symbol)return;

    if(symbol==="X") soundX.play();
    if(symbol==="O") soundO.play();

    socket.emit("make_move",{
        room:room,
        index:i,
        symbol:symbol
    });
        }
