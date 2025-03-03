from itertools import product
from itertools import combinations

def get_picross_input():
    rows = int(input("Enter the number of rows: "))
    cols = int(input("Enter the number of columns: "))

    row_hints = []
    print("Enter row hints (comma-separated numbers for each row):")
    for i in range(rows):
        hint = input(f"Row {i+1}: ")
        row_hints.append(list(map(int, hint.split(','))) if hint else [])

    col_hints = []
    print("Enter column hints (comma-separated numbers for each column):")
    for i in range(cols):
        hint = input(f"Column {i+1}: ")
        col_hints.append(list(map(int, hint.split(','))) if hint else [])

    return rows, cols, row_hints, col_hints

from itertools import product

def generate_possible_partial_rows(hint, length, current_row):
    """
    Generate all possible row configurations based on hints and the current row state.
    """
    if not hint:
        return ['.' * length] if all(c in {'.', '?'} for c in current_row) else []
    
    def backtrack(index, hint_index, row):
        """
        Recursively tries to place hint blocks at valid positions.
        """
        if hint_index == len(hint):  # Placed all blocks
            # Ensure the remaining row is valid (no contradictions)
            if all(c == '?' or c == r for c, r in zip(current_row, row)):
                valid_rows.append(''.join(row))
            return
        
        block_size = hint[hint_index]
        for start in range(index, length - block_size + 1):
            # Check if there's enough space after placing the block
            if start > 0 and row[start - 1] == '#':
                continue  # Can't place block right after another block
            
            new_row = row[:]
            new_row[start:start + block_size] = ['#'] * block_size  # Place block
            
            # Ensure the next position is either out of bounds or a space (if needed)
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
    
    # Process rows
    for i in range(rows):
        if '?' in board[i]:
            possible_rows = generate_possible_partial_rows(row_hints[i], cols, board[i])
            print(board)
            print(possible_rows)
            if possible_rows:
                merged = merge_possibilities(possible_rows)
                if merged != board[i]:
                    board[i] = merged
                    updated = True
    
    # Process columns
    for j in range(cols):
        col = ''.join(board[i][j] for i in range(rows))
        possible_cols = generate_possible_partial_rows(col_hints[j], rows, col)
        if possible_cols:
            merged = merge_possibilities(possible_cols)
            if merged != col:
                for i in range(rows):
                    board[i] = board[i][:j] + merged[i] + board[i][j+1:]
                    updated = True
    print(board)
    return updated

def interactive_solve(row_hints, col_hints):
    rows, cols = len(row_hints), len(col_hints)
    board = ['?' * cols for _ in range(rows)]
    
    while True:
        updated = update_board(board, row_hints, col_hints)
        
        # Check if the board is fully solved
        if all('?' not in row for row in board):
            break
        
        # Only prompt if no updates were made and ambiguity remains
        if not updated and any('?' in row for row in board):
            print("\nCurrent Board:")
            for row in board:
                print(row)
            
            print("There are multiple possible solutions. Please confirm one cell.")
            while True:
                try:
                    r = int(input("Enter row index (0-based): "))
                    c = int(input("Enter column index (0-based): "))
                    v = input("Enter value ('#' or '.'): ")
                    
                    if 0 <= r < rows and 0 <= c < cols:
                        if board[r][c] == '?':  # Ensure modification only occurs on '?'
                            if v in {'#', '.'}:
                                board[r] = board[r][:c] + v + board[r][c+1:]
                                break
                            else:
                                print("Invalid value. Enter '#' or '.'")
                        else:
                            print("You can only change uncertain ('?') positions.")
                    else:
                        print("Invalid input. Indices out of range.")
                except ValueError:
                    print("Invalid input. Enter numerical indices and '#' or '.'")
    
    # Verify if all hints are respected
    def check_hints(board, hints, is_row=True):
        for i, hint in enumerate(hints):
            line = board[i] if is_row else ''.join(board[j][i] for j in range(rows))
            groups = [len(g) for g in line.split('.') if g]
            if groups == [] and '#' not in line:  # Correctly validate empty rows/columns
                continue
            if groups != hint:
                print(f"Error: {'Row' if is_row else 'Column'} {i} does not match the hints.")
                return False
        return True
    
    row_valid = check_hints(board, row_hints, True)
    col_valid = check_hints(board, col_hints, False)
    
    if row_valid and col_valid:
        print("\nFinal Board:")
        for row in board:
            print(row)
    else:
        print("\nFinal board does not fully respect all hints. Please review your inputs.")
    
    return board

if __name__ == "__main__":
    initial = int(input("Welcome to Picross Alpha! Press Enter to continue, 1 our game, 2 yours: "))
    if initial == 2:
        rows, cols, row_hints, col_hints = get_picross_input()
    else:
        rows, cols = 5, 5
        row_hints = [[1, 1,], [1, 3, 1], [2,2,4], [2, 1, 1], [4, 1, 1], [1,1,2], [1,1], [5,1], [5,1], [1,5]]
        col_hints = [[1,1,1,1], [1,1,2], [1,2,2], [8], [1, 1,3], [1,6], [3,1], [2,1], [4,1], [2,1,1]]
    interactive_solve(row_hints, col_hints)
