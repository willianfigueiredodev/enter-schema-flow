import re
from typing import Dict, Any, Tuple, Callable, List

PAGE_WIDTH = 595
PAGE_HEIGHT = 842

Word = Tuple[float, float, float, float, str, int, int, int]

class HeuristicExtractor:
    """
    [AÇÃO 17.1 - CORRIGIDA]
    Corrige os 2 bugs da Ação 17 (âncora e 'direita').
    """

    def __init__(self):
        """
        [AÇÃO 17.1] Configuração Híbrida (OAB="below", Tela="right")
        """
        self.heuristic_map: Dict[str, Callable[[List[Word]], str | None]] = {

            "nome": self._extract_oab_name,
            "inscricao": self._create_layout_extractor(key="Inscrição", direction="below"),
            "seccional": self._create_layout_extractor(key="Seccional", direction="below"),
            "subsecao": self._create_layout_extractor(key="Subseção", direction="below"),
            "categoria": self._extract_oab_categoria,
            "situacao": self._extract_oab_situacao,
            
            "pesquisa_por": self._create_layout_extractor(key="Pesquisar por:", direction="right"),
            "pesquisa_tipo": self._create_layout_extractor(key="Tipo:", direction="right"),
            "cidade": self._create_layout_extractor(key="Cidade:", direction="right"),
            "data_base": self._create_layout_extractor(key="Data Base:", direction="right"),
            "produto": self._create_layout_extractor(key="Produto:", direction="right"),
            "sistema": self._create_layout_extractor(key="Sistema:", direction="right"),
            "valor_parcela": self._create_layout_extractor(key="Valor Parcela:", direction="right"),
            "data_referencia": self._create_layout_extractor(key="Data de Referência:", direction="right"),
        }
        print("[HeuristicExtractor] Initialized successfully (with FINAL Tuned Rules).")

    def _find_anchor_word(self, words: List[Word], text_to_find: str) -> Word | None:
        """
        Helper: Encontra a *palavra* âncora.
        [CORREÇÃO AÇÃO 17.1] Bug #1 (Falha de 10.93s)
        Lógica robusta para âncoras multi-palavra (ex: "Data Base:").
        """
        anchor_parts = text_to_find.upper().split()
        first_part = anchor_parts[0]

        for i, word in enumerate(words):
            word_text_upper = word[4].upper()
            
            if word_text_upper.startswith(first_part):
                if len(anchor_parts) == 1:
                    return word
                
                if i + 1 < len(words):
                    next_word_upper = words[i+1][4].upper()
                    if next_word_upper.startswith(anchor_parts[1]):
                        return words[i+1]
                
                
                if len(anchor_parts) > 1 and anchor_parts[1] in word_text_upper:
                    return word

        return None
    
    def _find_words_on_line(self, words: List[Word], y0: float, y1: float) -> List[Word]:
        """Helper: Encontra todas as palavras em uma "linha" (coordenada Y)."""
        line_words = []
        for word in words:
            wy0, wy1 = word[1], word[3]
        
            is_on_line = (wy0 >= y0 - 2) and (wy1 <= y1 + 2)
            if is_on_line:
                line_words.append(word)
        return sorted(line_words, key=lambda w: w[0]) 

    def _find_value_right_of(self, words: List[Word], anchor_word: Word) -> str | None:
        """
        Helper: Encontra o valor à DIREITA da âncora.
        """
        ax1, ay0, ay1 = anchor_word[2], anchor_word[1], anchor_word[3]
        
        line_words = self._find_words_on_line(words, ay0, ay1)
        value_words = [word for word in line_words if word[0] > (ax1 + 2)] 
        
        if value_words:
            final_words = []
            for word in value_words:
                word_text = word[4]
        
                if ":" in word_text and len(final_words) > 0:
                    break
                final_words.append(word_text)
            return " ".join(final_words).strip()
            
        return None

    def _find_value_below(self, words: List[Word], anchor_word: Word) -> str | None:
        """
        Helper: Encontra o valor ABAIXO da âncora.
        (Esta é a versão da Ação 17 que funcionou para OAB)
        """
        ax0, ax1, ay1 = anchor_word[0], anchor_word[2], anchor_word[3]
        
        first_word_below = None
        candidates = []
        for word in words:
            wx0, wy0 = word[0], word[1]
            is_below = wy0 > (ay1 + 2)
            is_in_column = (wx0 >= ax0 - 5) and (wx0 <= ax1 + 5) 
            if is_below and is_in_column:
                candidates.append(word)
        
        if not candidates:
            for word in words:
                wx0, wy0 = word[0], word[1]
                is_below = wy0 > (ay1 + 2)
                is_in_column = (wx0 >= ax0 - 10) and (wx0 <= ax1 + 200)
                if is_below and is_in_column:
                    candidates.append(word)
            if not candidates:
                return None

        
        first_word_below = sorted(candidates, key=lambda w: w[1])[0]

        value_line_words = self._find_words_on_line(words, first_word_below[1], first_word_below[3])
        
        column_words = []
        for word in value_line_words:
            wx0 = word[0]
            is_in_column = (wx0 >= ax0 - 5) and (wx0 <= ax1 + 5)
            if is_in_column:
                column_words.append(word[4])
        
        if column_words:
            result_text = " ".join(column_words).strip()
            if re.match(r"^\d+$", result_text) or len(result_text) == 2:
                return result_text
            
        fallback_words = [w[4] for w in value_line_words if w[0] >= ax0 - 5]
        if fallback_words:
             return " ".join(fallback_words).strip()
            
        return None

    def _create_layout_extractor(self, key: str, direction: str) -> Callable[[List[Word]], str | None]:
        """Factory: Cria uma função de extração baseada em layout."""
        
        def extractor(words: List[Word]) -> str | None:
            anchor_word = self._find_anchor_word(words, key)
            if not anchor_word:
                return None
            
            value_str = None
            if direction == "below":
                value_str = self._find_value_below(words, anchor_word)
            elif direction == "right":
                value_str = self._find_value_right_of(words, anchor_word)
            
            return value_str
            
        return extractor

    def _extract_oab_name(self, words: List[Word]) -> str | None:
        """
        Extrai por zona (canto superior esquerdo).
        (Esta é a versão da Ação 17 que funcionou)
        """
        top_zone_y_limit = PAGE_HEIGHT * 0.25
        
        lines = {}
        for word in words:
            y0 = word[1]
            if y0 > top_zone_y_limit:
                break
            
            line_y = round(y0)
            if line_y not in lines:
                lines[line_y] = []
            lines[line_y].append(word[4])
        
        if not lines: return None
        
        sorted_line_keys = sorted(lines.keys())
        for y_key in sorted_line_keys:
            line_text = " ".join(lines[y_key]).strip()
            if not line_text: continue
            
            if "INSCRIÇÃO" in line_text.upper():
                break
                
            if len(line_text) > 5:
                return line_text
        
        return None

    def _extract_oab_situacao(self, words: List[Word]) -> str | None:
        """Extrai por zona (canto inferior direito)."""
        bottom_right_zone_x = PAGE_WIDTH * 0.7
        bottom_right_zone_y = PAGE_HEIGHT * 0.7
        situacao_words = []
        
        for word in words:
            (x0, y0, text) = (word[0], word[1], word[4])
            is_in_zone = (x0 > bottom_right_zone_x and y0 > bottom_right_zone_y)
            
            if is_in_zone and "SITUAÇÃO" in text.upper():
                situacao_words.append(word)
        
        if not situacao_words: return None
        
        first_word = situacao_words[0]
        line_words = self._find_words_on_line(words, first_word[1], first_word[3])
        return " ".join([w[4] for w in line_words]).strip()

    def _extract_oab_categoria(self, words: List[Word]) -> str | None:
        """Regra especial: Procura por 'SUPLEMENTAR' etc."""
        for word in words:
            text = word[4].upper()
            if text in ["SUPLEMENTAR", "ADVOGADO", "ADVOGADA", "ESTAGIARIO", "ESTAGIARIA"]:
                return word[4] 
        return None

    def extract(self, words: List[Word], schema_to_find: Dict[str, str]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Executa o pipeline de heurísticas (agora usando 'words').
        """
        print("...[LOG] Calling Stage 1: Heuristic Extractor (Word-Aware)...")
        
        found_results = {}
        remaining_schema = {}

        for field, description in schema_to_find.items():
            if field in self.heuristic_map:
                extractor_function = self.heuristic_map[field]
                result = extractor_function(words)
                
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