import boto3
import glob
import os
from dotenv import load_dotenv

# carrega as variaveis do .env
load_dotenv()


def ler_parquet_mais_recente():
    # Mapeia todos os ficheiros .parquet dentro da pasta data/processed/
    ficheiros = glob.glob('data/processed/clean_vagas_*.parquet')

    if not ficheiros:
        print("Nenhum ficheiro Parquet encontrado na pasta data/processed/")
        return None

    #  Escolhe o mais recente pela data de modificação
    mais_recente = max(ficheiros, key=os.path.getmtime)
    print(f"Ficheiro : {mais_recente}")
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

    #  guard para variáveis em falta
    if not all([bucket, access_key, secret_key, region]):
        print("Erro: uma ou mais variáveis AWS não estão definidas no .env")
        print(f"  AWS_BUCKET_NAME : {'sucesso' if bucket else 'falha'}")
        print(f"  AWS_ACCESS_KEY  : {'sucesso' if access_key else 'falha'}")
        print(f"  AWS_SECRET_KEY  : {'sucesso' if secret_key else 'falha'}")
        print(f"  AWS_REGION      : {'sucesso' if region else 'falha'}")
        return

    # Define o nome do ficheiro e o caminho dentro do bucket
    nome_file = os.path.basename(caminho_recente)
    caminho_s3 = f"processed/{nome_file}"

    try:
        # Inicializa o cliente S3
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # Faz upload do ficheiro para o bucket
        s3_client.upload_file(
            Filename=caminho_recente,
            Bucket=bucket,
            Key=caminho_s3
        )

        print(f"Ficheiro carregado com sucesso em s3://{bucket}/{caminho_s3}")

    except Exception as e:
        print(f"Erro ao fazer o carregamento para a AWS: {e}")


if __name__ == "__main__":
    print("Iniciando o carregamento para S3...")
    storageS3()