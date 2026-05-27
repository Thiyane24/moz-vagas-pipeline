import glob
import os
import pandas as pd
from datetime import datetime

def ler_parquet_mais_recente():
    # 1. Mapeia todos os ficheiros .parquet dentro da pasta data/raw/
    ficheiros = glob.glob('data/raw/raw_vagas_*.parquet')
    
    if not ficheiros:
        print("Nenhum ficheiro Parquet encontrado na pasta data/raw/ para leitura.")
        return None
        
    # 2. Ordena os ficheiros pela data de modificação e escolhe o último (o mais recente)
    mais_recente = max(ficheiros, key=os.path.getmtime)
   
    
    # 3. Lê o ficheiro diretamente para o Pandas
    df = pd.read_parquet(mais_recente)
    return df

def nulos(df):
    # 1. Verifica a existência de colunas e imprime o número de valores nulos por coluna
    if df.empty:
        print("O DataFrame está vazio. Nenhuma coluna para verificar.")
        return
    
    print("Número de valores nulos por coluna:")
    print(df.isnull().sum())
    
    #Se tiver nulos, preenche com "Não Especificada"
    
    colunas_com_nulos = [col for col in df.columns if df[col].isnull().any()]

    if not colunas_com_nulos:
        print("Nenhuma coluna com nulos.") 
    else:
        for coluna in colunas_com_nulos:
            df[coluna] = df[coluna].fillna("Não Especificada")
            print(f"Coluna '{coluna}' preenchida com 'Não Especificada'.")
    return df

def duplicados(df):
    # 1. Verifica a existência de colunas e imprime o número de duplicados
    if df.empty:
        print("O DataFrame está vazio. Nenhuma coluna para verificar.")
        return
    
    
    n_duplicados = df.duplicated().sum()
    print(f"Número de linhas duplicadas: {n_duplicados}")

    if n_duplicados > 0:
      
        print("Linhas duplicadas encontradas:")
        print(df[df.duplicated(keep='first')])
        df = df.drop_duplicates(keep='first')
        print(f"Linhas após remoção: {len(df)}")
    return df

def padronizar(df):

    if df.empty:
        print("O DataFrame está vazio. Nenhuma coluna para padronizar.")
        return
    
    
    text_cols = ['titulo', 'role', 'empresa', 'location'] 
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].str.lower().str.strip()
        
    
    return df

def transformar():
    df = ler_parquet_mais_recente()
    if df is None:
        print("Transformação falhou: nenhum dado encontrado.")
        return None

    df = nulos(df)
    df = duplicados(df)
    df = padronizar(df)
    return df

