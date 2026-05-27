import os
import pytest
from unittest import mock
from pipeline.scraper import Scraper

@pytest.fixture
def scraper_instance():
    """Fixture que devolve uma instância limpa do teu Scraper"""
    return Scraper()

@pytest.fixture
def mock_html_vaga():
    """Devolve um HTML simulado com a estrutura exata que o site usa"""
    return """
    <ul>
        <li>
            <h4>Recrutamento na Oxfam, para a vaga de Auditoria Externa, em Cuamba, em Moçambique.</h4>
            <a href="https://www.emprego.co.mz/en/vaga/auditoria-externa/">Link Vaga</a>
            <a href="https://www.emprego.co.mz/en/cargos/auditoria/">Auditoria</a>
            <a href="https://www.emprego.co.mz/en/empresas/oxfam/">Oxfam</a>
        </li>
        <li>
            <h4>Sem Título</h4>
        </li>
    </ul>
    """


@pytest.fixture
def mock_aws_env():
    """Define variáveis de ambiente falsas para blindar os testes da AWS"""
    mock_env = {
        "AWS_BUCKET_NAME": "bucket-teste-mock",
        "AWS_ACCESS_KEY": "chave_falsa_123",
        "AWS_SECRET_KEY": "segredo_falso_456",
        "AWS_REGION": "us-east-1"
    }
    
    # O patch.dict substitui o os.environ real por este dicionário durante o teste
    with mock.patch.dict(os.environ, mock_env):
        yield