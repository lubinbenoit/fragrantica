# perfume_spider_resumable.py
import scrapy
import re
import json
from pathlib import Path
from fragrantica_scraper.items import FragranticaPerfumeItem

class PerfumeSpider(scrapy.Spider):
    name = "perfume_data"
    allowed_domains = ["fragrantica.com"]
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 10,  # 10 secondes entre chaque requête
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 10,
        'AUTOTHROTTLE_MAX_DELAY': 30,
        'COOKIES_ENABLED': True,
        'RETRY_ENABLED': False,  # Pas de retry, on passe au suivant
        'DOWNLOADER_MIDDLEWARES': {
            'fragrantica_scraper.middlewares.StopOn429Middleware': 543,
        },
        'LOG_LEVEL': 'INFO',
        # Sauvegarder l'état pour pouvoir reprendre
        'JOBDIR': 'crawls/perfume_data',
    }
    
    async def start(self):
        """Load URLs and skip already scraped ones."""
        # Charger les URLs à scraper
        with open("data/perfume_urls.json", "r", encoding="utf-8") as f:
            all_urls = json.load(f)
        
        # Charger les URLs déjà scrapées
        scraped_urls = set()
        output_file = Path("data/perfume_data.json")
        if output_file.exists():
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                    scraped_urls = {item.get("url") for item in existing_data if item.get("url")}
                self.logger.info(f"Found {len(scraped_urls)} already scraped perfumes")
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Ne scraper que les URLs non encore faites
        remaining = [u for u in all_urls if u["perfume_url"] not in scraped_urls]
        self.logger.info(f"Total URLs: {len(all_urls)}, Already scraped: {len(scraped_urls)}, Remaining: {len(remaining)}")
        
        for data in remaining:
            url = data["perfume_url"]
            designer = data.get("designer", "Unknown")
            yield scrapy.Request(
                url,
                callback=self.parse_perfume,
                meta={"designer": designer},
                errback=self.handle_error,
            )
    
    def parse_perfume(self, response):
        """Parse individual perfume page."""
        item = FragranticaPerfumeItem()
        item["url"] = response.url
        
        # Nom et marque
        title = response.css("h1::text").get()
        if title:
            title = title.strip()
            item["name"] = title
            item["brand"] = response.meta.get("designer", title.split(" ", 1)[0])
        else:
            item["name"] = "Unknown"
            item["brand"] = response.meta.get("designer", "Unknown")
        
        # Accords
        accords = {}
        for bar in response.css("div.flex.flex-col.w-full > div.w-full > div"):
            name = bar.css("span.truncate::text").get()
            style = bar.attrib.get("style", "")
            match = re.search(r"width:\s*([\d.]+)%", style)
            if name and match:
                accords[name.strip()] = float(match.group(1))
        
        item["accords"] = accords
        
        # Log progress
        self.logger.info(f"✓ Scraped: {item['brand']} - {item['name']}")
        
        yield item
    
    def handle_error(self, failure):
        """Handle errors gracefully."""
        self.logger.error(f"✗ Failed: {failure.request.url}")