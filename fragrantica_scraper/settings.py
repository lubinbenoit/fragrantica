ROBOTSTXT_OBEY = False

BOT_NAME = 'fragrantica_scraper'

SPIDER_MODULES = ['fragrantica_scraper.spiders']
NEWSPIDER_MODULE = 'fragrantica_scraper.spiders'

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

DOWNLOAD_DELAY = 3
RANDOMIZE_DOWNLOAD_DELAY = True

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 3
AUTOTHROTTLE_MAX_DELAY = 15

COOKIES_ENABLED = True

