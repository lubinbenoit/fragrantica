# perfume_data_spider.py
import scrapy
import re
from pymongo import MongoClient
from fragrantica_scraper.items import FragranticaPerfumeItem


class PerfumeSpider(scrapy.Spider):
    name = "perfume_data"
    allowed_domains = ["fragrantica.com"]
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 6,
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 3,
        'AUTOTHROTTLE_MAX_DELAY': 20,
        'COOKIES_ENABLED': True,
        'RETRY_ENABLED': False,
        'DOWNLOADER_MIDDLEWARES': {
            'fragrantica_scraper.middlewares.StopOn429Middleware': 543,
        },
        'LOG_LEVEL': 'INFO',
    }
    
    def start_requests(self):
        """Load URLs from MongoDB and skip already scraped ones."""
        # ✅ Valeur par défaut Docker-friendly
        mongo_uri = self.settings.get(
            'MONGO_URI', 
            'mongodb://admin:password123@mongodb:27017/'
        )
        mongo_db = self.settings.get('MONGO_DATABASE', 'fragrantica')
        
        self.logger.info(f"Connecting to MongoDB: {mongo_uri}")
        
        try:
            client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000
            )
            
            # Test de connexion
            client.admin.command('ping')
            db = client[mongo_db]
            
            # Charger les URLs
            all_urls = list(db.perfume_urls.find(
                {}, 
                {"perfume_url": 1, "designer": 1, "_id": 0}
            ))
            
            # Charger les URLs déjà scrapées
            scraped_urls = set(
                item["url"] 
                for item in db.perfume_data.find({}, {"url": 1, "_id": 0})
            )
            
            self.logger.info(f"Found {len(scraped_urls)} already scraped perfumes")
            
            # Calculer les URLs restantes
            remaining = [
                u for u in all_urls 
                if u["perfume_url"] not in scraped_urls
            ]
            
            self.logger.info(
                f"Total URLs: {len(all_urls)}, "
                f"Already scraped: {len(scraped_urls)}, "
                f"Remaining: {len(remaining)}"
            )
            
            # Générer les requêtes
            for data in remaining:
                url = data["perfume_url"]
                designer = data.get("designer", "Unknown")
                yield scrapy.Request(
                    url,
                    callback=self.parse_perfume,
                    meta={"designer": designer},
                    errback=self.handle_error,
                    dont_filter=True
                )
        
        except Exception as e:
            self.logger.error(f"MongoDB connection failed: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise
        
        finally:
            client.close()
    
    def parse_perfume(self, response):
        """Parse individual perfume page."""
        item = FragranticaPerfumeItem()
        item["url"] = response.url
        
        title = response.css("h1::text").get()
        if title:
            title = title.strip()
            item["name"] = title
            item["brand"] = response.meta.get("designer", title.split(" ", 1)[0])
        else:
            item["name"] = "Unknown"
            item["brand"] = response.meta.get("designer", "Unknown")
        
        accords = {}
        for bar in response.css("div.flex.flex-col.w-full > div.w-full > div"):
            name = bar.css("span.truncate::text").get()
            style = bar.attrib.get("style", "")
            match = re.search(r"width:\s*([\d.]+)%", style)
            if name and match:
                accords[name.strip()] = float(match.group(1))
        
        item["accords"] = accords
        
        self.logger.info(f"✓ Scraped: {item['brand']} - {item['name']}")
        
        yield item
    
    def handle_error(self, failure):
        """Handle errors gracefully."""
        self.logger.error(f"✗ Failed: {failure.request.url}")