from rest_framework.response import Response
from rest_framework.decorators import api_view
from itertools import product
from django.shortcuts import render
from collections import defaultdict

@api_view(['POST'])
def solve_picross(request):
    data = request.data  # Receive JSON input
    print(data)
    rows, cols = data["rows"], data["cols"]
    row_hints, col_hints = data["row_hints"], data["col_hints"]
    certain_board = data.get("certain_board", None)  # Get the certain board

    # Generate all possible solutions
    print("Input certain_board:", certain_board)
    solutions = generate_all_solutions(rows, cols, row_hints, col_hints, certain_board)

    if not solutions:
        return Response({"error": "No solutions found"})

    # Analyze solutions to determine certain cells and probabilities
    certain_board, probability_board = analyze_solutions(solutions, rows, cols, certain_board)

    print("Output certain_board:", certain_board)
    return Response({
        "certain_board": certain_board,
        "probability_board": probability_board,
        "total_solutions": len(solutions)
    })

def generate_all_solutions(rows, cols, row_hints, col_hints, certain_board):
    """Generate all possible solutions based on hints and certain board."""
    solutions = []
    board = ["?" * cols for _ in range(rows)]
    if certain_board:
        for i in range(rows):
            for j in range(cols):
                if certain_board[i][j] != '?':
                    board[i] = board[i][:j] + certain_board[i][j] + board[i][j+1:]
    backtrack(board, 0, 0, rows, cols, row_hints, col_hints, solutions, certain_board)
    return solutions

def backtrack(board, row, col, rows, cols, row_hints, col_hints, solutions, certain_board):
    if row == rows:
        if is_valid_solution(board, row_hints, col_hints):
            solutions.append([row[:] for row in board])
        return

    next_row, next_col = (row, col + 1) if col + 1 < cols else (row + 1, 0)

    # If the cell is already certain, skip it
    if certain_board and certain_board[row][col] != '?':
        backtrack(board, next_row, next_col, rows, cols, row_hints, col_hints, solutions, certain_board)
        return

    # Try placing a filled cell
    board[row] = board[row][:col] + '#' + board[row][col+1:]
    if is_partial_valid(board, row_hints, col_hints, row, col):
        backtrack(board, next_row, next_col, rows, cols, row_hints, col_hints, solutions, certain_board)

    # Try placing an empty cell
    board[row] = board[row][:col] + '.' + board[row][col+1:]
    if is_partial_valid(board, row_hints, col_hints, row, col):
        backtrack(board, next_row, next_col, rows, cols, row_hints, col_hints, solutions, certain_board)

    board[row] = board[row][:col] + '?' + board[row][col+1:]

def is_partial_valid(board, row_hints, col_hints, row, col):
    """Check if the current board state is partially valid."""
    # Check row hints
    current_row = board[row]
    if '?' not in current_row:
        if not matches_hint(current_row, row_hints[row]):
            return False

    # Check column hints
    current_col = ''.join(board[i][col] for i in range(len(board)))
    if '?' not in current_col:
        if not matches_hint(current_col, col_hints[col]):
            return False

    return True

def is_valid_solution(board, row_hints, col_hints):
    """Check if the board is a valid solution."""
    for i, row in enumerate(board):
        if not matches_hint(row, row_hints[i]):
            return False
    for j in range(len(board[0])):
        col = ''.join(board[i][j] for i in range(len(board)))
        if not matches_hint(col, col_hints[j]):
            return False
    return True

def matches_hint(line, hint):
    """Check if a line matches the given hint."""
    blocks = [len(block) for block in line.split('.') if block]
    return blocks == hint

def analyze_solutions(solutions, rows, cols, certain_board):
    """Analyze solutions to determine certain cells and probabilities."""
    probability_board = [[{'#': 0, '.': 0} for _ in range(cols)] for _ in range(rows)]

    for solution in solutions:
        for i in range(rows):
            for j in range(cols):
                cell = solution[i][j]
                probability_board[i][j][cell] += 1

    # Initialize certain_board with the input certain_board
    final_certain_board = [row[:] for row in certain_board] if certain_board else [['?' for _ in range(cols)] for _ in range(rows)]

    for i in range(rows):
        for j in range(cols):
            if certain_board and certain_board[i][j] != '?':
                # Skip cells that are already certain
                continue

            total = len(solutions)
            filled = probability_board[i][j]['#']
            empty = probability_board[i][j]['.']

            if filled == total:
                final_certain_board[i][j] = '#'
            elif empty == total:
                final_certain_board[i][j] = '.'
            else:
                final_certain_board[i][j] = '?'
                probability_board[i][j]['#'] = filled / total
                probability_board[i][j]['.'] = empty / total

    return final_certain_board, probability_board

def home(request):
    return render(request, 'index.html')  # Ensure this path is correct