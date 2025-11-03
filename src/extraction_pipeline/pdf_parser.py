import fitz # PyMuPDF
from typing import List

class PdfParser:

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self._text_cache = None 

    def extract_text(self) -> str:
        if self._text_cache:
            return self._text_cache
        
        try:
            with fitz.open(self.pdf_path) as doc:
                if len(doc) == 0:
                    print(f"Error: PDF {self.pdf_path}is empty.")
                    return ""
                
                page = doc[0]
                self._text_cache = page.get_text("text")
                return self._text_cache
        except Exception as e:
            print(f"Error reading PDF {self.pdf_path}: {e}")
            return ""