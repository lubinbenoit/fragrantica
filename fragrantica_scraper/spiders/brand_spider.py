# brand_spider.py
import scrapy
import random
from scrapy.exceptions import CloseSpider, IgnoreRequest

class PerfumeURLsSpider(scrapy.Spider):
    name = "perfume_urls"
    allowed_domains = ["fragrantica.com"]
    start_urls = ["https://www.fragrantica.com/designers/"]
    
    # Paramètres spécifiques à ce spider
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0 Safari/537.36"
        ),
        'DOWNLOAD_DELAY': 2,  # Augmenté pour éviter le 429
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 2,
        'AUTOTHROTTLE_MAX_DELAY': 10,
        'CONCURRENT_REQUESTS': 2,
        'COOKIES_ENABLED': True,
        'RETRY_ENABLED': False,  # Désactive les retries automatiques
    }
    
    # Limite d'URLs par designer
    max_urls_per_designer = 10
    
    def parse(self, response):
        """Parse la page des designers et envoie une requête vers chaque designer."""
        designer_links = response.xpath(
            '//a[starts-with(@href, "/designers/") and contains(@href, ".html")]'
        )
        self.logger.info(f"{len(designer_links)} designers trouvés")
        
        for a in designer_links:
            designer_name = a.xpath("normalize-space(text())").get()
            designer_url = response.urljoin(a.attrib["href"])
            yield scrapy.Request(
                designer_url,
                callback=self.parse_designer,
                meta={"designer": designer_name},
                errback=self.handle_error,
                dont_filter=True
            )
    
    def parse_designer(self, response):
        """Parse la page d'un designer pour récupérer les URLs de ses parfums."""
        # Vérifier si on a reçu un 429
        if response.status == 429:
            self.logger.error("Erreur 429 détectée - Arrêt du spider")
            raise CloseSpider(reason="rate_limited_429")
        
        # Nom du designer propre
        designer = response.css("h1::text").get()
        if designer:
            designer = designer.replace(" perfumes and colognes", "").strip()
        else:
            designer = response.meta.get("designer", "Unknown")
        
        # Récupération des URLs des parfums
        perfume_links = list(set(response.xpath('//a[contains(@href, "/perfume/")]/@href').getall()))
        random.shuffle(perfume_links)
        
        # Limite par designer appliquée ici
        for link in perfume_links[:self.max_urls_per_designer]:
            yield {
                "designer": designer,
                "perfume_url": response.urljoin(link)
            }
        
        self.logger.info(f"{designer}: {min(len(perfume_links), self.max_urls_per_designer)} parfums collectés")
    
    def handle_error(self, failure):
        """Gère les erreurs de requête."""
        request = failure.request
        
        if failure.check(scrapy.spidermiddlewares.httperror.HttpError):
            response = failure.value.response
            if response.status == 429:
                self.logger.error(f"Erreur 429 sur {request.url} - Arrêt du spider")
                raise CloseSpider(reason="rate_limited_429")
        
        self.logger.error(f"Erreur sur {request.url}: {failure}")