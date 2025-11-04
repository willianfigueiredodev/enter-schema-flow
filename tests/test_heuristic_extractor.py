import pytest
from src.extraction_pipeline.extractors.heuristic_extractor import HeuristicExtractor

@pytest.fixture
def extractor() -> HeuristicExtractor:
    return HeuristicExtractor()

MOCK_OAB_TEXT = """
JOANA D'ARC
Inscrição
101943
Seccional Subseção
PR CONSELHO SECCIONAL - PARANÁ
SUPLEMENTAR
SITUAÇÃO REGULAR
"""

def test_extract_oab_number_success(extractor: HeuristicExtractor):
    print("Running test_extract_oab_number_success...")
    
    schema = {"inscricao": "Número de inscrição"}
    found, remaining = extractor.extract(MOCK_OAB_TEXT, schema)
    
    assert "inscricao" in found
    assert found["inscricao"] == "101943"
    assert "inscricao" not in remaining

def test_extract_oab_number_fail(extractor: HeuristicExtractor):
    print("Running test_extract_oab_number_fail...")
    
    text_without_number = "JOANA D'ARC\nSeccional PR"
    schema = {"inscricao": "Número de inscrição"}
    found, remaining = extractor.extract(text_without_number, schema)
    
    assert "inscricao" not in found
    assert "inscricao" in remaining

def test_extract_ignores_other_fields(extractor: HeuristicExtractor):
    print("Running test_extract_ignores_other_fields...")

    schema = {"nome": "Nome do profissional"}
    found, remaining = extractor.extract(MOCK_OAB_TEXT, schema)

    assert "nome" not in found
    assert "nome" in remaining