# Použijeme lehkou verzi Pythonu
FROM python:3.11-slim

# Nastavení pracovního adresáře uvnitř kontejneru
WORKDIR /app

# Instalace systémových závislostí pro PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Kopírování requirements a instalace Python knihoven
COPY pavouci_api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopírování celého projektu do kontejneru
COPY . .

# Exponování portu, na kterém aplikace poběží
EXPOSE 8001

# Příkaz pro spuštění aplikace
CMD ["uvicorn", "pavouci_api.main:app", "--host", "0.0.0.0", "--port", "8001"]
