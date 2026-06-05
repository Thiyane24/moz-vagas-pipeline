import glob
import os
import pandas as pd
from datetime import datetime


def ler_e_combinar_arquivos_bronze():
    """Localiza o ficheiro raw mais recente de CADA scraper e combina-os"""
    import glob
    import os
    import pandas as pd

    ficheiros = glob.glob('data/raw/raw_vagas_*.parquet')
    
    if not ficheiros:
        print("Nenhum ficheiro Parquet encontrado na pasta data/raw/ para leitura.")
        return None

    # Dicionário para garantir apenas o ficheiro mais recente por fonte
    fontes_mais_recentes = {}

    for ficheiro in ficheiros:
        nome_base = os.path.basename(ficheiro)
        
        # Identifica o grupo do scraper
        if "emprego.co.mz" in nome_base:
            grupo = "emprego_co_mz"
        elif "mmo" in nome_base:
            grupo = "mmo_vagas"
        elif "moz" in nome_base:
            grupo = "vagas_emprego_moz"
        else:
            grupo = "desconhecida"

        # Se o grupo não existe ou este ficheiro é mais recente do que o guardado, atualiza
        mtime_atual = os.path.getmtime(ficheiro)
        if grupo != "desconhecida":
            if grupo not in fontes_mais_recentes or mtime_atual > fontes_mais_recentes[grupo]['mtime']:
                fontes_mais_recentes[grupo] = {
                    'caminho': ficheiro,
                    'mtime': mtime_atual
                }

    lista_dfs = []
    print("Ficheiros mais recentes selecionados por scraper para consolidação:")
    for grupo, info in fontes_mais_recentes.items():
        ficheiro = info['caminho']
        print(f" -> {grupo}: {ficheiro}")
        try:
            df_temp = pd.read_parquet(ficheiro)
            if not df_temp.empty:
                df_temp["origem"] = grupo
                lista_dfs.append(df_temp)
        except Exception as e:
            print(f"Erro ao ler o ficheiro {ficheiro}: {e}")

    if not lista_dfs:
        return None
        
    df_consolidado = pd.concat(lista_dfs, ignore_index=True, sort=False)
    print(f"Dados unificados com sucesso. Total de linhas iniciais: {len(df_consolidado)}")
    return df_consolidado

def tratar_nulos(df):
    if df is None or df.empty:
        return df
    
    print("Verificação de Nulos")
  
    print(df.isnull().sum())
    
    colunas_com_nulos = [col for col in df.columns if df[col].isnull().any()]

    if not colunas_com_nulos:
        print("Nenhuma coluna com valores nulos.") 
    else:
        for coluna in colunas_com_nulos:
            # Preenche nulos mantendo o tipo string para a padronização
            df[coluna] = df[coluna].fillna("Não Especificada")
            print(f"Coluna '{coluna}' normalizada com 'Não Especificada'.")
    return df


def tratar_duplicados(df):
    if df is None or df.empty:
        return df
    
    print("Verificação de Duplicados")
  
   
    subset_col = ['link'] if 'link' in df.columns else None
    
    n_duplicados = df.duplicated(subset=subset_col).sum()
    print(f"Número de linhas duplicadas detetadas: {n_duplicados}")

    if n_duplicados > 0:
        df = df.drop_duplicates(subset=subset_col, keep='first')
        print(f"Linhas após remoção de duplicados técnicos: {len(df)}")
    return df


def padronizar(df):
    if df is None or df.empty:
        return df
    
    print("Padronização de Texto")
    
    # Lista de colunas possíveis geradas pelos diferentes scrapers
    text_cols = ['titulo', 'role', 'empresa', 'location', 'regime', 'titulo_original', 'origem'] 
    
    for col in text_cols:
        if col in df.columns:
            # Passa para lowercase, remove espaços e garante formato string limpo
            df[col] = df[col].astype(str).str.lower().str.strip()
            
    return df


def transformar():
    
    df = ler_e_combinar_arquivos_bronze()
    if df is None:
        print("Transformação falhou: nenhum dado encontrado na camada Bronze.")
        return None

  
    df = tratar_nulos(df)
    df = tratar_duplicados(df)
    df = padronizar(df)
    
    if df is not None and not df.empty:
        os.makedirs('data/processed', exist_ok=True)
        
        load_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        caminho_silver = f'data/processed/silver_vagas_limpas_{load_id}.parquet'
        
        
        df.to_parquet(caminho_silver, index=False)
        print(f"Dados consolidados e salvos na camada Silver: {caminho_silver}")
        return caminho_silver
        
    return None


if __name__ == "__main__":
    transformar()