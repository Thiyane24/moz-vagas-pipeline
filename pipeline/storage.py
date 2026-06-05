import boto3
import glob
import os
from datetime import datetime
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()


def ler_parquet_mais_recente():
    
    pasta_silver = 'data/processed'
    ficheiros = glob.glob(os.path.join(pasta_silver, 'silver_vagas_*.parquet'))

    if not ficheiros:
        print(f" Erro: Nenhum ficheiro Parquet encontrado na pasta: {pasta_silver}")
        return None

    # Escolhe o mais recente pela data de modificação
    mais_recente = max(ficheiros, key=os.path.getmtime)
    print(f"Ficheiro Silver detetado para upload: {mais_recente}")
    return mais_recente 


def storageS3():
    caminho_recente = ler_parquet_mais_recente()
    if not caminho_recente:
        return

    # Valida as variáveis de ambiente antes de tentar ligar
    bucket = os.getenv("AWS_BUCKET_NAME")
    access_key = os.getenv("AWS_ACCESS_KEY")
    secret_key = os.getenv("AWS_SECRET_KEY")
    region = os.getenv("AWS_REGION")

    # Guard para variáveis em falta
    if not all([bucket, access_key, secret_key, region]):
        print(" Erro: Uma ou mais variáveis AWS não estão definidas no .env")
        print(f"  AWS_BUCKET_NAME : {'Sucesso' if bucket else 'Falha'}")
        print(f"  AWS_ACCESS_KEY  : {'Sucesso' if access_key else 'Falha'}")
        print(f"  AWS_SECRET_KEY  : {'Sucesso' if secret_key else 'Falha'}")
        print(f"  AWS_REGION      : {'Sucesso' if region else 'Falha'}")
        return

    nome_file = os.path.basename(caminho_recente)
    
    hoje = datetime.now()
    caminho_s3 = f"gold/year={hoje.year}/month={hoje.strftime('%m')}/day={hoje.strftime('%d')}/{nome_file}"

    try:
        print(f"A estabelecer ligação segura com a AWS ({region})")
        # Inicializa o cliente S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        print(f"A efetuar o upload do ficheiro")
        # Faz upload do ficheiro para o bucket
        s3_client.upload_file(
            Filename=caminho_recente,
            Bucket=bucket,
            Key=caminho_s3
        )

        print(f"Ficheiro carregado ao S3: s3://{bucket}/{caminho_s3}")

    except Exception as e:
        print(f"Erro ao fazer o carregamento para a AWS: {e}")


if __name__ == "__main__":
    print("Iniciando o carregamento para o S3")
    storageS3()