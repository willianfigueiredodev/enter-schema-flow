import os
import json
from openai import OpenAI
from typing import Dict, Any

class LlmExtractor:
    """
    Implements Stage 3 (LLM Fallback).
    
    Receives the FULL PDF text and organizes it into the final JSON.
    This is the "minimum" strategy guaranteed by the manager.
    """
    
    def __init__(self, model: str = "gpt-5-mini"):
        self.model = model 
        try:
            self.client = OpenAI()
        except Exception as e:
            print(f"Critical Error: Failed to initialize OpenAI client. Is API Key set?")
            print(f"Detail: {e}")
            self.client = None

    def _create_prompt(self, pdf_text: str, extraction_schema: Dict[str, str]) -> str:
        """
        Creates the robust "full text" prompt.
        """
        
        fields_string = []
        for key, description in extraction_schema.items():
            fields_string.append(f'- "{key}": ({description})')
        
        fields_string = "\n".join(fields_string)

        return f"""
        Context: You are a document data extraction assistant.
        The document text is in Portuguese.

        Document (Filtered Text):
        ---
        {pdf_text}
        ---
        
        Task: Your job is to analyze the document text and extract the data
        into a valid JSON object.
        
        Rules:
        1.  Respond ONLY with a valid JSON object.
        2.  Match the data to the concepts described in the Extraction Schema.
        3.  If a field is not found, return null.
        4.  Return the exact string from the document (e.g., "JOANA D'ARC", "SITUAÇÃO REGULAR").

        Extraction Schema:
        {fields_string}

        Output JSON:
        """

    def extract(self, pdf_text: str, extraction_schema: Dict[str, str]) -> Dict[str, Any] | None:
        """
        Executes the "Organizer" call to the LLM.
        """
        if not self.client:
            print("...[LOG] LLM Extractor not initialized. Aborting extraction.")
            return None

        # [AÇÃO 13] Nota: o pdf_text que chega aqui é o "filtered_llm_context"
        # do Orchestrator, se o Estágio 1 falhar.
        print(f"...[LOG] Calling Stage 3: LLM (Filtered Text) (Model: {self.model})")
        
        prompt = self._create_prompt(pdf_text, extraction_schema)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            json_result = json.loads(response.choices[0].message.content)
            return json_result
            
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return None