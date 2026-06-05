from datetime import datetime
import os
import re
from bs4 import BeautifulSoup as bs
import pandas as pd
from pipeline.base_scraper import BaseScraper


class MMO_Vagas_Scraper(BaseScraper):

    def __init__(self):
        super().__init__(base_url="https://emprego.mmo.co.mz/")

    def parse_jobs(self, html):
        """Isola a lógica de extração para permitir testes unitários"""
        vagas_da_pagina = []
        parser = bs(html, "html.parser")
        
        job_items = parser.select(
            "li.job_listing, .job-list-item, article.job_listing"
        )

        if not job_items:
            job_items = [
                li
                for li in parser.find_all("li")
                if li.find("h4") or li.find("h3")
            ]

        for item in job_items:
            h_tag = item.find(["h4", "h3", "h2"])
            if not h_tag:
                continue
            titulo_bruto = h_tag.text.strip()

            a_tag = h_tag.find("a") if h_tag.find("a") else item.find("a")
            link = (
                a_tag["href"].strip()
                if a_tag and a_tag.has_attr("href")
                else None
            )

            if not link or "emprego.mmo.co.mz" not in link:
                continue

            empresa_tag = item.find(
                class_=re.compile(r"company|employer|recruiter", re.I)
            )
            if not empresa_tag:
                strong_tags = item.find_all("strong")
                empresa = (
                    strong_tags[0].text.strip()
                    if strong_tags
                    else "Não Especificada"
                )
            else:
                empresa = empresa_tag.text.strip()

            job_type_tag = item.find(
                class_=re.compile(r"job-type|job-time|badge", re.I)
            )
            regime = (
                job_type_tag.text.strip() if job_type_tag else "Tempo Inteiro"
            )

            match_loc = re.search(
                r"(?:,|–|-)\s*(?:em|no|na|in)?\s*([A-Z][a-zà-ú]+(?:\s+[A-Z][a-zà-ú]+)*)",
                titulo_bruto,
            )
            if match_loc:
                location = match_loc.group(1).strip()
                titulo_limpo = (
                    titulo_bruto.replace(match_loc.group(0), "").strip()
                )
            else:
                loc_tag = item.find(
                    class_=re.compile(r"location|location-meta|meta-loc", re.I)
                )
                location = (
                    loc_tag.text.strip() if loc_tag else "Moçambique"
                )
                titulo_limpo = titulo_bruto

            # Regex corrigida para incluir "Vaga de"
            titulo_limpo = re.sub(
                r"^(Vaga de Emprego para|Vaga para|Vaga de|Oportunidade de Emprego:)\s*",
                "",
                titulo_limpo,
                flags=re.I,
            ).strip()

            vagas_da_pagina.append(
                {
                    "titulo": titulo_limpo,
                    "titulo_original": titulo_bruto,
                    "link": link,
                    "empresa": empresa,
                    "location": location,
                    "regime": regime,
                    "scraped_at": datetime.now().isoformat(),
                }
            )
        return vagas_da_pagina

    def run(self):
        todas_as_vagas = []
        seen_links = set()
        first_page_links = None
        max_paginas = 15

        for page in range(1, max_paginas + 1):
            print(f"[MMO Vagas] A aceder à página {page} de {max_paginas}")
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
            caminho_parquet = f"data/raw/raw_vagas_mmo_{load_id}.parquet"
            df.to_parquet(caminho_parquet, index=False)
            print(f"Sucesso: {len(df)} vagas gravadas para MMO Vagas")
            return caminho_parquet
        return None