# middlewares.py
import random
from scrapy.exceptions import CloseSpider

class StopOn429Middleware:
    """Middleware to stop spider when encountering HTTP 429 (Too Many Requests)."""
    
    @classmethod
    def from_crawler(cls, crawler):
        """Create middleware instance with crawler reference."""
        middleware = cls()
        middleware.crawler = crawler
        return middleware
    
    def process_response(self, request, response, spider):
        """Check for 429 status and stop spider if detected."""
        if response.status == 429:
            spider.logger.warning(
                f"HTTP 429 (Too Many Requests) detected on {request.url}. "
                "Closing spider to avoid rate limiting."
            )
            raise CloseSpider("429_received")
        return response


class RotateUserAgentMiddleware:
    """Middleware to rotate user agents on each request."""
    
    def __init__(self, user_agents):
        self.user_agents = user_agents
    
    @classmethod
    def from_crawler(cls, crawler):
        """Get user agents from spider settings."""
        user_agents = getattr(crawler.spider, 'user_agents', [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ])
        return cls(user_agents)
    
    def process_request(self, request, spider):
        """Set a random user agent for each request."""
        request.headers['User-Agent'] = random.choice(self.user_agents)