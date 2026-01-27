import scrapy
import re
from fragrantica_scraper.items import FragranticaPerfumeItem


class FragranticaSpider(scrapy.Spider):
    name = "fragrantica"
    allowed_domains = ["fragrantica.com"]
    start_urls = [
        "https://www.fragrantica.com/perfume/Yves-Saint-Laurent/Y-100.html"
    ]

    def parse(self, response):
        item = FragranticaPerfumeItem()

        item["url"] = response.url
        
        # item["name"] = response.css("h1::text").get().strip()[2:] # response.css("h1::text").get().strip()
        # brand est dans itemprop="brand"
        #item["brand"] = response.css('[itemprop="brand"]::text').get()

        title = response.css("h1::text").get().strip()
        item["name"] = title
        item["brand"] = title.split(" ", 1)[1] if " " in title else None
        
        accords = {}

        for bar in response.xpath('//div[contains(@style, "width")]'):
            name = bar.xpath('.//span[@class="truncate"]/text()').get()
            style = bar.attrib.get("style", "")

            match = re.search(r'width:\s*([\d.]+)%', style)
            if name and match:
                accords[name.strip()] = float(match.group(1))
            item["accords"] = accords

        yield item
