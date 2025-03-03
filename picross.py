import cv2
import pytesseract
import numpy as np

def preprocess_image_rows(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    thresh = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    kernel = np.ones((2,2), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    return processed

def preprocess_image_columns(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    kernel = np.ones((2,2), np.uint8)
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    return processed

def detect_grid_size(image):
    """ Dynamically detects the grid size based on contours """
    edges = cv2.Canny(image, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Assume the largest square found is the grid area
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    grid_size = min(w, h)  # Assume square grid
    
    print(f"Detected grid bounding box: x={x}, y={y}, w={w}, h={h}, grid_size={grid_size}")
    return x, y, grid_size

def extract_hint_regions(image):
    """ Dynamically extracts hint areas using contours """
    x, y, grid_size = detect_grid_size(image)
    
    # Set left hint width to 1/10 of total image width
    image_width = image.shape[1]
    left_hint_width = max(int(image_width * 0.1), x)  # Ensure it's at least `x`

    top_hints = image[0:y, x:x+grid_size]  # Top hint area
    left_hints = image[y:y+grid_size, 0:left_hint_width]  # Left hint area with fixed width
    
    cv2.imwrite("debug_top_hints.png", top_hints)
    cv2.imwrite("debug_left_hints.png", left_hints)
    
    return top_hints, left_hints, grid_size


def extract_cells(region, num_cells, is_column=True):
    """ Extracts individual hint cells by dynamically detecting their boundaries """
    region_height, region_width = region.shape
    cell_size = (region_width // num_cells) if is_column else (region_height // num_cells)
    
    cells = []
    for i in range(num_cells):
        if is_column:
            cell = region[:, i * cell_size:(i + 1) * cell_size]
        else:
            cell = region[i * cell_size:(i + 1) * cell_size, :]
        
        cv2.imwrite(f"debug_cell_{'col' if is_column else 'row'}_{i}.png", cell)
        cells.append(cell)
    return cells

def extract_text_from_cells(cells):
    """Extracts text from hint cells allowing multiple numbers"""
    hints = []
    
    # Use OCR with custom whitelist and better segmentation
    config = "--psm 6 -c tessedit_char_whitelist='123456789 '"
    
    for i, cell in enumerate(cells):
        cell = cv2.bitwise_not(cell)  # Invert colors for better OCR
        
        # Extra noise filtering (optional)
        cell = cv2.dilate(cell, np.ones((2,2), np.uint8), iterations=1)
        
        # OCR Read
        text = pytesseract.image_to_string(cell, config=config).strip()
        
        # Filter out incorrect readings
        print(f"Cell {i} OCR: {text}")
        cleaned_text = ' '.join(text.split())  # Remove extra spaces
        hints.append(cleaned_text if cleaned_text else "0")  # Ensure empty reads are "0"
        print(f"Cell {i}: {cleaned_text}")
        
    return hints

def extract_hints(image_path):
    # Preprocess separately for rows and columns
    processed_for_rows = preprocess_image_rows(image_path)
    processed_for_columns = preprocess_image_columns(image_path)
    
    # Extract hint regions and detect grid size
    top_hints, left_hints, grid_size = extract_hint_regions(processed_for_columns)  # Use column-friendly processing
    _, left_hints_rows, _ = extract_hint_regions(processed_for_rows)  # Use row-friendly processing

    num_cells = grid_size // 5  # Assume a 5x5 grid for now

    # Extract individual hint cells
    column_cells = extract_cells(top_hints, 5, is_column=True)
    row_cells = extract_cells(left_hints_rows, 5, is_column=False)

    # Get OCR text from each cell
    column_hints = extract_text_from_cells(column_cells)
    row_hints = extract_text_from_cells(row_cells)

    return column_hints, row_hints

if __name__ == "__main__":
    image_path = "test4.png"  # Replace with your image path
    column_hints, row_hints = extract_hints(image_path)
    
    print("Column Hints:")
    print(" ".join(column_hints))
    
    print("Row Hints:")
    print(" ".join(row_hints))