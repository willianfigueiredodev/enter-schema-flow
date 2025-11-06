import re
from typing import Dict, Any, Tuple, Callable, List

PAGE_WIDTH = 595
PAGE_HEIGHT = 842

class HeuristicExtractor:
    """
    Implements Stage 1 (Fast & Cheap) extraction logic.
    Uses Regex and Layout-based logic.
    """

    def __init__(self):
        """
        Initializes the heuristic map.
        """

        self.heuristic_map: Dict[str, Callable[[List[Tuple]], str | None]] = {
            "inscricao": self._extract_oab_number,
            "nome": self._extract_name_by_layout,
            "situacao": self._extract_situacao_by_layout,
        }
        print("[HeuristicExtractor] Initialized successfully (with Layout rules).")

    def _extract_oab_number(self, text_blocks: List[Tuple]) -> str | None:
        """Tenta extrair o número de inscrição OAB (6 dígitos) usando Regex."""
        
        full_text = "\n".join([block[4] for block in text_blocks])

        match = re.search(r"Inscrição\s+(\d{6})", full_text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        match = re.search(r"\b(\d{6})\b", full_text)
        if match:
            return match.group(1)
            
        return None

    def _extract_name_by_layout(self, text_blocks: List[Tuple]) -> str | None:
        """
        Extrai o campo "nome", que o schema descreve como
        "normalmente no canto superior esquerdo".
        """

        top_left_zone = (0, 0, PAGE_WIDTH * 0.5, PAGE_HEIGHT * 0.25)
        
        for (x0, y0, x1, y1, text, block_no, block_type) in text_blocks:
            is_in_zone = (x0 > top_left_zone[0] and
                          y0 > top_left_zone[1] and
                          x1 < top_left_zone[2] and
                          y1 < top_left_zone[3])
            
            text_cleaned = text.strip()
            if is_in_zone and len(text_cleaned) > 5 and text_cleaned != "Inscrição":
                return text_cleaned.replace("\n", " ")
        return None

    def _extract_situacao_by_layout(self, text_blocks: List[Tuple]) -> str | None:
        """
        Extrai o campo "situacao", que o schema descreve como
        "normalmente no canto inferior direito".
        """

        bottom_right_zone = (PAGE_WIDTH * 0.5, PAGE_HEIGHT * 0.75, PAGE_WIDTH, PAGE_HEIGHT)

        for (x0, y0, x1, y1, text, block_no, block_type) in text_blocks:
            is_in_zone = (x0 > bottom_right_zone[0] and
                          y0 > bottom_right_zone[1] and
                          x1 < bottom_right_zone[2] and
                          y1 < bottom_right_zone[3])
            
            text_cleaned = text.strip()
            if is_in_zone and "SITUAÇÃO" in text_cleaned.upper():
                return text_cleaned.replace("\n", " ")
        return None

    def extract(self, text_blocks: List[Tuple], schema_to_find: Dict[str, str]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Executa o pipeline de heurísticas (agora usando blocos de layout).
        """
        print("...[LOG] Calling Stage 1: Heuristic Extractor (Layout-Aware)...")
        
        found_results = {}
        remaining_schema = {}

        for field, description in schema_to_find.items():
            if field in self.heuristic_map:
                extractor_function = self.heuristic_map[field]
                result = extractor_function(text_blocks)
                
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