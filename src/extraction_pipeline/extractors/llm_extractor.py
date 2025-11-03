import os 
import json
from openai import OpenAI
from typing import Dict, Any

class LlmExtractor:

    def __init__(self, model: str = "gpt-5-mini"):
        self.model = model

        try:
            self.client = OpenAI()
        except Exception as e:
            print(f"Critical Error: Failed to initialize OpenAI client. Is API Key set?")
            print(f"Detail: {e}")
            self.client = None

    def _create_prompt(self, pdf_text: str, extraction_schema: Dict[str, str]) -> str:
        desired_fields = []
        for key, description in extraction_schema.items():
            desired_fields.append(f'- "{key}": ({description})')

        fields_string = "\n" .join(desired_fields)

        return f"""
        Context: You are a document data extraction assistant.
        Document (text extracted from PDF):
        ---
        {pdf_text}
        ---
        
        Task: Extract the following information from the document above, based on the descriptions.
        Respond ONLY with a valid JSON object.
        If a field is not found, return null for that field.

        Extraction Schema:
        {fields_string}

        Output JSON:
        """

    def extract(self, pdf_text: str, extraction_schema: Dict[str, str]) -> Dict[str, Any] | None:
        if not self.client:
            print("...[LOG] LLM Extractor not initialized. Aborting extraction.")
            return None
        
        print(f"...[LOG] Calling Stage 3: LLM Extractor (Model: {self.model})")

        prompt = self._create_prompt(pdf_text, extraction_schema)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}, 
            )
            
            json_result = json.loads(response.choices[0].message.content)
            return json_result
            
        except Exception as e:
            print(f"Error calling LLM API: {e}")
            return None