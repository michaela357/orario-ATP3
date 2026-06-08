def get_calendar_navigation(year, month):
    """
    Calculates the previous and next month/year pagination values.

    Args:
        - year (int): The current year.
        - month (int): The current month.
    Returns:
        - tuple: (prev_year, prev_month, next_year, next_month)
    """
    if month > 1:
        prev_month, prev_year = month - 1, year
    else:
        prev_month, prev_year = 12, year - 1
    
    if month < 12:
        next_month, next_year = month + 1, year
    else:
        next_month, next_year = 1, year + 1
        
    return prev_year, prev_month, next_year, next_month

import os

from docx import Document
from pypdf import PdfReader


def extract_text_from_file(file_path):
    """Helper function to read text based on file extensions."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
            
    elif ext == '.pdf':
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
        
    elif ext == '.docx':
        doc = Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        
    return None