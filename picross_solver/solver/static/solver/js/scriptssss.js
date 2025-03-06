let currentCertainBoard = [];
let currentProbabilityBoard = [];
let currentRowHints = [];
let currentColHints = [];
let previousRowHints = []; // Track previous row hints
let previousColHints = []; // Track previous column hints
let isSolved = false; // Flag to track if the puzzle is solved

function resetState() {
    // Clear all variables
    currentCertainBoard = [];
    currentProbabilityBoard = [];
    currentRowHints = [];
    currentColHints = [];

    // Clear the grid and status box
    const grid = document.getElementById("grid");
    grid.innerHTML = "";
    updateStatus("");
}

function generateGrid() {
    resetState();
    previousRowHints = []; // Reset previous row hints
    previousColHints = []; // Reset previous column hints

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

    // Initialize currentCertainBoard
    currentCertainBoard = Array.from({ length: height }, () => Array.from({ length: width }, () => '?'));

    // Create the main grid
    for (let i = 0; i < height; i++) {
        for (let j = 0; j < width; j++) {
            let cell = document.createElement("div");
            cell.classList.add("cell", "empty");
            grid.appendChild(cell);
        }
    }
}

function drawGrid(certainBoard, probabilityBoard) {
    const grid = document.getElementById("grid");
    grid.innerHTML = ""; // Clear the grid before redrawing
    currentCertainBoard = certainBoard;
    currentProbabilityBoard = probabilityBoard;

    certainBoard.forEach((row, i) => {
        row.forEach((cell, j) => {
            const div = document.createElement("div");
            div.classList.add("cell");

            if (cell === '#') {
                div.classList.add("filled"); // Filled cells
            } else if (cell === '.') {
                div.classList.add("empty", "zero-percent"); // Empty cells with 0% probability
            } else if (cell === '?') {
                div.classList.add("uncertain"); // Uncertain cells
                const probFilled = (probabilityBoard[i][j]['#'] * 100).toFixed(2);
                div.textContent = `${(probFilled / 100).toFixed(2)}`; // Display probability

                // Add click event to uncertain cells
                div.addEventListener("click", () => markCellAsCertain(i, j));
            }

            grid.appendChild(div);
        });
    });
}

function markCellAsCertain(row, col) {
    console.log(`Clicked cell at row: ${row}, col: ${col}`); // Debugging log

    // Ask the user to mark the cell as filled or empty
    const choice = prompt("Mark this cell as:\n1. Filled (#)\n2. Empty (.)");
    if (choice === '1') {
        currentCertainBoard[row][col] = '#';
        console.log(`User chose to mark cell (${row}, ${col}) as Filled (#)`); // Print user's choice
    } else if (choice === '2') {
        currentCertainBoard[row][col] = '.';
        console.log(`User chose to mark cell (${row}, ${col}) as Empty (.)`); // Print user's choice
    } else {
        alert("Invalid choice. Please try again.");
        return;
    }

    isSolved = false; // The puzzle is no longer solved
    solvePuzzle(); // Re-solve the puzzle with the updated certain board
}

function updateStatus(message) {
    const statusBox = document.getElementById("status-box");
    statusBox.textContent = message;
}

function arraysEqual(a, b) {
    if (a === b) return true;
    if (a == null || b == null) return false;
    if (a.length !== b.length) return false;

    for (let i = 0; i < a.length; i++) {
        if (Array.isArray(a[i]) && Array.isArray(b[i])) {
            if (!arraysEqual(a[i], b[i])) return false;
        } else if (a[i] !== b[i]) {
            return false;
        }
    }
    return true;
}

async function solvePuzzle() {
    const width = parseInt(document.getElementById("width").value);
    const height = parseInt(document.getElementById("height").value);
    
    const rowHintsInputs = document.querySelectorAll("#side-hints input");
    const colHintsInputs = document.querySelectorAll("#top-hints input");

    const maxRowHints = Math.ceil(width / 2);
    const maxColHints = Math.ceil(height / 2);

    // Parse row hints
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

    // Parse column hints
    const colHints = [];
    for (let j = 0; j < width; j++) {
        const hints = [];
        for (let i = 0; i < maxColHints; i++) {
            const value = colHintsInputs[i * width + j].value.trim();
            if (value) {
                hints.push(parseInt(value));
            }
        }
        colHints.push(hints);
    }

    // Check if hints have changed
    const hintsChanged = !arraysEqual(rowHints, previousRowHints) || !arraysEqual(colHints, previousColHints);

    if (hintsChanged) {
        // Reset the grid and state if hints have changed
        resetState();
        updateStatus("Solving..."); // Update status to indicate solving is in progress
    }

    // Update previous hints
    previousRowHints = rowHints;
    previousColHints = colHints;

    // Initialize currentCertainBoard if it's empty
    if (!currentCertainBoard.length) {
        currentCertainBoard = Array.from({ length: height }, () => Array.from({ length: width }, () => '?'));
    }

    // Send data to the API
    try {
        const response = await fetch('https://nonogramsolver.onrender.com/api/solve/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                rows: height,
                cols: width,
                row_hints: rowHints,
                col_hints: colHints,
                certain_board: currentCertainBoard // Send the current certain board
            })
        });

        const data = await response.json();
        if (data.error) {
            updateStatus(`Error: ${data.error}`);
        } else if (data.total_solutions === 1) {
            updateStatus("Puzzle solved!");
            isSolved = true; // Set the flag to true
            drawGrid(data.certain_board, data.probability_board); // Draw the solution
        } else if (data.total_solutions > 1) {
            updateStatus(`Multiple solutions found (${data.total_solutions}). Click on uncertain cells to mark them.`);
            isSolved = false; // Set the flag to false
            drawGrid(data.certain_board, data.probability_board); // Draw the possible solutions
        } else {
            updateStatus("No solutions found.");
            isSolved = false; // Set the flag to false
        }
    } catch (error) {
        updateStatus(`Error: ${error.message}`);
        isSolved = false; // Set the flag to false
    }
}

generateGrid();