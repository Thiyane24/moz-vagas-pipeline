import http.client
import time
import requests

# Força o interpretador a aceitar respostas longas e pesadas de firewalls
http.client._MAXHEADERS = 1000


class BaseScraper:

    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "connection": "keep-alive",
        }
        self.session.headers.update(self.headers)

    def fetch_page(self, url, page_number=1):
        try:
            # Pausa intencional para evitar bloqueios por taxa de requisição
            if page_number > 1:
                time.sleep(2.0)

            response = self.session.get(url, timeout=15)
            if response.status_code == 200:
                return response.text
            else:
                print(
                    f"Erro HTTP {response.status_code} na página {page_number}"
                )
                return None
        except Exception as e:
            print(f"Erro de Rede/Timeout na página {page_number}: {e}")
            return None