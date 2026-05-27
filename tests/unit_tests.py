import os
import pytest
from unittest import mock
from pipeline.storage import storageS3


def test_parse_jobs_extrai_dados_corretamente(scraper_instance, mock_html_vaga):
    """Garante que o parse_jobs extrai os campos e ignora 'Sem Título'"""
    
    
    resultado = scraper_instance.parse_jobs(mock_html_vaga)
    
  
    
    # 1. Deve encontrar apenas 1 vaga válida 
    assert len(resultado) == 1
    
    vaga = resultado[0]
    
    # 2. Valida se os campos foram mapeados 
    assert vaga["titulo"] == "Recrutamento na Oxfam, para a vaga de Auditoria Externa, em Cuamba, em Moçambique."
    assert vaga["link"] == "https://www.emprego.co.mz/en/vaga/auditoria-externa/"
    assert vaga["role"] == "Auditoria"
    assert vaga["empresa"] == "Oxfam"
    
    # 3. Valida se o  Regex do Scraper apanhou a localização antes do transform lower()
    assert vaga["location"] == "Cuamba"


def test_storage_s3_falha_se_faltar_variavel_no_env(mock_aws_env):
    """Garante que o storage aborta se uma das chaves for apagada do .env"""
    
    # Simula o apagão de uma chave crucial (ex: AWS_SECRET_KEY)
    if "AWS_SECRET_KEY" in os.environ:
        del os.environ["AWS_SECRET_KEY"]
        
    # Mock a função 'ler_parquet_mais_recente' para fingir que há um arquivo válido,
    # forçando o código a passar da primeira linha e bater na validação do .env
    with mock.patch('pipeline.storage.ler_parquet_mais_recente', return_value='data/processed/clean_vagas_teste.parquet'):
        
        # Mock o boto3.client para garantir que, se a validação falhar, 
        # ele nao vai tentar iniciar a conexão com a AWS
        with mock.patch('boto3.client') as mock_boto:
            storageS3()
            
            
            mock_boto.assert_not_called()

def test_storage_s3_tenta_conectar_se_env_estiver_completo(mock_aws_env):
    """Garante que o fluxo segue para o boto3 se todas as variáveis existirem"""
    
    # Mock o ficheiro recente e o upload_file para o teste não quebrar a tentar enviar algo real
    with mock.patch('pipeline.storage.ler_parquet_mais_recente', return_value='data/processed/clean_vagas_teste.parquet'), \
         mock.patch('boto3.client') as mock_boto:
        
        storageS3()
        
        # ASSERT: Como o ambiente estava completo (graças à fixture), 
        # o inicializador do boto3.client TEM de ter sido chamado
        mock_boto.assert_called_once_with(
            's3',
            aws_access_key_id='chave_falsa_123',
            aws_secret_access_key='segredo_falso_456',
            region_name='us-east-1'
        )