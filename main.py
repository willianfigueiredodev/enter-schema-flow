import json
import os
import argparse
from dotenv import load_dotenv
from typing import List, Dict, Any
from src.extraction_pipeline.pdf_parser import PdfParser
from src.extraction_pipeline.orchestrator import Orchestrator
from src.extraction_pipeline.extractors.llm_extractor import LlmExtractor
from src.extraction_pipeline.extractors.heuristic_extractor import HeuristicExtractor
from src.extraction_pipeline.extractors.cache_extractor import CacheExtractor

def load_dataset(json_path: str) -> List[Dict[str, Any]]:
    """Loads a dataset JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Critical Error: dataset.json not found at '{json_path}'")
        return []
    except json.JSONDecodeError:
        print(f"Critical Error: Failed to read JSON from '{json_path}'.")
        return []

def process_single_item(orchestrator: Orchestrator, label: str, pdf_path: str, schema: Dict[str, str]):
    """Processes a single document and prints the result."""
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at '{pdf_path}'. Skipping.")
        return

    result, time_taken = orchestrator.process_document(
        label=label,
        pdf_path=pdf_path,
        original_schema=schema
    )
    
    print(f"--- Extraction Result (Took {time_taken:.4f}s) ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))

def main():
    """
    Main entry point for the application.
    Sets up and runs the extraction pipeline.
    """
    print("--- Starting Extraction Application ---")
    load_dotenv() 

    parser = argparse.ArgumentParser(description="Run the extraction pipeline.")
    parser.add_argument('--file', type=str, help="Path to a single PDF file to process.")
    parser.add_argument('--label', type=str, help="The label for the single PDF file.")
    parser.add_argument('--schema', type=str, help="The extraction schema (as a JSON string).")
    args = parser.parse_args()

    heuristic_ext = HeuristicExtractor()
    cache_ext = CacheExtractor()
    llm_ext = LlmExtractor(model="gpt-5-mini")
    
    orchestrator = Orchestrator(
        heuristic_extractor=heuristic_ext,
        cache_extractor=cache_ext,
        llm_extractor=llm_ext
    )

    if args.file and args.label:
        print(f"Running in SINGLE FILE mode for: {args.file}")
        
        if not args.schema:
            print("Error: --schema (as a JSON string) is required for single file mode.")
            return

        try:
            schema_dict = json.loads(args.schema)
        except json.JSONDecodeError:
            print("Error: --schema argument is not valid JSON.")
            return

        process_single_item(orchestrator, args.label, args.file, schema_dict)

    else:
        print("Running in BATCH (dataset.json) mode...")
        DATASET_PATH = "data/dataset.json"
        dataset = load_dataset(DATASET_PATH)
        if not dataset:
            print("Application shutting down due to dataset error.")
            return

        print(f"Items to process: {len(dataset)}")

        for item in dataset:
            label = item.get("label")
            schema = item.get("extraction_schema")
            pdf_rel_path = item.get("pdf_path") 
            
            pdf_filename = os.path.basename(pdf_rel_path)
            pdf_abs_path = os.path.join("data", pdf_filename)
            
            if not all([label, schema, pdf_abs_path]):
                print(f"Invalid item in dataset (missing data): {item}")
                continue

            process_single_item(orchestrator, label, pdf_abs_path, schema)

    print("\n--- Processing Finished ---")

if __name__ == "__main__":
    main()