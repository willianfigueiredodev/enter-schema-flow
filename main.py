import json
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

from src.extraction_pipeline.pdf_parser import PdfParser
from src.extraction_pipeline.orchestrator import Orchestrator
from src.extraction_pipeline.extractors.llm_extractor import LlmExtractor
from src.extraction_pipeline.extractors.heuristic_extractor import HeuristicExtractor

def load_dataset(json_path: str) -> List[Dict[str, Any]]:
    """Loads the main dataset.json file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Critical Error: dataset.json not found at '{json_path}'")
        return []
    except json.JSONDecodeError:
        print(f"Critical Error: Failed to read JSON from '{json_path}'.")
        return []

def main():
    print("--- Starting Extraction Application ---")
    
    load_dotenv() 

    DATASET_PATH = "data/dataset.json"
    dataset = load_dataset(DATASET_PATH)

    if not dataset:
        print("Application shutting down due to dataset error.")
        return

    heuristic_ext = HeuristicExtractor()
    llm_ext = LlmExtractor(model="gpt-5-mini")
    
    orchestrator = Orchestrator(
        heuristic_extractor=heuristic_ext,
        llm_extractor=llm_ext
    )

    print(f"Items to process: {len(dataset)}")
    
    all_results = []

    for item in dataset:
        label = item.get("label")
        schema = item.get("extraction_schema")
        pdf_rel_path = item.get("pdf_path") 
        pdf_filename = os.path.basename(pdf_rel_path)
        pdf_abs_path = os.path.join("data", pdf_filename)
        
        if not all([label, schema, pdf_abs_path]):
            print(f"Invalid item in dataset (missing data): {item}")
            continue

        if not os.path.exists(pdf_abs_path):
            print(f"Error: PDF not found at '{pdf_abs_path}'. Skipping.")
            continue
            
        parser = PdfParser(pdf_path=pdf_abs_path)
        document_text = parser.extract_text()
        
        if not document_text:
            print(f"Failed to read text from PDF: {pdf_abs_path}. Skipping.")
            continue
            
        result = orchestrator.process_document(
            label=label,
            pdf_text=document_text,
            original_schema=schema
        )
    
        print("--- Extraction Result ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        all_results.append({
            "file": pdf_filename,
            "label": label,
            "result": result
        })

    print("\n--- Processing Finished ---")

if __name__ == "__main__":
    main()