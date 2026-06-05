FROM python:3.11-slim

WORKDIR /app

# 1. Instala dependências 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Cria as pastas necessárias
RUN mkdir -p data/raw data/processed

# 3. Copia o código 
COPY pipeline/ ./pipeline/
COPY main.py .

CMD ["python", "main.py"]