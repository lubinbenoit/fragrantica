# items.py
import scrapy

class FragranticaPerfumeItem(scrapy.Item):
    name = scrapy.Field()
    brand = scrapy.Field()
    accords = scrapy.Field()  # dict {accord: pourcentage}
    url = scrapy.Field()