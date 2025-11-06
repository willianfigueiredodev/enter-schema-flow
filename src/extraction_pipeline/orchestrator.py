from typing import Dict, Any
from .pdf_parser import PdfParser
from .extractors.llm_extractor import LlmExtractor
from .extractors.heuristic_extractor import HeuristicExtractor
from .extractors.cache_extractor import CacheExtractor

class Orchestrator:
    """
    Orchestrates the 0-1-2-3 stage extraction pipeline
    to balance cost, speed, and accuracy.
    """
    
    def __init__(self, 
                 heuristic_extractor: HeuristicExtractor, 
                 cache_extractor: CacheExtractor, 
                 llm_extractor: LlmExtractor):
        """
        Initializes the orchestrator with the extraction strategies (DI).
        """
        self.heuristic_extractor = heuristic_extractor
        self.cache_extractor = cache_extractor
        self.llm_extractor = llm_extractor
        print("[Orchestrator] Initialized successfully.")

    def process_document(self, label: str, pdf_path: str, original_schema: Dict[str, str]) -> Dict[str, Any]:
        """
        Executes the full pipeline for a single document.
        """
        print(f"\n[Orchestrator] Starting pipeline for Label: '{label}' ({pdf_path})")
        
        parser = PdfParser(pdf_path)

        print("...[LOG] Calling Stage 0: Hash Cache...")
        pdf_hash = parser.get_file_hash()
        cached_result = self.cache_extractor.check_hash_cache(pdf_hash)
        
        if cached_result:
            print("[Orchestrator] 100% of fields resolved by Stage 0. Pipeline finished.")
            return cached_result

        pdf_text = parser.extract_text()
        if not pdf_text:
            print("[Orchestrator] Failed to extract text. Aborting.")
            return {field: None for field in original_schema}

        final_results = {}
        remaining_schema = original_schema.copy()

        stage_1_results, stage_2_schema = self.heuristic_extractor.extract(
            pdf_text,
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
            
            stage_3_results = self.llm_extractor.extract(
                pdf_text,
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
        print("[Orchestrator] Pipeline finished.")
        return final_results