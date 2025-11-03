from typing import Dict, Any
from .extractors.llm_extractor import LlmExtractor

class Orchestrator:

    def __init__(self, llm_extractor: LlmExtractor):
        self.llm_extractor = llm_extractor

    def process_document(self, label: str, pdf_text: str, original_schema: Dict[str, str]) -> Dict[str, Any]:
        print(f"\n[Orchestrator] Starting pipeline for Label: '{label}'...")

        final_results = {}
        remaining_schema = original_schema.copy()

        print("...[LOG] Stage 1 (Heuristics): Skipping (not implemented)")

        print("...[LOG] Stage 2 (Cache): Skipping (not implemented)")

        if remaining_schema:
            print(f"[Orchestrator] {len(remaining_schema)} field(s) to resolve.")

            stage_3_results = self.llm_extractor.extract(
                pdf_text,
                remaining_schema
            )

            if stage_3_results:
                final_results.update(stage_3_results)

        for field in original_schema:
            if field not in final_results:
                final_results[field] = None

        print("[Orchestrator] Pipeline finished.")
        return final_results