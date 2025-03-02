import cv2
import pytesseract
import numpy as np

def preprocess_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    _, thresh = cv2.threshold(image, 150, 255, cv2.THRESH_BINARY_INV)
    
    return thresh

def extract_hint_regions(image):
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    image_copy = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(image_copy, contours, -1, (0, 255, 0), 2)
    cv2.imshow("Contours Detected", image_copy)
    cv2.waitKey(0)
    
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    if len(contours) < 2:
        raise ValueError("Could not detect hint areas.")
    
    row_hint_area = contours[0]
    col_hint_area = contours[1]
    return row_hint_area, col_hint_area

def extract_numbers(image, contour):
    x, y, w, h = cv2.boundingRect(contour)
    roi = image[y:y+h, x:x+w]
    cv2.imshow("Extracted ROI", roi)
    cv2.waitKey(0)
    
    roi = cv2.bitwise_not(roi)
    cv2.imshow("Inverted ROI", roi)
    cv2.waitKey(0)
    
    text = pytesseract.image_to_string(roi, config='--psm 6 digits')
    print("OCR Raw Output:", text)
    numbers = [int(num) for num in text.split() if num.isdigit()]
    print("Parsed Numbers:", numbers)
    return numbers

def extract_hints(image_path):
    processed_image = preprocess_image(image_path)
    row_hint_area, col_hint_area = extract_hint_regions(processed_image)
    row_hints = extract_numbers(processed_image, row_hint_area)
    col_hints = extract_numbers(processed_image, col_hint_area)
    return row_hints, col_hints

# Example usage
image_path = 'test3.png'  # Replace with actual image path
row_hints, col_hints = extract_hints(image_path)
print("Row Hints:", row_hints)
print("Column Hints:", col_hints)

cv2.destroyAllWindows()