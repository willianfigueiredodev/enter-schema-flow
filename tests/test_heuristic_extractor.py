import pytest
from src.extraction_pipeline.extractors.heuristic_extractor import HeuristicExtractor

@pytest.fixture
def extractor() -> HeuristicExtractor:
    """Provides a fresh instance of the HeuristicExtractor for each test."""
    return HeuristicExtractor()


MOCK_OAB_BLOCKS = [
    (50.0, 50.0, 200.0, 70.0, "JOANA D'ARC\n", 0, 0),    
    (50.0, 80.0, 100.0, 90.0, "Inscrição\n", 1, 0),      
    (110.0, 80.0, 160.0, 90.0, "Seccional\n", 2, 0),     
    (170.0, 80.0, 220.0, 90.0, "Subseção\n", 3, 0),      
    (50.0, 90.0, 100.0, 100.0, "101943\n", 4, 0),        
    (110.0, 90.0, 160.0, 100.0, "PR\n", 5, 0),         
    (170.0, 90.0, 300.0, 100.0, "CONSELHO SECCIONAL - PARANÁ\n", 6, 0),
    (50.0, 100.0, 150.0, 110.0, "SUPLEMENTAR\n", 7, 0), 
    (480.0, 800.0, 550.0, 820.0, "SITUAÇÃO REGULAR\n", 8, 0),
]

MOCK_TS_BLOCKS = [
    (10.0, 50.0, 100.0, 60.0, "Pesquisar por:", 0, 0),
    (110.0, 50.0, 200.0, 60.0, "CLIENTE", 1, 0),
    (10.0, 70.0, 100.0, 80.0, "Tipo:", 2, 0),
    (110.0, 70.0, 200.0, 80.0, "CPF", 3, 0),
    (10.0, 90.0, 100.0, 100.0, "Cidade:", 4, 0),
    (110.0, 90.0, 200.0, 100.0, "Mozarlândia", 5, 0),
    (10.0, 110.0, 100.0, 120.0, "Data Base:", 6, 0),
    (110.0, 110.0, 200.0, 120.0, "05/09/2025", 7, 0),
    (10.0, 130.0, 100.0, 140.0, "Produto:", 8, 0),
    (110.0, 130.0, 200.0, 140.0, "CONSIGNADO", 9, 0),
]

def test_extract_oab_registration_success(extractor: HeuristicExtractor):
    schema = {"inscricao": "Número"}
    found, _ = extractor.extract(MOCK_OAB_BLOCKS, schema)
    assert found.get("inscricao") == "101943"

def test_extract_oab_seccional_success(extractor: HeuristicExtractor):
    schema = {"seccional": "Seccional"}
    found, _ = extractor.extract(MOCK_OAB_BLOCKS, schema)
    assert found.get("seccional") == "PR"

def test_extract_oab_subsecao_success(extractor: HeuristicExtractor):
    schema = {"subsecao": "Subseção"}
    found, _ = extractor.extract(MOCK_OAB_BLOCKS, schema)
    assert found.get("subsecao") == "CONSELHO SECCIONAL - PARANÁ"
    
def test_extract_oab_categoria_success(extractor: HeuristicExtractor):
    schema = {"categoria": "Categoria"}
    found, _ = extractor.extract(MOCK_OAB_BLOCKS, schema)
    assert found.get("categoria") == "SUPLEMENTAR"

def test_extract_name_by_layout_success(extractor: HeuristicExtractor):
    schema = {"nome": "Nome do profissional"}
    found, _ = extractor.extract(MOCK_OAB_BLOCKS, schema)
    assert found.get("nome") == "JOANA D'ARC"

def test_extract_situacao_by_layout_success(extractor: HeuristicExtractor):
    schema = {"situacao": "Situação do profissional"}
    found, _ = extractor.extract(MOCK_OAB_BLOCKS, schema)
    assert found.get("situacao") == "SITUAÇÃO REGULAR"

def test_extract_ts_pesquisa_por_success(extractor: HeuristicExtractor):
    schema = {"pesquisa_por": "Pesquisar por"}
    found, _ = extractor.extract(MOCK_TS_BLOCKS, schema)
    assert found.get("pesquisa_por") == "CLIENTE"

def test_extract_ts_cidade_success(extractor: HeuristicExtractor):
    schema = {"cidade": "Cidade"}
    found, _ = extractor.extract(MOCK_TS_BLOCKS, schema)
    assert found.get("cidade") == "Mozarlândia"

def test_extract_ts_data_base_success(extractor: HeuristicExtractor):
    schema = {"data_base": "Data Base"}
    found, _ = extractor.extract(MOCK_TS_BLOCKS, schema)
    assert found.get("data_base") == "05/09/2025"

def test_extract_ts_produto_success(extractor: HeuristicExtractor):
    schema = {"produto": "Produto"}
    found, _ = extractor.extract(MOCK_TS_BLOCKS, schema)
    assert found.get("produto") == "CONSIGNADO"

def test_extract_ignores_other_fields(extractor: HeuristicExtractor):
    schema = {"endereco_profissional": "Endereço"}
    found, remaining = extractor.extract(MOCK_OAB_BLOCKS, schema)
    assert "endereco_profissional" not in found
    assert "endereco_profissional" in remaining