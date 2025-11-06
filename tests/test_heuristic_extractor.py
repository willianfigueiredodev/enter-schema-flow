import pytest
from src.extraction_pipeline.extractors.heuristic_extractor import HeuristicExtractor

@pytest.fixture
def extractor() -> HeuristicExtractor:
    """Provides a fresh instance of the HeuristicExtractor for each test."""
    return HeuristicExtractor()

MOCK_OAB_BLOCKS = [
    (50, 50, 200, 70, "JOANA D'ARC\n"), 
    (50, 80, 100, 90, "Inscrição\n"),
    (50, 90, 100, 100, "101943\n"),
    (500, 800, 550, 820, "SITUAÇÃO REGULAR\n"),
]

def test_extract_oab_number_success(extractor: HeuristicExtractor):
    """
    Tests that the extractor finds the OAB number.
    """
    print("Running test_extract_oab_number_success...")
    schema = {"inscricao": "Número de inscrição"}
    
    found, remaining = extractor.extract(MOCK_OAB_BLOCKS, schema)
    
    assert "inscricao" in found
    assert found["inscricao"] == "101943"
    assert "inscricao" not in remaining

def test_extract_name_by_layout_success(extractor: HeuristicExtractor):
    """
    Tests that the layout heuristic finds the name.
    """
    print("Running test_extract_name_by_layout_success...")
    schema = {"nome": "Nome do profissional"}
    
    found, remaining = extractor.extract(MOCK_OAB_BLOCKS, schema)
    
    assert "nome" in found
    assert found["nome"] == "JOANA D'ARC"
    assert "nome" not in remaining

def test_extract_situacao_by_layout_success(extractor: HeuristicExtractor):
    """
    Tests that the layout heuristic finds the situacao.
    """
    print("Running test_extract_situacao_by_layout_success...")
    schema = {"situacao": "Situação do profissional"}
    
    found, remaining = extractor.extract(MOCK_OAB_BLOCKS, schema)
    
    assert "situacao" in found
    assert found["situacao"] == "SITUAÇÃO REGULAR"
    assert "situacao" not in remaining