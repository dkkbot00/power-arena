let board = ["","","","","","","","",""];
let currentPlayer = "X";
let gameActive = true;

const boardDiv = document.getElementById("board");
const statusDiv = document.getElementById("status");

/* SOUND SYSTEM */

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

/* DRAW BOARD */

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

/* PLAYER MOVE */

function makeMove(i){
    if(!gameActive) return;
    if(board[i] !== "") return;

    if(!musicStarted){
        bgMusic.play();
        musicStarted = true;
    }

    clickSound.play();

    board[i] = "X";
    xSound.play();
    drawBoard();

    if(checkWinner("X")){
        statusDiv.innerText = "🥳 You Win!";
        winSound.play();
        gameActive = false;
        return;
    }

    if(board.includes("")){
        statusDiv.innerText = "AI Thinking...";
        setTimeout(aiMove,1500);
    }
}

/* HARD AI */

function aiMove(){
    if(!gameActive) return;

    let move = bestMove("O");
    if(move === null) move = bestMove("X");
    if(move === null){
        let empty = board.map((v,i)=>v===""?i:null).filter(v=>v!==null);
        move = empty[Math.floor(Math.random()*empty.length)];
    }

    board[move] = "O";
    oSound.play();
    drawBoard();

    if(checkWinner("O")){
        statusDiv.innerText = "😈 AI Wins!";
        loseSound.play();
        gameActive = false;
        return;
    }

    statusDiv.innerText = "Your Turn";
}

function bestMove(player){
    const wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ];

    for(let combo of wins){
        const [a,b,c] = combo;
        const values = [board[a], board[b], board[c]];
        if(values.filter(v=>v===player).length===2 && values.includes("")){
            return combo[values.indexOf("")];
        }
    }
    return null;
}

/* WIN CHECK */

function checkWinner(player){
    const wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ];

    return wins.some(([a,b,c]) =>
        board[a]===player && board[b]===player && board[c]===player
    );
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

drawBoard();
