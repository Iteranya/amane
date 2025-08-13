import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os
import re
import cv2 # OpenCV
import numpy as np

# Optional: If Tesseract is not in your PATH, include the following line
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Example for Windows

def clean_text(text):
    """A helper function to clean up the extracted text."""
    # Replace multiple newlines with a single one
    text = re.sub(r'\n\s*\n', '\n\n', text)
    # Remove form feed characters
    text = text.replace('\f', '')
    # Optional: Fix common OCR errors (e.g., ligatures)
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    # Trim leading/trailing whitespace from each line
    text = "\n".join([line.strip() for line in text.split('\n')])
    return text.strip()

def enhance_image_for_ocr(image):
    """
    Enhances an image for better OCR results using OpenCV.
    - Converts to grayscale
    - Applies adaptive thresholding
    """
    # Convert PIL Image to an OpenCV image (numpy array)
    open_cv_image = np.array(image)

    # Convert RGB to BGR (OpenCV format) if it's a color image
    if len(open_cv_image.shape) == 3 and open_cv_image.shape[2] == 3:
        open_cv_image = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2BGR)

    # Convert the image to grayscale
    gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding to binarize the image.
    # This is often better than a simple global threshold for scanned documents
    # with varying lighting conditions.
    binary_image = cv2.adaptiveThreshold(
        gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )

    # Convert the processed OpenCV image back to a PIL Image
    return Image.fromarray(binary_image)


async def pdf_to_text_pipeline(pdf_path, ocr_threshold=100, use_image_enhancement=True):
    """
    The main pipeline to convert a PDF to raw text.

    Args:
        pdf_path (str): The file path to the PDF.
        ocr_threshold (int): If the character count from direct extraction is
                             below this, OCR will be triggered.
        use_image_enhancement (bool): Whether to use OpenCV to enhance images
                                      before running OCR.

    Returns:
        str: The extracted raw text.
    """
    print(f"--- Starting processing for: {os.path.basename(pdf_path)} ---")

    # === PART 1: FAST PATH - DIRECT TEXT EXTRACTION ===
    try:
        doc = fitz.open(pdf_path)
        direct_text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            direct_text += page.get_text("text")

        doc.close()

        # Check if the extracted text is substantial
        if len(direct_text.strip()) > ocr_threshold:
            print("✅ Success: Extracted text directly (fast path).")
            return clean_text(direct_text)
        else:
            print("⚠️ Direct extraction yielded minimal text. Proceeding to OCR.")

    except Exception as e:
        print(f"Error during direct extraction: {e}. Proceeding to OCR.")

    # === PART 2: ROBUST PATH - OCR ===
    # This part runs if the direct extraction failed or returned too little text.
    print("⏳ Running OCR path (this may take a while)...")
    ocr_text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            print(f"  - OCR on page {page_num + 1}/{len(doc)}")
            page = doc.load_page(page_num)

            # Render page to a high-resolution image (300 DPI is good for OCR)
            pix = page.get_pixmap(dpi=300)
            img_data = pix.tobytes("png")
            image = Image.open(io.BytesIO(img_data))

            # Enhance the image if the flag is set
            if use_image_enhancement:
                image = enhance_image_for_ocr(image)

            # Use Tesseract to do OCR on the image
            page_text = pytesseract.image_to_string(image, lang='eng') # Specify language
            ocr_text += page_text + "\n"

        doc.close()

        if ocr_text.strip():
            print("✅ Success: Extracted text using OCR.")
            return clean_text(ocr_text)
        else:
            print("❌ Failure: OCR path also failed to extract any text.")
            return "" # Return empty string if both methods fail

    except Exception as e:
        print(f"❌ Critical Error during OCR processing: {e}")
        return ""