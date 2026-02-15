const socket = io({ transports:["websocket"] });

let room=null;
let symbol=null;
let board=[];

const boardDiv=document.getElementById("board");
const statusDiv=document.getElementById("status");
const onlineDiv=document.getElementById("onlineCount");
const bgMusic=document.getElementById("bgMusic");
const moveSound=document.getElementById("moveSound");

socket.on("connect",()=>{
    socket.emit("join_game");
});

socket.on("online_count",(c)=>{
    onlineDiv.innerText="🟢 Online: "+c;
});

socket.on("waiting",()=>{
    statusDiv.innerText="Waiting 2 sec...";
});

socket.on("game_start",(data)=>{
    room=data.room;
    symbol=data.symbol;
    board=["","","","","","","","",""];
    statusDiv.innerText=data.ai?"AI Mode":"Multiplayer";
    drawBoard();
    bgMusic.volume=0.2;
    bgMusic.play();
});

socket.on("update_board",(data)=>{
    board=data.board;
    drawBoard();
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
    if(board[i]!=="") return;

    moveSound.play();

    socket.emit("make_move",{
        room:room,
        index:i,
        symbol:symbol
    });
}
