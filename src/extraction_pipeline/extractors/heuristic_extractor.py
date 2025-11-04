import re
from typing import Dict, Any, Tuple, Callable

class HeuristicExtractor:

    def __init__(self):
        self.heuristic_map: Dict[str, Callable[[str], str | None]] = {
            "inscricao": self._extract_oab_number,
        }
        print("[HeuristicExtractor] Initialized successfully.")

    def _extract_oab_number(self, pdf_text: str) -> str | None:
        match = re.search(r"Inscrição\s+(\d{6})", pdf_text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        match = re.search(r"\b(\d{6})\b", pdf_text)
        if match:
            return match.group(1)
            
        return None

    def extract(self, pdf_text: str, schema_to_find: Dict[str, str]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        print("...[LOG] Calling Stage 1: Heuristic Extractor...")
        
        found_results = {}
        remaining_schema = {}

        for field, description in schema_to_find.items():
            if field in self.heuristic_map:
                extractor_function = self.heuristic_map[field]
                result = extractor_function(pdf_text)
                
                if result:
                    print(f"    - [HEURISTIC] Field '{field}': FOUND ('{result}')")
                    found_results[field] = result
                else:
                    print(f"    - [HEURISTIC] Field '{field}': Not Found. Marking for next stage.")
                    remaining_schema[field] = description
            else:
                print(f"    - [HEURISTIC] Field '{field}': No heuristic. Marking for next stage.")
                remaining_schema[field] = description
                
        return found_results, remaining_schema