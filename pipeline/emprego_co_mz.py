from datetime import datetime
import os
import re
from bs4 import BeautifulSoup as bs
import pandas as pd
from pipeline.base_scraper import BaseScraper


class EmpregoCoMz_Scraper(BaseScraper):

    def __init__(self):
        super().__init__(base_url="https://www.emprego.co.mz/en/")

    def parse_jobs(self, html):
        """Isola a lógica de extração para permitir testes unitários"""
        vagas_da_pagina = []
        parser = bs(html, "html.parser")

        for item in parser.find_all("li"):
            h4_tag = item.find("h4")
            titulo = h4_tag.text.strip() if h4_tag else "Sem Título"
            if titulo == "Sem Título":
                continue

            links = item.find_all("a")
            link = (
                links[0]["href"]
                if links and links[0].has_attr("href")
                else None
            )

            if len(links) >= 3:
                role = links[1].text.strip()
                empresa = links[2].text.strip()
            else:
                role = "Não Especificada"
                empresa = "Não Especificada"

            match = re.search(
                r",\s*in\s+([^,\.]+)|,\s*em\s+([^,\-\.]+)",
                titulo,
                re.IGNORECASE,
            )
            location = (
                (match.group(1) or match.group(2)).strip()
                if match
                else "Não Especificada"
            )

            vagas_da_pagina.append(
                {
                    "titulo": titulo,
                    "link": link,
                    "role": role,
                    "empresa": empresa,
                    "location": location,
                }
            )
        return vagas_da_pagina

    def run(self):
        todas_as_vagas = []
        seen_links = set()
        first_page_links = None
        max_paginas = 15

        for page in range(1, max_paginas + 1):
            print(f"[Emprego.co.mz] A aceder à página {page} de {max_paginas}")
            url = (
                self.base_url
                if page == 1
                else f"{self.base_url}page/{page}/"
            )

            html = self.fetch_page(url, page_number=page)
            if not html:
                break

            vagas_da_pagina = self.parse_jobs(html)

            if not vagas_da_pagina:
                break

            page_links = {v["link"] for v in vagas_da_pagina if v["link"]}
            if page == 1:
                first_page_links = page_links
            elif page_links == first_page_links:
                print(f"Aviso: Página {page} repetida. Parando paginação.")
                break

            novas = [v for v in vagas_da_pagina if v["link"] not in seen_links]
            seen_links.update(v["link"] for v in novas)
            todas_as_vagas.extend(novas)

        if todas_as_vagas:
            df = pd.DataFrame(todas_as_vagas)
            load_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("data/raw", exist_ok=True)
            caminho_parquet = (
                f"data/raw/raw_vagas_emprego.co.mz_{load_id}.parquet"
            )
            df.to_parquet(caminho_parquet, index=False)
            print(f"Sucesso: {len(df)} vagas gravadas para Emprego.co.mz")
            return caminho_parquet
        return None