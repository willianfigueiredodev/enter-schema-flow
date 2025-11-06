import fitz  # PyMuPDF
import hashlib
from typing import List, Tuple, Any

class PdfParser:
    """
    [AÇÃO 17] Parser (get_text("words"))
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self._text_cache = None
        self._hash_cache = None
        self._words_cache = None 

    def get_file_hash(self) -> str:
        """Calculates the SHA256 hash of the PDF file content."""
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
        """Extracts plain text from the first page of the PDF."""
        if self._text_cache:
            return self._text_cache

        try:
            with fitz.open(self.pdf_path) as doc:
                if len(doc) == 0:
                    print(f"Error: PDF {self.pdf_path} is empty.")
                    return ""
                
                page = doc[0] 
                self._text_cache = page.get_text("text", sort=True) 
                return self._text_cache
        except Exception as e:
            print(f"Error reading PDF {self.pdf_path}: {e}")
            return ""

    def extract_words(self) -> List[Tuple[float, float, float, float, str, int, int, int]]:
        """
        [AÇÃO 17] Extrai todas as PALAVRAS com suas coordenadas.
        """
        if self._words_cache:
            return self._words_cache

        try:
            with fitz.open(self.pdf_path) as doc:
                if len(doc) == 0:
                    return []
                
                page = doc[0]
                self._words_cache = page.get_text("words", sort=True) 
                return self._words_cache
        except Exception as e:
            print(f"Error extracting text words from {self.pdf_path}: {e}")
            return []