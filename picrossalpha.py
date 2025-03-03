from rest_framework.response import Response
from rest_framework.decorators import api_view

def generate_possible_partial_rows(hint, length, current_row):
    """Generate all possible row configurations based on hints and the current row state."""
    if not hint:
        return ['.' * length] if all(c in {'.', '?'} for c in current_row) else []
    
    def backtrack(index, hint_index, row):
        """Recursively tries to place hint blocks at valid positions."""
        if hint_index == len(hint):
            if all(c == '?' or c == r for c, r in zip(current_row, row)):
                valid_rows.append(''.join(row))
            return
        
        block_size = hint[hint_index]
        for start in range(index, length - block_size + 1):
            if start > 0 and row[start - 1] == '#':
                continue  # Can't place block right after another block
            
            new_row = row[:]
            new_row[start:start + block_size] = ['#'] * block_size  # Place block
            
            if start + block_size < length:
                new_row[start + block_size] = '.'  # Add space
            
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

def update_board(board, row_hints, col_hints):
    rows, cols = len(row_hints), len(col_hints)
    updated = False
    steps = []
    
    for i in range(rows):
        if '?' in board[i]:
            possible_rows = generate_possible_partial_rows(row_hints[i], cols, board[i])
            if possible_rows:
                merged = merge_possibilities(possible_rows)
                if merged != board[i]:
                    board[i] = merged
                    updated = True
                    steps.append({"type": "row", "index": i, "state": board.copy()})
    
    for j in range(cols):
        col = ''.join(board[i][j] for i in range(rows))
        possible_cols = generate_possible_partial_rows(col_hints[j], rows, col)
        if possible_cols:
            merged = merge_possibilities(possible_cols)
            if merged != col:
                for i in range(rows):
                    board[i] = board[i][:j] + merged[i] + board[i][j+1:]
                    updated = True
                steps.append({"type": "col", "index": j, "state": board.copy()})
    
    return updated, steps

@api_view(['POST'])
def solve_picross(request):
    data = request.data
    rows, cols = data['rows'], data['cols']
    row_hints, col_hints = data['row_hints'], data['col_hints']
    
    board = ['?' * cols for _ in range(rows)]
    steps = []
    
    while True:
        updated, step_data = update_board(board, row_hints, col_hints)
        steps.extend(step_data)
        if not updated or all('?' not in row for row in board):
            break
    
    return Response({"steps": steps, "final_board": board})
