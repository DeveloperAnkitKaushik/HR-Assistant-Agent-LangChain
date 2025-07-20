"""
PDF/Document Processing Utility for LangChain HR Assistant
Extracts text from PDF, DOCX, and TXT files
"""

import io
import PyPDF2
import pdfplumber
from docx import Document
from typing import Optional

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file using multiple methods for better accuracy"""
    text = ""
    
    try:
        # Method 1: pdfplumber (better for complex layouts)
        with pdfplumber.open(io.BytesIO(file_content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"pdfplumber failed: {e}")
        
        # Method 2: PyPDF2 (fallback)
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e2:
            print(f"PyPDF2 also failed: {e2}")
            return "Error: Could not extract text from PDF"
    
    return text.strip()

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        doc = Document(io.BytesIO(file_content))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        return f"Error: Could not extract text from DOCX - {str(e)}"

def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file"""
    try:
        return file_content.decode('utf-8').strip()
    except UnicodeDecodeError:
        try:
            return file_content.decode('latin-1').strip()
        except Exception as e:
            return f"Error: Could not decode text file - {str(e)}"

def process_uploaded_file(uploaded_file) -> str:
    """
    Process uploaded file from Streamlit and extract text
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        str: Extracted text content
    """
    if uploaded_file is None:
        return ""
    
    file_content = uploaded_file.read()
    file_name = uploaded_file.name.lower()
    
    if file_name.endswith('.pdf'):
        return extract_text_from_pdf(file_content)
    elif file_name.endswith('.docx'):
        return extract_text_from_docx(file_content)
    elif file_name.endswith('.txt'):
        return extract_text_from_txt(file_content)
    else:
        return f"Error: Unsupported file type. Please upload PDF, DOCX, or TXT files." 