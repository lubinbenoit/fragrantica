import scrapy
from fragrantica_scraper.items import FragranticaPerfumeItem
import re

class FragranticaSpider(scrapy.Spider):
    name = "fragrantica"
    allowed_domains = ["fragrantica.com"]
    start_urls = [
        "https://www.fragrantica.com/perfume/Yves-Saint-Laurent/Y-100.html"
    ]

    def parse(self, response):
        item = FragranticaPerfumeItem()

        item["url"] = response.url
        item["name"] = response.css("h1::text").get()
        item["brand"] = response.css(".perfume-brand::text").get()

        accords = {}

        for accord in response.css(".accord-bar"):
            name = accord.css(".accord-name::text").get()
            style = accord.css(".accord-value::attr(style)").get()

            if style:
                percentage = re.search(r"width:\s*(\d+)%", style)
                if percentage:
                    accords[name] = int(percentage.group(1))

        item["accords"] = accords

        yield item