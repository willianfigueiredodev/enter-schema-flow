from typing import Dict, Any
from .extractors.llm_extractor import LlmExtractor
from .extractors.heuristic_extractor import HeuristicExtractor

class Orchestrator:
    def __init__(self, heuristic_extractor: HeuristicExtractor, llm_extractor: LlmExtractor):
        self.heuristic_extractor = heuristic_extractor
        self.llm_extractor = llm_extractor

        print("[Orchestrator] Initialized successfully.")

    def process_document(self, label: str, pdf_text: str, original_schema: Dict[str, str]) -> Dict[str, Any]:
        print(f"\n[Orchestrator] Starting pipeline for Label: '{label}'...")
        
        final_results = {}
        remaining_schema = original_schema.copy()

        stage_1_results, stage_2_schema = self.heuristic_extractor.extract(
            pdf_text,
            remaining_schema
        )
        final_results.update(stage_1_results)
        remaining_schema = stage_2_schema
        
        print("...[LOG] Stage 2 (Cache): Skipping (not implemented)")

        if remaining_schema:
            print(f"[Orchestrator] {len(remaining_schema)} field(s) to resolve via LLM.")
            
            stage_3_results = self.llm_extractor.extract(
                pdf_text,
                remaining_schema
            )
            
            if stage_3_results:
                final_results.update(stage_3_results)
                
        else:
            print("[Orchestrator] 100% of fields resolved by Stage 1. Skipping LLM.")

        for field in original_schema:
            if field not in final_results:
                final_results[field] = None 

        print("[Orchestrator] Pipeline finished.")
        return final_results