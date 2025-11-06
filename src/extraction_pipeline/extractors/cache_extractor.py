import json
import re
from typing import Dict, Any, Tuple

class CacheExtractor:
    """
    Implements Stage 0 (Hash Cache) and Stage 2 (Template Cache).
    
    It learns from successful LLM extractions to provide fast, cheap
    responses for repeated files or labels.
    """
    CACHE_FILE = "cache_db.json"

    def __init__(self):
        """Initializes the Cache Extractor and loads cache data."""
        self._load_cache()
        print("[CacheExtractor] Initialized successfully.")

    def _load_cache(self):
        """Loads the cache database from a JSON file."""
        try:
            with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.hash_cache = data.get("hash_cache", {})
                self.template_cache = data.get("template_cache", {})
        except (FileNotFoundError, json.JSONDecodeError):
            self.hash_cache = {}
            self.template_cache = {}

    def _save_cache(self):
        """Saves the current cache state back to the JSON file."""
        try:
            data = {
                "hash_cache": self.hash_cache,
                "template_cache": self.template_cache
            }
            with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"[CacheExtractor] Error saving cache: {e}")

    def check_hash_cache(self, pdf_hash: str) -> Dict[str, Any] | None:
        """
        Checks if an exact result for this file hash already exists.
        """
        return self.hash_cache.get(pdf_hash)
    
    def save_hash_cache(self, pdf_hash: str, result: Dict[str, Any]):
        """
        Saves a definitive result for a specific file hash.
        """
        print(f"    - [CACHE-HASH] Saving result for hash: {pdf_hash[:10]}...")
        self.hash_cache[pdf_hash] = result
        self._save_cache()

    def learn_template(self, label: str, llm_results: Dict[str, Any]):
        """
        Learns from a successful LLM extraction for a specific label.
        """
        if not label:
            return
            
        print(f"    - [CACHE-TPL] Learning from LLM for label: '{label}'")
        
        if label not in self.template_cache:
            self.template_cache[label] = {}
        
        for field, value in llm_results.items():
            if value and (isinstance(value, str) or isinstance(value, list)):
                self.template_cache[label][field] = value
        
        self._save_cache()

    def extract_template(self, label: str, pdf_text: str, schema_to_find: Dict[str, str]) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """
        Runs the template-based cache extraction (Stage 2).
        """
        if not label:
            return {}, schema_to_find

        print("...[LOG] Calling Stage 2: Template Cache...")
        
        if label not in self.template_cache:
            print(f"    - [CACHE-TPL] Label '{label}' not found in cache. Skipping.")
            return {}, schema_to_find

        label_rules = self.template_cache[label]
        found_results = {}
        remaining_schema = {}

        for field, description in schema_to_find.items():
            if field in label_rules:
                saved_value = label_rules[field]
                
                # Simple string matching for now
                if isinstance(saved_value, str) and re.search(re.escape(saved_value), pdf_text):
                    print(f"    - [CACHE-TPL] Field '{field}': FOUND ('{saved_value}')")
                    found_results[field] = saved_value
                # Simple list matching (handles "array of objects")
                elif isinstance(saved_value, list):
                     print(f"    - [CACHE-TPL] Field '{field}': FOUND (from list cache)")
                     found_results[field] = saved_value
                else:
                    print(f"    - [CACHE-TPL] Field '{field}': Cache rule failed. Marking for next stage.")
                    remaining_schema[field] = description
            else:
                print(f"    - [CACHE-TPL] Field '{field}': No cache rule. Marking for next stage.")
                remaining_schema[field] = description

        return found_results, remaining_schema