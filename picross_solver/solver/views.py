from rest_framework.response import Response
from rest_framework.decorators import api_view
from itertools import product

@api_view(['POST'])
def solve_picross(request):
    data = request.data  # Receive JSON input
    print(data)
    rows, cols = data["rows"], data["cols"]
    row_hints, col_hints = data["row_hints"], data["col_hints"]

    # Initialize the board
    board = ["?" * cols for _ in range(rows)]

    # Solve Picross step-by-step
    steps = []
    while True:
        updated = False
        new_board = board[:]

        # Process rows
        for i in range(rows):
            possible_rows = generate_possible_partial_rows(row_hints[i], cols, board[i])
            merged = merge_possibilities(possible_rows)
            if merged != board[i]:
                new_board[i] = merged
                updated = True
                steps.append({"type": "row", "index": i, "state": new_board})  # Save step

        # Process columns
        for j in range(cols):
            col = "".join(board[i][j] for i in range(rows))
            possible_cols = generate_possible_partial_rows(col_hints[j], rows, col)
            merged = merge_possibilities(possible_cols)
            if merged != col:
                for i in range(rows):
                    new_board[i] = new_board[i][:j] + merged[i] + new_board[i][j+1:]
                updated = True
                steps.append({"type": "col", "index": j, "state": new_board})  # Save step

        board = new_board
        if not updated or all("?" not in row for row in board):
            break

    return Response({"steps": steps, "final_board": board})

def generate_possible_partial_rows(hint, length, current_row):
    """Generate all possible row configurations based on hints."""
    if not hint:
        return ['.' * length] if all(c in {'.', '?'} for c in current_row) else []
    
    def backtrack(index, hint_index, row):
        if hint_index == len(hint):
            if all(c == '?' or c == r for c, r in zip(current_row, row)):
                valid_rows.append(''.join(row))
            return
        
        block_size = hint[hint_index]
        for start in range(index, length - block_size + 1):
            if start > 0 and row[start - 1] == '#':
                continue  
            new_row = row[:]
            new_row[start:start + block_size] = ['#'] * block_size  
            if start + block_size < length:
                new_row[start + block_size] = '.'
            backtrack(start + block_size + 1, hint_index + 1, new_row)

    valid_rows = []
    backtrack(0, 0, ['.'] * length)
    return valid_rows

def merge_possibilities(options):
    """Merge multiple row possibilities, keeping '?' for uncertain positions."""
    merged = list(options[0])
    for opt in options[1:]:
        for i, char in enumerate(opt):
            if merged[i] != char:
                merged[i] = '?'
    return ''.join(merged)
