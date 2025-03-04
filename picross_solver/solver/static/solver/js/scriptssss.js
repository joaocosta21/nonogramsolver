function generateGrid() {
    const width = parseInt(document.getElementById("width").value);
    const height = parseInt(document.getElementById("height").value);
    const grid = document.getElementById("grid");
    const topHints = document.getElementById("top-hints");
    const sideHints = document.getElementById("side-hints");
    
    grid.innerHTML = "";
    topHints.innerHTML = "";
    sideHints.innerHTML = "";
    
    // Set grid dimensions
    grid.style.gridTemplateColumns = `repeat(${width}, 30px)`;
    grid.style.gridTemplateRows = `repeat(${height}, 30px)`;
    topHints.style.setProperty('--grid-width', width); // Set CSS variable for top hints
    
    // Calculate the number of hint inputs needed per row/column
    const maxRowHints = Math.ceil(width / 2); // Maximum hints per row
    const maxColHints = Math.ceil(height / 2); // Maximum hints per column

    // Create side (row) hints as inputs
    sideHints.style.gridTemplateRows = `repeat(${height}, 30px)`;
    sideHints.style.gridTemplateColumns = `repeat(${maxRowHints}, 30px)`;
    for (let i = 0; i < height; i++) {
        for (let j = 0; j < maxRowHints; j++) {
            let input = document.createElement("input");
            input.type = "text";
            input.classList.add("hint-input");
            input.placeholder = "0";
            sideHints.appendChild(input);
        }
    }

    // Create top (column) hints as inputs
    topHints.style.gridTemplateColumns = `repeat(${width}, 30px)`;
    topHints.style.gridTemplateRows = `repeat(${maxColHints}, 30px)`;
    for (let j = 0; j < width; j++) {
        for (let i = 0; i < maxColHints; i++) {
            let input = document.createElement("input");
            input.type = "text";
            input.classList.add("hint-input");
            input.placeholder = "0";
            topHints.appendChild(input);
        }
    }

    // Create the main grid
    for (let i = 0; i < height; i++) {
        for (let j = 0; j < width; j++) {
            let cell = document.createElement("div");
            cell.classList.add("cell", "empty");
            grid.appendChild(cell);
        }
    }
}

async function solvePuzzle() {
    const width = parseInt(document.getElementById("width").value);
    const height = parseInt(document.getElementById("height").value);
    
    const rowHintsInputs = document.querySelectorAll("#side-hints input");
    const colHintsInputs = document.querySelectorAll("#top-hints input");

    // Calculate the number of hint inputs per row/column
    const maxRowHints = Math.ceil(width / 2);
    const maxColHints = Math.ceil(height / 2);

    // Parse row hints into arrays
    const rowHints = [];
    for (let i = 0; i < height; i++) {
        const hints = [];
        for (let j = 0; j < maxRowHints; j++) {
            const value = rowHintsInputs[i * maxRowHints + j].value.trim();
            if (value) {
                hints.push(parseInt(value));
            }
        }
        rowHints.push(hints);
    }

    // Parse column hints into arrays
    const colHints = [];
    for (let j = 0; j < width; j++) {
        const hints = [];
        console.log(hints);
        for (let i = 0; i < maxColHints; i++) {
            console.log(i, j);
            const value = colHintsInputs[i * width + j].value.trim(); // Corrected indices
            if (value) {
                hints.push(parseInt(value));
            }
        }
        colHints.push(hints);
    }

    // Send data to the API
    const response = await fetch('https://nonogramsolver.onrender.com/api/solve/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rows: height, cols: width, row_hints: rowHints, col_hints: colHints })
    });
    
    const data = await response.json();
    drawGrid(data.final_board);
}

function drawGrid(board) {
    const grid = document.getElementById("grid");
    grid.innerHTML = "";
    board.forEach(row => {
        row.split('').forEach(cell => {
            const div = document.createElement("div");
            div.classList.add("cell", cell === '#' ? 'filled' : 'empty');
            grid.appendChild(div);
        });
    });
}


generateGrid();