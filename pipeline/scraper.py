import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime


class Scraper:
    def __init__(self):
        self.base_url="https://www.emprego.co.mz/en/" 
        self.headers= {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9"
            }
        
    def fetch_page(self):
        try:
            response = requests.get(self.base_url, headers= self.headers, timeout = 10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Erro ao aceder ao site, status: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro de rede ou timeout: {e}")
            return None
    
    def parse_jobs(self, html_content):
        parser = bs(html_content, 'html.parser')
        vagas = []
        
        #capturas todos os blocos ou títulos de vagas da página
        items_vagas = parser.find_all('li') 
        
        #loop varre esses cabeçalhos para extrair os atributos
        for item in items_vagas:
            # 1. Extrai o resumo descritivo do h4 (como já fizeste muito bem)
            h4_tag = item.find('h4')
            titulo = h4_tag.text.strip() if h4_tag else "Sem Título"
            
            # 2. Vamos buscar TODOS os links (tags <a>) que existem dentro deste bloco de vaga
            links = item.find_all('a')
            
            # Se o bloco for válido, o primeiro link é a própria vaga, o segundo é a empresa, o terceiro é o local!
            if len(links) >= 3:
                link = links[0]['href'] if links[0].has_attr('href') else None
                empresa = links[1].text.strip()
                location = links[2].text.strip()
                
                    
            else:
                # Fallback de segurança caso o bloco seja um anúncio ou esteja incompleto
                link = links[0]['href'] if (links and links[0].has_attr('href')) else None
                empresa = "Não Especificada"
                location = "Maputo"
            
            # Monta o dicionário temporário da vaga (Adorei a estrutura!)
            dados_vaga = {
                "titulo": titulo,
                "link": link,
                "empresa": empresa,
                "location": location
            }
            
            if titulo != "Sem Título":
                vagas.append(dados_vaga)
                
        df= pd.DataFrame(vagas)
        load_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        df.to_parquet(f'data/raw/raw_vagas_{load_id}.parquet')
        print(f'data/raw/raw_vagas_{load_id}.parquet')
        return vagas
        
    
    
        