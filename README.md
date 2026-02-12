# 🌸 Fragrantica – Projet de Data Engineering

Pipeline complet pour collecter, stocker et explorer des données de parfums issues de **fragrantica.com**.

Le projet combine scraping (Scrapy), persistance (MongoDB), et visualisation (Flask + API REST) pour transformer un site communautaire en dataset structuré et interrogeable.

---

## 📋 Table des matières

- [Architecture](#-architecture)
- [Fonctionnalités](#-fonctionnalités)
- [Structure du projet](#-structure-du-projet)
- [Prérequis](#-prérequis)
- [Installation & Démarrage](#-installation--démarrage)
- [API REST](#-api-rest)
- [Scripts utilitaires](#-scripts-utilitaires)
- [Structure des données](#-structure-des-données)

---

## 🏗 Architecture

```
Scrapy Spiders
      ↓
Items + Pipelines (nettoyage)
      ↓
MongoDB (2 collections)
      ↓
Services Flask (logique métier)
      ↓
Routes + API REST
      ↓
Templates Jinja2 / JSON
```

### Flux de données

1. **Spider URLs** (`perfume_urls_spider.py`) → Collecte les URLs des parfums
2. **Spider Data** (`perfume_data_spider.py`) → Extrait les infos détaillées
3. **Pipelines** → Nettoie et normalise les données
4. **MongoDB** → Stocke dans 2 collections (`perfume_urls`, `perfume_data`)
5. **Services** → Requêtes, filtres, agrégations
6. **Routes Flask** → UI web + API REST

---

## ✨ Fonctionnalités

### Pipeline de scraping
- ✅ Crawl automatique des URLs de parfums
- ✅ Extraction : nom, marque, accords, image
- ✅ Gestion des erreurs 429 (rate limiting)
- ✅ Reprise après interruption
- ✅ Statistiques en temps réel

### Backend / Services
- ✅ Pagination, filtres, recherche
- ✅ Agrégations statistiques (marques, accords)
- ✅ Parfums aléatoires et récents

### API REST
- ✅ 9 endpoints JSON documentés
- ✅ Gestion d'erreurs standardisée
- ✅ Limites de pagination (max 100/page)

### Frontend Flask
- ✅ Liste & détail des parfums
- ✅ Navigation par marque / accord
- ✅ Recherche full-text
- ✅ Statistiques visuelles
- ✅ Pages d'erreur personnalisées

### Infrastructure
- ✅ Docker Compose (MongoDB, Scraper, Webapp, Mongo Express)
- ✅ Variables d'environnement centralisées
- ✅ Health checks automatiques
- ✅ Volumes persistants

---

## 🗂 Structure du projet

```
fragrantica/
│
├── fragrantica_scraper/         # Projet Scrapy
│   ├── spiders/
│   │   ├── perfume_urls_spider.py    # Collecte URLs
│   │   └── perfume_data_spider.py    # Scrape données détaillées
│   ├── items.py                 # FragranticaPerfumeItem
│   ├── pipelines.py             # Nettoyage + MongoDB
│   └── settings.py              # Config Scrapy
│
├── webapp/                      # Application Flask
│   ├── routes/
│   │   ├── main.py              # Routes UI
│   │   ├── perfumes.py          # Routes parfums
│   │   └── api.py               # 9 endpoints REST
│   ├── services/
│   │   ├── perfume_service.py   # Logique métier parfums
│   │   └── stats_service.py     # Agrégations stats
│   ├── models/
│   │   └── perfume.py           # Modèle Perfume
│   ├── utils/
│   │   ├── db.py                # Connexion MongoDB
│   │   └── formatters.py        # Helpers
│   ├── templates/               # Jinja2 (10+ pages)
│   ├── static/                  # CSS/JS/images
│   ├── app.py                   # Point d'entrée
│   └── config.py                # Configuration Flask
│
├── scripts/
│   └── mongo_utils.py           # CLI MongoDB (stats, export, reset)
│
├── data/                        # Exports JSON
├── crawls/                      # États Scrapy
├── logs/                        # Logs scraping
│
├── run_scrapers.py              # Orchestrateur de scraping
├── docker-compose.yml           # 4 services
├── Dockerfile                   # Image scraper
├── Dockerfile.webapp            # Image Flask
├── requirements.txt             # Dépendances scraper
├── requirements-webapp.txt      # Dépendances Flask
├── .env.example                 # Template config
└── scrapy.cfg
```

---

## 💻 Prérequis

### Obligatoires
- **Python 3.11+**
- **Docker** + **Docker Compose**
- **Ports disponibles** : 5000 (Flask), 27017 (MongoDB), 8081 (Mongo Express)

### Optionnels
- Linux/Mac : scripts `.sh` fonctionnent nativement
- Windows : scripts `.bat` ou WSL2

---

## 🚀 Installation & Démarrage

### 1️⃣ Configuration initiale

```bash
# Cloner le projet
git clone <votre-repo>
cd fragrantica

# Copier et adapter la config
cp .env.example .env
```

**Variables d'environnement** (`.env`) :
```bash
# MongoDB
MONGO_USER=admin
MONGO_PASSWORD=password123
MONGO_DATABASE=fragrantica

# Mongo Express (interface web)
MONGOEXPRESS_LOGIN=admin
MONGOEXPRESS_PASSWORD=pass

# Flask (production uniquement)
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=changez-moi-en-production
```
---

### 2️⃣ Démarrage avec Docker

#### Lancer le scraping

```bash
# Linux/Mac
./start-scraper.sh

# Windows
.\start-scraper.bat
```

**Services lancés** :
- `mongodb` (port 27017)
- `mongo-express` (http://localhost:8081)
- `scraper` (exécute `run_scrapers.py`)

#### Lancer l'application web

```bash
# Linux/Mac
./start-webapp.sh

# Windows
.\start-webapp.bat
```

**Service lancé** :
- `webapp` (http://localhost:5000)


---

## 🌐 API REST

Base URL : `http://localhost:5000/api`

### Endpoints disponibles

#### 📦 Parfums

| Endpoint | Méthode | Description | Paramètres |
|----------|---------|-------------|------------|
| `/api/perfumes` | GET | Liste paginée de parfums | `page`, `per_page`, `brand`, `search` |
| `/api/perfumes/<id>` | GET | Détail d'un parfum | - |
| `/api/search` | GET | Recherche full-text | `q` (requis), `limit` |
| `/api/random` | GET | Parfums aléatoires | `limit` (max 50) |

#### 🏷 Marques & Accords

| Endpoint | Méthode | Description | Paramètres |
|----------|---------|-------------|------------|
| `/api/brands` | GET | Liste des marques + stats | - |
| `/api/brands/<name>` | GET | Parfums d'une marque | `page`, `per_page` |
| `/api/accords` | GET | Liste des accords + stats | - |

#### 📊 Statistiques

| Endpoint | Méthode | Description | Paramètres |
|----------|---------|-------------|------------|
| `/api/stats` | GET | Statistiques globales | - |

---

### Exemples de requêtes

#### Lister les parfums (pagination)

```bash
curl "http://localhost:5000/api/perfumes?page=1&per_page=10"
```

**Réponse** :
```json
{
  "success": true,
  "data": [
    {
      "id": "507f1f77bcf86cd799439011",
      "name": "Sauvage",
      "brand": "Dior",
      "accords": {"fresh": 80, "woody": 60},
      "url": "https://www.fragrantica.com/perfume/Dior/Sauvage.html",
      "image_url": "https://..."
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 1247,
    "pages": 125
  }
}
```

#### Rechercher des parfums

```bash
curl "http://localhost:5000/api/search?q=chanel&limit=5"
```

**Réponse** :
```json
{
  "success": true,
  "count": 5,
  "data": [...]
}
```

#### Obtenir des parfums aléatoires

```bash
curl "http://localhost:5000/api/random?limit=3"
```

#### Statistiques par marque

```bash
curl "http://localhost:5000/api/brands"
```

**Réponse** :
```json
{
  "success": true,
  "data": [
    {"brand": "Dior", "count": 45},
    {"brand": "Chanel", "count": 38},
    ...
  ]
}
```

#### Statistiques globales

```bash
curl "http://localhost:5000/api/stats"
```

---

### Format des erreurs

```json
{
  "success": false,
  "error": "Resource not found"
}
```

**Codes HTTP** :
- `200` : Succès
- `400` : Paramètre manquant/invalide
- `404` : Ressource introuvable
- `500` : Erreur serveur

---

## 🛠 Scripts utilitaires

Le script `scripts/mongo_utils.py` fournit des outils CLI pour gérer MongoDB.

### Commandes disponibles

```bash
# Afficher les statistiques
python scripts/mongo_utils.py stats

# Exporter les données
python scripts/mongo_utils.py export-urls     # URLs -> data/perfume_urls.json
python scripts/mongo_utils.py export-data     # Parfums -> data/perfume_data.json
python scripts/mongo_utils.py export-all      # Les deux

# Réinitialiser (avec confirmation)
python scripts/mongo_utils.py reset-urls      # Vider la collection URLs
python scripts/mongo_utils.py reset-data      # Vider la collection parfums
```

### Exemple de sortie (stats)

```
======================================================================
📊 Fragrantica MongoDB Statistics
======================================================================

Perfume URLs collected:    2,847
Unique brands:             124

Perfumes scraped:          1,523

Top 5 brands:
  1. Dior: 67 perfumes
  2. Chanel: 54 perfumes
  3. Guerlain: 48 perfumes
  4. Tom Ford: 42 perfumes
  5. Hermès: 39 perfumes

──────────────────────────────────────────────────────────────────────
Remaining to scrape:       1,324
Progress:                  53.5%
======================================================================
```

---

## 📊 Structure des données

### Item Scrapy (`items.py`)

```python
class FragranticaPerfumeItem(scrapy.Item):
    name = scrapy.Field()        # Nom du parfum
    brand = scrapy.Field()       # Marque
    accords = scrapy.Field()     # Dict {accord: pourcentage}
    url = scrapy.Field()         # URL Fragrantica
    image_url = scrapy.Field()   # URL de l'image
```

### Exemple de document MongoDB

```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "Sauvage Eau de Toilette",
  "brand": "Dior",
  "accords": {
    "fresh": 40.1,
    "woody": 30.2,
    "citrus": 20.3,
    "aromatic": 9.4
  },
  "url": "https://www.fragrantica.com/perfume/Dior/Sauvage-31861.html",
  "image_url": "https://fimgs.net/mdimg/perfume/375x500.31861.jpg"
}
```

### Collections MongoDB

- **`perfume_urls`** : URLs collectées par le premier spider
  - Champs : `url`, `designer`, `name`
  
- **`perfume_data`** : Données complètes scrapées
  - Champs : `name`, `brand`, `accords`, `url`, `image_url`

---

## 🔧 Architecture Docker

### Services (`docker-compose.yml`)

| Service | Image | Port | Rôle |
|---------|-------|------|------|
| `mongodb` | mongo:7.0 | 27017 (interne) | Base de données |
| `mongo-express` | mongo-express:latest | 8081 | Interface web MongoDB |
| `scraper` | build: Dockerfile | - | Scraping Scrapy |
| `webapp` | build: Dockerfile.webapp | 5000 | Application Flask |

### Volumes persistants

- **`mongodb_data`** : Données MongoDB
- **`mongodb_config`** : Configuration MongoDB
- **Bind mounts** : `./data`, `./crawls`, `./logs`, `./webapp`

### Réseau

- **`fragrantica_network`** : Réseau bridge interne
- Les services communiquent via leurs noms (ex: `mongodb:27017`)

### Health checks

```yaml
# MongoDB
test: mongosh localhost:27017/test --eval 'db.runCommand("ping")'

# Webapp
test: curl -f http://localhost:5000/api/stats
```

---

## 📈 Métriques typiques

Sur une exécution complète (durée variable selon rate limiting) :

- **URLs collectées** : ~200-1,000
- **Parfums scrapés** : ~20-400
- **Marques uniques** : ~120
- **Accords distincts** : ~30-80
- **Temps de scraping total** : 1-6 heures (avec pauses 429)

---

## 🎯 Cas d'usage

### Analyse de marché
```bash
curl http://localhost:5000/api/brands | jq '.data[] | select(.count > 50)'
```

### Export pour ML/Data Science
```bash
python scripts/mongo_utils.py export-all
# → data/perfume_data.json
```

### Intégration dans un dashboard
```python
import requests
response = requests.get('http://localhost:5000/api/stats')
stats = response.json()['data']
```

---

## ⚠️ Disclaimer

Les données proviennent de **fragrantica.com**.  
Ce projet est réalisé dans un contexte de data engineering.

---

## 🎓 Projet académique

**Fragrantica Explorer** ─ Projet Data Engineering E4 ESIEE

---

**Contributeurs** : Lucas TONLOP, Lubin BENOIT
**Dernière mise à jour** : Février 2026  
**Version** : 1.0.0