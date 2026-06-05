from datetime import datetime
import os
import re
from bs4 import BeautifulSoup as bs
import pandas as pd
from pipeline.base_scraper import BaseScraper


class VagasEmpregoMoz_Scraper(BaseScraper):

    def __init__(self):
        super().__init__(base_url="https://vagasempregomoz.com/")

    def parse_jobs(self, html):
        """Isola a lógica de extração para permitir testes unitários"""
        vagas_da_pagina = []
        parser = bs(html, "html.parser")
        
        job_items = parser.select("article, .post, .entry-card, .grid-pro-box")

        if not job_items:
            job_items = [
                div
                for div in parser.find_all(["div", "li"])
                if div.find(["h2", "h3"])
            ]

        for item in job_items:
            h_tag = item.find(["h2", "h3", "h4"])
            if not h_tag:
                continue
            titulo_bruto = h_tag.text.strip()

            if any(
                x in titulo_bruto.lower()
                for x in ["contactos para", "anunciar vaga", "domine excel"]
            ):
                continue

            a_tag = h_tag.find("a") if h_tag.find("a") else item.find("a")
            link = (
                a_tag["href"].strip()
                if a_tag and a_tag.has_attr("href")
                else None
            )

            if not link or "vagasempregomoz.com" not in link:
                continue

            p_tag = item.find("p") or item.find(
                class_=re.compile(r"summary|excerpt|description", re.I)
            )
            descricao_curta = p_tag.text.strip() if p_tag else ""

            match_empresa = re.search(
                r"A\s+([A-Z][A-Za-z0-9\s\.]+?)\s+(?:pretende|anuncia|está a)",
                descricao_curta,
            )
            empresa = (
                match_empresa.group(1).strip()
                if match_empresa
                else "Ver nos detalhes da vaga"
            )

            match_loc = re.search(
                r"(?:-|–|,)\s*([A-Z][a-zà-ú]+(?:\s+[A-Z][a-zà-ú]+)*)$",
                titulo_bruto,
            )
            if match_loc:
                location = match_loc.group(1).strip()
                titulo_limpo = (
                    titulo_bruto.replace(match_loc.group(0), "").strip()
                )
            else:
                location = "Moçambique"
                titulo_limpo = titulo_bruto

            titulo_limpo = re.sub(
                r"^(Vaga de Emprego:|Vagas de Emprego:|Vaga para|Vaga de Emprego para)\s*",
                "",
                titulo_limpo,
                flags=re.I,
            ).strip()

            vagas_da_pagina.append(
                {
                    "titulo": titulo_limpo,
                    "link": link,
                    "empresa": empresa,
                    "location": location,
                }
            )
        return vagas_da_pagina

    def run(self):
        todas_as_vagas = []
        seen_links = set()
        first_page_links = None
        max_paginas = 5

        for page in range(1, max_paginas + 1):
            print(f"[VagasMoz] A aceder à página {page} de {max_paginas}")
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
            elif page_links and page_links == first_page_links:
                break

            novas = [v for v in vagas_da_pagina if v["link"] not in seen_links]
            seen_links.update(v["link"] for v in novas)
            todas_as_vagas.extend(novas)

        if todas_as_vagas:
            df = pd.DataFrame(todas_as_vagas)
            load_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("data/raw", exist_ok=True)
            caminho_parquet = f"data/raw/raw_vagas_moz_{load_id}.parquet"
            df.to_parquet(caminho_parquet, index=False)
            print(f"Sucesso: {len(df)} vagas gravadas para VagasEmpregoMoz")
            return caminho_parquet
        return None