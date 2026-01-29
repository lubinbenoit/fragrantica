# perfume_urls_spider.py
import scrapy
import random
from pymongo import MongoClient


class PerfumeURLsSpider(scrapy.Spider):
    name = "perfume_urls"
    allowed_domains = ["fragrantica.com"]
    start_urls = ["https://www.fragrantica.com/designers/"]
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 4,
        'COOKIES_ENABLED': True,
        'RETRY_ENABLED': False,
    }
    
    max_urls_per_designer = 100
    
    def __init__(self, *args, skip_existing=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.skip_existing = skip_existing
        self.got_429 = False
        
        # ✅ NE PAS charger le cache ici - self.settings n'existe pas encore
        self.scraped_designers = set()
        self.existing_urls = set()
    
    # ✅ NOUVEAU : Charger le cache quand le spider démarre
    def start_requests(self):
        """Charge le cache avant de démarrer le scraping."""
        if self.skip_existing:
            self.scraped_designers = self._load_scraped_designers()
            self.existing_urls = self._load_existing_urls()
            self.logger.info(
                f"Loaded {len(self.scraped_designers)} fully scraped designers "
                f"and {len(self.existing_urls)} existing URLs from MongoDB"
            )
        
        # ✅ Maintenant on peut démarrer les requêtes normalement
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)
    
    def _get_mongo_connection(self):
        """Crée une connexion MongoDB avec les bons paramètres."""
        # ✅ Maintenant self.settings existe
        mongo_uri = self.settings.get(
            'MONGO_URI', 
            'mongodb://admin:password123@mongodb:27017/'
        )
        
        self.logger.debug(f"Connecting to MongoDB: {mongo_uri}")
        
        try:
            client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            # Test de connexion
            client.admin.command('ping')
            return client
        except Exception as e:
            self.logger.error(f"MongoDB connection failed: {e}")
            raise
    
    def _load_scraped_designers(self):
        """Charge la liste des designers avec au moins max_urls_per_designer URLs."""
        try:
            client = self._get_mongo_connection()
            mongo_db = self.settings.get('MONGO_DATABASE', 'fragrantica')
            db = client[mongo_db]
            
            pipeline = [
                {"$group": {"_id": "$designer", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gte": self.max_urls_per_designer}}}
            ]
            
            fully_scraped = {
                doc["_id"] for doc in db.perfume_urls.aggregate(pipeline)
            }
            
            self.logger.info(f"📊 Found {len(fully_scraped)} fully scraped designers")
            
            client.close()
            return fully_scraped
        
        except Exception as e:
            self.logger.error(f"Could not load scraped designers: {e}")
            return set()
    
    def _load_existing_urls(self):
        """Charge toutes les URLs déjà présentes en base."""
        try:
            client = self._get_mongo_connection()
            mongo_db = self.settings.get('MONGO_DATABASE', 'fragrantica')
            db = client[mongo_db]
            
            # Compter d'abord
            total_count = db.perfume_urls.count_documents({})
            self.logger.info(f"📊 Total URLs in database: {total_count}")
            
            # Charger toutes les URLs
            existing_urls = set()
            cursor = db.perfume_urls.find({}, {"perfume_url": 1, "_id": 0})
            
            for doc in cursor:
                if "perfume_url" in doc:
                    # ✅ Normaliser l'URL lors du chargement
                    url = doc["perfume_url"].rstrip('/').split('?')[0]
                    existing_urls.add(url)
            
            self.logger.info(f"✅ Loaded {len(existing_urls)} unique URLs into memory")
            
            # ✅ DEBUG : Afficher quelques exemples
            if existing_urls:
                sample_urls = list(existing_urls)[:3]
                self.logger.info(f"📝 Sample URLs in cache:")
                for url in sample_urls:
                    self.logger.info(f"   - {url}")
            
            # Vérification de cohérence
            if len(existing_urls) != total_count:
                self.logger.warning(
                    f"⚠️  Mismatch: {total_count} docs in DB but {len(existing_urls)} unique URLs loaded"
                )
            
            client.close()
            return existing_urls
        
        except Exception as e:
            self.logger.error(f"❌ Could not load existing URLs: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return set()
    
    def parse(self, response):
        """Parse la page des designers et envoie une requête vers chaque designer."""
        designer_links = response.xpath(
            '//a[starts-with(@href, "/designers/") and contains(@href, ".html")]'
        )
        self.logger.info(f"{len(designer_links)} designers trouvés")
        
        skipped_count = 0
        requested_count = 0
        
        for a in designer_links:
            designer_name = a.xpath("normalize-space(text())").get()
            
            if designer_name in self.scraped_designers:
                skipped_count += 1
                self.logger.debug(
                    f"⊘ Skipping fully scraped designer: {designer_name}"
                )
                continue
            
            designer_url = response.urljoin(a.attrib["href"])
            requested_count += 1
            
            yield scrapy.Request(
                designer_url,
                callback=self.parse_designer,
                meta={"designer": designer_name},
                errback=self.handle_error,
                dont_filter=True
            )
        
        self.logger.info(
            f"✓ Designers: {requested_count} to scrape, "
            f"{skipped_count} fully done"
        )
    
    def parse_designer(self, response):
        """Parse la page d'un designer pour récupérer les URLs de ses parfums."""
        if response.status == 429:
            self.logger.warning(
                f"HTTP 429 détecté sur {response.url} - "
                "Le spider sera arrêté par le middleware"
            )
            self.got_429 = True
            return
        
        designer = response.css("h1::text").get()
        if designer:
            designer = designer.replace(" perfumes and colognes", "").strip()
        else:
            designer = response.meta.get("designer", "Unknown")
        
        perfume_links = list(set(
            response.xpath('//a[contains(@href, "/perfume/")]/@href').getall()
        ))
        random.shuffle(perfume_links)
        
        # Compter vraiment les nouvelles URLs
        new_urls = []
        duplicate_count = 0
        
        for link in perfume_links[:self.max_urls_per_designer]:
            full_url = response.urljoin(link)
            
            # ✅ Normaliser l'URL pour éviter les doublons
            normalized_url = full_url.rstrip('/').split('?')[0]
            
            # Vérifier si l'URL existe déjà
            if normalized_url not in self.existing_urls:
                new_urls.append(normalized_url)
                # Ajouter au set local pour éviter les doublons dans cette session
                self.existing_urls.add(normalized_url)
                
                yield {
                    "designer": designer,
                    "perfume_url": normalized_url
                }
            else:
                duplicate_count += 1
        
        # Log précis
        if new_urls:
            self.logger.info(
                f"{designer}: {len(new_urls)} new URLs collected "
                f"({duplicate_count} already in DB, total found: {len(perfume_links)})"
            )
        else:
            self.logger.info(
                f"{designer}: 0 new URLs - all {duplicate_count} already in DB "
                f"(total found: {len(perfume_links)})"
            )
    
    def handle_error(self, failure):
        """Gère les erreurs de requête de manière non-bloquante."""
        if "IgnoreRequest" in str(failure):
            return
        
        self.logger.debug(f"Requête ignorée: {failure.request.url}")
    
    def closed(self, reason):
        """Appelé quand le spider se ferme."""
        if reason == '429_received':
            self.logger.warning(
                "⚠️  Spider arrêté à cause du rate limiting (429). "
                "Les URLs collectées jusqu'ici ont été sauvegardées."
            )
            self.logger.info(
                "💡 Conseil: Relancez plus tard pour continuer "
                "(les URLs déjà collectées seront automatiquement skippées)"
            )