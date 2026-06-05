import os
import pytest
from unittest import mock
from pipeline.storage import storageS3
from pipeline.emprego_co_mz import EmpregoCoMz_Scraper
from pipeline.mmo_vagas import MMO_Vagas_Scraper
from pipeline.vagasempregomoz import VagasEmpregoMoz_Scraper


@pytest.fixture
def mock_aws_env():
    """Define variáveis de ambiente falsas para blindar os testes da AWS"""
    mock_env = {
        "AWS_BUCKET_NAME": "bucket-teste-mock",
        "AWS_ACCESS_KEY": "chave_falsa_123",
        "AWS_SECRET_KEY": "segredo_falso_456",
        "AWS_REGION": "us-east-1"
    }
    with mock.patch.dict(os.environ, mock_env):
        yield




@pytest.fixture
def html_emprego_co_mz():
    """HTML simulado com a estrutura posicional do Emprego.co.mz"""
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

def test_parser_emprego_co_mz_extrai_dados_corretamente(html_emprego_co_mz):
    scraper = EmpregoCoMz_Scraper()
    resultado = scraper.parse_jobs(html_emprego_co_mz)
    
    assert len(resultado) == 1
    vaga = resultado[0]
    assert vaga["titulo"] == "Recrutamento na Oxfam, para a vaga de Auditoria Externa, em Cuamba, em Moçambique."
    assert vaga["link"] == "https://www.emprego.co.mz/en/vaga/auditoria-externa/"
    assert vaga["role"] == "Auditoria"
    assert vaga["empresa"] == "Oxfam"
    assert vaga["location"] == "Cuamba"




@pytest.fixture
def html_mmo_vagas():
    """HTML simulado com a estrutura de listagem do MMO Vagas"""
    return """
    <ul>
        <li class="job_listing">
            <h4 class="job_listing-title">
                <a href="https://emprego.mmo.co.mz/vaga-de-engenheiro-gaza/">
                    Vaga de Engenheiro - Gaza
                </a>
            </h4>
            <div class="job_listing-company"><strong>Cervejas de Moçambique</strong></div>
            <span class="job-type-badge">Tempo Inteiro</span>
        </li>
    </ul>
    """

def test_parser_mmo_vagas_extrai_dados_corretamente(html_mmo_vagas):
    scraper = MMO_Vagas_Scraper()
    resultado = scraper.parse_jobs(html_mmo_vagas)
    
    assert len(resultado) == 1
    vaga = resultado[0]
    assert vaga["titulo"] == "Engenheiro"
    assert vaga["titulo_original"] == "Vaga de Engenheiro - Gaza"
    assert vaga["link"] == "https://emprego.mmo.co.mz/vaga-de-engenheiro-gaza/"
    assert vaga["empresa"] == "Cervejas de Moçambique"
    assert vaga["location"] == "Gaza"
    assert vaga["regime"] == "Tempo Inteiro"



@pytest.fixture
def html_vagas_moz():
    """HTML simulado com a estrutura do portal VagasEmpregoMoz"""
    return """
    <div class="site-main">
        <article class="post">
            <h2>
                <a href="https://vagasempregomoz.com/vaga-de-emprego-contabilista-maputo/">
                    Vaga de Emprego: Contabilista-Maputo
                </a>
            </h2>
            <p>A BDQ Holdings pretende recrutar profissionais qualificados...</p>
        </article>
        <article class="post">
            <h2><a href="https://vagasempregomoz.com/anunciar-vaga/">Anunciar Vaga</a></h2>
        </article>
    </div>
    """

def test_parser_vagas_moz_extrai_dados_corretamente(html_vagas_moz):
    scraper = VagasEmpregoMoz_Scraper()
    resultado = scraper.parse_jobs(html_vagas_moz)
    
    assert len(resultado) == 1
    vaga = resultado[0]
    assert vaga["titulo"] == "Contabilista"
    assert vaga["link"] == "https://vagasempregomoz.com/vaga-de-emprego-contabilista-maputo/"
    assert vaga["empresa"] == "BDQ Holdings"
    assert vaga["location"] == "Maputo"




def test_storage_s3_falha_se_faltar_variavel_no_env(mock_aws_env):
    if "AWS_SECRET_KEY" in os.environ:
        del os.environ["AWS_SECRET_KEY"]
        
    with mock.patch('pipeline.storage.ler_parquet_mais_recente', return_value='data/processed/clean_vagas_teste.parquet'):
        with mock.patch('boto3.client') as mock_boto:
            storageS3()
            mock_boto.assert_not_called()

def test_storage_s3_tenta_conectar_se_env_estiver_completo(mock_aws_env):
    with mock.patch('pipeline.storage.ler_parquet_mais_recente', return_value='data/processed/clean_vagas_teste.parquet'), \
         mock.patch('boto3.client') as mock_boto:
        
        storageS3()
        
        mock_boto.assert_called_once_with(
            's3',
            aws_access_key_id='chave_falsa_123',
            aws_secret_access_key='segredo_falso_456',
            region_name='us-east-1'
        )