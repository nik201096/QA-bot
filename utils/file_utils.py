import requests
from PyPDF2 import PdfReader
from io import BytesIO
from PIL import Image
from docx import Document
import pytesseract
import fitz  # PyMuPDF

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def download_file_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to download file from {url}")



def read_pdf(pdf_bytes):
    text = ""
    try:
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        num_pages = pdf_document.page_count
        
        for page_num in range(num_pages):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF with PyMuPDF: {e}")
    return text


def read_docx(file_bytes):
    text = ""
    try:
        doc = Document(BytesIO(file_bytes))
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
        print(f"Error reading .docx file: {e}")
    return text

def read_txt(file_bytes):
    try:
        return file_bytes.decode('utf-8')
    except Exception as e:
        print(f"Error reading .txt file: {e}")
        return ""

def extract_text_from_image(image_bytes):
    try:
        image = Image.open(BytesIO(image_bytes))
        return pytesseract.image_to_string(image)
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return None