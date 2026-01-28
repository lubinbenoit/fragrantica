# Dockerfile
FROM python:3.11-slim

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier les fichiers de dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copier le code du projet
COPY scrapy.cfg .
COPY fragrantica_scraper/ ./fragrantica_scraper/
COPY scripts/ ./scripts/
COPY run_scrapers.py .
COPY test_mongo.py .

# Créer les dossiers nécessaires
RUN mkdir -p data crawls logs

# Variables d'environnement
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV SCRAPY_SETTINGS_MODULE=fragrantica_scraper.settings

# Point d'entrée
ENTRYPOINT ["python"]
CMD ["run_scrapers.py"]