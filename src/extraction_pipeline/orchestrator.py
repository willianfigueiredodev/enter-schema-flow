import time
from typing import Dict, Any, Tuple
from .pdf_parser import PdfParser
from .extractors.llm_extractor import LlmExtractor
from .extractors.heuristic_extractor import HeuristicExtractor
from .extractors.cache_extractor import CacheExtractor

class Orchestrator:
    """
    [AÇÃO 17] Pipeline 0-1-2-3 (Heurística "Word-Aware")
    """
    
    def __init__(self, 
                 heuristic_extractor: HeuristicExtractor, 
                 cache_extractor: CacheExtractor, 
                 llm_extractor: LlmExtractor):
        
        self.heuristic_extractor = heuristic_extractor 
        self.cache_extractor = cache_extractor     
        self.llm_extractor = llm_extractor       
        print("[Orchestrator] Initialized successfully (FINAL 4-Stage Pipeline).")

    def _get_hardcoded_clues(self) -> set:
        FIXED_CLUES = [
            "inscrição", "seccional", "subseção", "categoria", "situação",
            "endereço profissional", "telefone profissional",
            "pesquisar por", "tipo:", "cidade:", "data base:", "produto:", "sistema:",
            "valor parcela", "data de referência"
        ]
        return set(FIXED_CLUES)

    def _build_filtered_llm_context(self, label: str, pdf_text: str, schema_to_find: Dict[str, str]) -> str:
        print("    - [Orchestrator] Building ADAPTIVE filtered context for LLM...")
        lines = pdf_text.split('\n')
        context_lines = set()
        if label == 'carteira_oab':
            for line in lines[:10]: context_lines.add(line)
            for line in lines[-3:]: context_lines.add(line)
        else:
            clues = self._get_hardcoded_clues()
            for key in schema_to_find.keys():
                clues.add(key.replace("_", " "))
            for i, line in enumerate(lines):
                if not line.strip(): continue
                line_lower = line.lower()
                for clue in clues:
                    if clue in line_lower:
                        if i > 0: context_lines.add(lines[i-1])
                        context_lines.add(line)
                        if i + 1 < len(lines): context_lines.add(lines[i+1])
                        if i + 2 < len(lines): context_lines.add(lines[i+2])
                        break
        if not context_lines: return pdf_text
        final_lines = [line for line in lines if line in context_lines and line.strip()]
        filtered_context = "\n".join(final_lines)
        print(f"    - [Orchestrator] Context reduced from {len(pdf_text)} chars to {len(filtered_context)} chars.")
        return filtered_context

    def process_document(self, label: str, pdf_path: str, original_schema: Dict[str, str]) -> Tuple[Dict[str, Any], float]:
        """
        [AÇÃO 17] Executa a pipeline 0-1-2-3 CORRETA.
        """
        start_time = time.perf_counter()
        
        print(f"\n[Orchestrator] Starting pipeline for Label: '{label}' ({pdf_path})")
        
        parser = PdfParser(pdf_path)

        print("...[LOG] Calling Stage 0: Hash Cache...")
        pdf_hash = parser.get_file_hash()
        cached_result = self.cache_extractor.check_hash_cache(pdf_hash)
        
        if cached_result:
            end_time = time.perf_counter()
            time_taken = end_time - start_time
            print(f"[Orchestrator] 100% resolved by Stage 0 (Hash Cache). Finished. (Took {time_taken:.4f}s)")
            return cached_result, time_taken

        pdf_text = parser.extract_text() 
        pdf_words = parser.extract_words() 
        
        if not pdf_text or not pdf_words:
            end_time = time.perf_counter()
            time_taken = end_time - start_time
            print(f"[Orchestrator] Failed to extract text/words. Aborting. (Took {time_taken:.4f}s)")
            return {field: None for field in original_schema}, time_taken

        final_results = {}
        remaining_schema = original_schema.copy()

        print("...[LOG] Calling Stage 1: Heuristic Extractor (Word-Aware)...")
        stage_1_results, stage_2_schema = self.heuristic_extractor.extract(
            pdf_words,
            remaining_schema
        )
        final_results.update(stage_1_results)
        remaining_schema = stage_2_schema
        
        if remaining_schema:
            stage_2_results, stage_3_schema = self.cache_extractor.extract_template(
                label,
                pdf_text,
                remaining_schema
            )
            final_results.update(stage_2_results)
            remaining_schema = stage_3_schema
        else:
            print("[Orchestrator] 100% of fields resolved by Stage 1.")

        if remaining_schema:
            print(f"[Orchestrator] {len(remaining_schema)} field(s) to resolve via LLM.")
            
            filtered_llm_context = self._build_filtered_llm_context(
                label,
                pdf_text,
                remaining_schema
            )
            
            stage_3_results = self.llm_extractor.extract(
                filtered_llm_context, 
                remaining_schema
            )
            
            if stage_3_results:
                final_results.update(stage_3_results)
                self.cache_extractor.learn_template(label, stage_3_results)
        else:
            print("[Orchestrator] 100% of fields resolved by Stage 1 or 2. Skipping LLM.")

        for field in original_schema:
            if field not in final_results:
                final_results[field] = None 
        
        self.cache_extractor.save_hash_cache(pdf_hash, final_results)
        
        end_time = time.perf_counter()
        time_taken = end_time - start_time
        print(f"[Orchestrator] Pipeline finished. (Took {time_taken:.4f}s)")
        return final_results, time_taken