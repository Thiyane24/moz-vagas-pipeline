import sys
from pipeline.emprego_co_mz import EmpregoCoMz_Scraper
from pipeline.mmo_vagas import MMO_Vagas_Scraper
from pipeline.vagasempregomoz import VagasEmpregoMoz_Scraper
from pipeline.transform import transformar
from pipeline.storage import storageS3

def run_pipeline():
    print("A iniciar extração de dados (Camada Bronze)")
    arquivos_bronze = []

    # 1. Executa Ingestão do Site 1: Emprego.co.mz
    try:
        emprego_bot = EmpregoCoMz_Scraper()
        caminho = emprego_bot.run()
        if caminho:
            arquivos_bronze.append(caminho)
    except Exception as e:
        print(f"Falha ao rodar o scraper Emprego.co.mz: {e}")

    # 2. Executa Ingestão do Site 2: MMO Vagas
    try:
        mmo_bot = MMO_Vagas_Scraper()
        caminho = mmo_bot.run()
        if caminho:
            arquivos_bronze.append(caminho)
    except Exception as e:
        print(f"Falha ao rodar o scraper MMO: {e}")
        
    # 3. Executa Ingestão do Site 3: VagasEmpregoMoz
    try:
        moz_bot = VagasEmpregoMoz_Scraper()
        caminho = moz_bot.run()
        if caminho:
            arquivos_bronze.append(caminho)
    except Exception as e:
        print(f"Falha ao rodar o scraper VagasMoz: {e}")
    # Verifica se pelo menos um scraper conseguiu extrair dados novos
    if not arquivos_bronze:
        print("Avisos: Nenhum dado novo foi extraído pelos scrapers nesta execução.")

    print("A iniciar higienização dos dados ")
    # 4. Executa a Transformação Unificada
    caminho_final = transformar()
    
    # 5. Carrega o arquivo unificado para o armazenamento cloud S3 se a transformação for bem-sucedida
    if caminho_final:
        print("A iniciar upload do arquivo processado para o S3")
        storageS3()
        print("Pipeline executado com sucesso global!")
    else:
        print("Concluído com avisos: Nenhuma alteração persistida na camada Silver.")
    

if __name__ == "__main__":
    run_pipeline()