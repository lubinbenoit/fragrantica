# perfume_urls_spider.py
import scrapy
import random
from scrapy.exceptions import CloseSpider
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
        'CONCURRENT_REQUESTS': 2,
        'COOKIES_ENABLED': True,
        'RETRY_ENABLED': False,
    }
    
    max_urls_per_designer = 10
    
    def __init__(self, *args, skip_existing=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.skip_existing = skip_existing
        
        if self.skip_existing:
            self.scraped_designers = self._load_scraped_designers()
            self.existing_urls = self._load_existing_urls()
            self.logger.info(
                f"Loaded {len(self.scraped_designers)} designers "
                f"and {len(self.existing_urls)} URLs from MongoDB"
            )
        else:
            self.scraped_designers = set()
            self.existing_urls = set()
    
    def _load_scraped_designers(self):
        """Charge la liste des designers avec au moins max_urls_per_designer URLs."""
        try:
            mongo_uri = self.settings.get('MONGO_URI', 'mongodb://localhost:27017/')
            mongo_db = self.settings.get('MONGO_DATABASE', 'fragrantica')
            
            client = MongoClient(mongo_uri)
            db = client[mongo_db]
            
            # Designers avec le nombre max d'URLs déjà collectées
            pipeline = [
                {"$group": {"_id": "$designer", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gte": self.max_urls_per_designer}}}
            ]
            
            fully_scraped = {
                doc["_id"] for doc in db.perfume_urls.aggregate(pipeline)
            }
            
            client.close()
            return fully_scraped
        
        except Exception as e:
            self.logger.warning(f"Could not load scraped designers: {e}")
            return set()
    
    def _load_existing_urls(self):
        """Charge toutes les URLs déjà présentes en base."""
        try:
            mongo_uri = self.settings.get('MONGO_URI', 'mongodb://localhost:27017/')
            mongo_db = self.settings.get('MONGO_DATABASE', 'fragrantica')
            
            client = MongoClient(mongo_uri)
            db = client[mongo_db]
            
            existing_urls = set(
                doc["perfume_url"] 
                for doc in db.perfume_urls.find({}, {"perfume_url": 1, "_id": 0})
            )
            
            client.close()
            return existing_urls
        
        except Exception as e:
            self.logger.warning(f"Could not load existing URLs: {e}")
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
            
            # Skip si déjà complètement scrapé
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
            self.logger.error("Erreur 429 détectée - Arrêt du spider")
            raise CloseSpider(reason="rate_limited_429")
        
        designer = response.css("h1::text").get()
        if designer:
            designer = designer.replace(" perfumes and colognes", "").strip()
        else:
            designer = response.meta.get("designer", "Unknown")
        
        # Récupération des URLs des parfums
        perfume_links = list(set(
            response.xpath('//a[contains(@href, "/perfume/")]/@href').getall()
        ))
        random.shuffle(perfume_links)
        
        # Filtrer les URLs déjà présentes
        new_urls = []
        for link in perfume_links[:self.max_urls_per_designer]:
            full_url = response.urljoin(link)
            if full_url not in self.existing_urls:
                new_urls.append(full_url)
                yield {
                    "designer": designer,
                    "perfume_url": full_url
                }
        
        self.logger.info(
            f"{designer}: {len(new_urls)} new URLs collected "
            f"(total found: {len(perfume_links)})"
        )
    
    def handle_error(self, failure):
        """Gère les erreurs de requête."""
        request = failure.request
        
        if failure.check(scrapy.spidermiddlewares.httperror.HttpError):
            response = failure.value.response
            if response.status == 429:
                self.logger.error(f"Erreur 429 sur {request.url} - Arrêt du spider")
                raise CloseSpider(reason="rate_limited_429")
        
        self.logger.error(f"Erreur sur {request.url}: {failure}")