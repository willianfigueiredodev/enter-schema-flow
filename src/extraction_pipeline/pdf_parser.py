import fitz  # PyMuPDF
import hashlib
from typing import List, Tuple, Any

class PdfParser:
    """
    Encapsulates PDF text extraction, hashing, and layout parsing.
    """

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self._text_cache = None
        self._hash_cache = None
        self._blocks_cache = None

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
                self._text_cache = page.get_text("text")
                return self._text_cache
        except Exception as e:
            print(f"Error reading PDF {self.pdf_path}: {e}")
            return ""

    def extract_text_blocks(self) -> List[Tuple[float, float, float, float, str]]:
        """
        Extracts all text blocks with their coordinates (x0, y0, x1, y1, "text").
        """
        if self._blocks_cache:
            return self._blocks_cache

        blocks = []
        try:
            with fitz.open(self.pdf_path) as doc:
                if len(doc) == 0:
                    return []
                
                page = doc[0]

                self._blocks_cache = page.get_text("blocks")
                return self._blocks_cache
        except Exception as e:
            print(f"Error extracting text blocks from {self.pdf_path}: {e}")
            return []