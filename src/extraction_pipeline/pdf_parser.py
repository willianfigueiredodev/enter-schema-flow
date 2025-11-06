import fitz 
import hashlib
from typing import List

class PdfParser:
    """
    Encapsulates PDF text extraction and file hashing.
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self._text_cache = None
        self._hash_cache = None

    def get_file_hash(self) -> str:
        """
        Calculates the SHA256 hash of the PDF file content.
        """
        if self._hash_cache:
            return self._hash_cache
        
        try:
            with open(self.pdf_path, 'rb') as f:
                file_bytes = f.read()
                self._hash_cache = hashlib.sha256(file_bytes).hexdigest()
                return self._hash_cache
        except Exception as e:
            print(f"Error generating hash for {self.pdf_path}: {e}")
            return ""

    def extract_text(self) -> str:
        """
        Extracts plain text from the first page of the PDF.
        """
        if self._text_cache:
            return self._text_cache

        try:
            with fitz.open(self.pdf_path) as doc:
                if len(doc) == 0:
                    print(f"Error: PDF {self.pdf_path} is empty.")
                    return ""
                
                page = doc[0] 
                self._text_cache = page.get_text("text")
                return self._text_cache
        except Exception as e:
            print(f"Error reading PDF {self.pdf_path}: {e}")
            return ""