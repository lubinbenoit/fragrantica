# items.py
import scrapy

class FragranticaPerfumeItem(scrapy.Item):
    name = scrapy.Field()
    brand = scrapy.Field()
    accords = scrapy.Field()  # dict {accord: pourcentage}
    url = scrapy.Field()

    image_url = scrapy.Field() # URL de l'image du parfum