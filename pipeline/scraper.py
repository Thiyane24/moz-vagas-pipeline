import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from datetime import datetime
import re


class Scraper:
    def __init__(self):
        self.base_url = "https://www.emprego.co.mz/en/"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9"
        }

    def fetch_page(self, page_number=1):
        try:
            url = self.base_url if page_number == 1 else f"{self.base_url}page/{page_number}/"
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Erro ao aceder à página {page_number}, status: {response.status_code}")
                return None
        except Exception as e:
            print(f"Erro de rede ou timeout na página {page_number}: {e}")
            return None

    def parse_jobs(self, html_content):
        parser = bs(html_content, 'html.parser')
        vagas = []

        for item in parser.find_all('li'):
            h4_tag = item.find('h4')
            titulo = h4_tag.text.strip() if h4_tag else "Sem Título"

            if titulo == "Sem Título":
                continue

            links = item.find_all('a')
            link = links[0]['href'] if links and links[0].has_attr('href') else None

            if len(links) >= 3:
                role = links[1].text.strip()
                empresa = links[2].text.strip()
            else:
                role = "Não Especificada"
                empresa = "Não Especificada"

            match = re.search(r',\s*in\s+([^,\.]+)|,\s*em\s+([^,\-\.]+)', titulo, re.IGNORECASE)
            location = (match.group(1) or match.group(2)).strip() if match else "Não Especificada"

            vagas.append({
                "titulo": titulo,
                "link": link,
                "role": role,
                "empresa": empresa,
                "location": location
            })

        return vagas
    
    def run(self):  
        todas_as_vagas = []
        seen_links = set()
        first_page_links = None
        max_paginas = 15

        for page in range(1, max_paginas + 1):
            print(f"A aceder à página {page} de {max_paginas}...")
            html = self.fetch_page(page)

            if not html:
                break

            vagas_da_pagina = self.parse_jobs(html)

            if not vagas_da_pagina:
                break

            page_links = {v["link"] for v in vagas_da_pagina}
            if page == 1:
                first_page_links = page_links
            elif page_links == first_page_links:
                print(f"Página {page} repete a página 1. A parar.")
                break

            novas = [v for v in vagas_da_pagina if v["link"] not in seen_links]
            seen_links.update(v["link"] for v in novas)
            todas_as_vagas.extend(novas)

        if todas_as_vagas:
            df = pd.DataFrame(todas_as_vagas)
            load_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            caminho_parquet = f'data/raw/raw_vagas_{load_id}.parquet'
            df.to_parquet(caminho_parquet)
            print(f"Total de vagas: {len(df)}")
            return caminho_parquet  # ← devolve o caminho para o pipeline usar
        
        return None

if __name__ == "__main__":
    bot = Scraper()
    bot.run()