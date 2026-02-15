let board = ["","","","","","","","",""];

const boardDiv = document.getElementById("board");

function drawBoard(){
    boardDiv.innerHTML = "";
    board.forEach((cell,i)=>{
        const div = document.createElement("div");
        div.classList.add("cell");
        div.innerText = cell;
        boardDiv.appendChild(div);
    });
}

drawBoard();
