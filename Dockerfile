FROM python:3.11-slim

# Define o directório de trabalho
WORKDIR /app

# Copia e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código todo
COPY . .

# Cria as pastas de dados
RUN mkdir -p data/raw data/processed

# Corre o pipeline
CMD ["python", "main.py"]