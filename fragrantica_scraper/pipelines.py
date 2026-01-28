# pipelines.py
import logging
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from itemadapter import ItemAdapter


class MongoPerfumeURLsPipeline:
    """Pipeline pour sauvegarder les URLs de parfums dans MongoDB."""
    
    collection_name = "perfume_urls"
    
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @classmethod
    def from_crawler(cls, crawler):
        """Récupère la config depuis settings.py"""
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017/'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'fragrantica')
        )
    
    def open_spider(self, spider):
        """Connexion à MongoDB au démarrage du spider."""
        if spider.name != "perfume_urls":
            return
        
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            
            # Créer un index unique sur perfume_url pour éviter les doublons
            self.db[self.collection_name].create_index("perfume_url", unique=True)
            
            self.logger.info(f"✓ Connected to MongoDB: {self.mongo_db}.{self.collection_name}")
        except PyMongoError as e:
            self.logger.error(f"✗ MongoDB connection failed: {e}")
            raise
    
    def close_spider(self, spider):
        """Fermeture de la connexion MongoDB."""
        if spider.name != "perfume_urls" or not self.client:
            return
        
        self.client.close()
        self.logger.info("✓ MongoDB connection closed")
    
    def process_item(self, item, spider):
        """Sauvegarde l'item dans MongoDB."""
        if spider.name != "perfume_urls":
            return item
        
        try:
            adapter = ItemAdapter(item)
            self.db[self.collection_name].insert_one(dict(adapter))
            self.logger.debug(f"✓ Inserted URL: {item.get('perfume_url')}")
        except DuplicateKeyError:
            self.logger.debug(f"⊘ Duplicate URL skipped: {item.get('perfume_url')}")
        except PyMongoError as e:
            self.logger.error(f"✗ MongoDB insert error: {e}")
        
        return item


class MongoPerfumeDataPipeline:
    """Pipeline pour sauvegarder les données détaillées de parfums dans MongoDB."""
    
    collection_name = "perfume_data"
    
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None
        self.db = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self.items_saved = 0
        self.items_skipped = 0
    
    @classmethod
    def from_crawler(cls, crawler):
        """Récupère la config depuis settings.py"""
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI', 'mongodb://localhost:27017/'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'fragrantica')
        )
    
    def open_spider(self, spider):
        """Connexion à MongoDB au démarrage du spider."""
        if spider.name != "perfume_data":
            return
        
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            
            # Index unique sur l'URL du parfum
            self.db[self.collection_name].create_index("url", unique=True)
            
            # Index sur la marque pour les requêtes fréquentes
            self.db[self.collection_name].create_index("brand")
            
            self.logger.info(f"✓ Connected to MongoDB: {self.mongo_db}.{self.collection_name}")
        except PyMongoError as e:
            self.logger.error(f"✗ MongoDB connection failed: {e}")
            raise
    
    def close_spider(self, spider):
        """Fermeture de la connexion et statistiques."""
        if spider.name != "perfume_data" or not self.client:
            return
        
        self.logger.info(
            f"✓ Pipeline stats: {self.items_saved} saved, "
            f"{self.items_skipped} duplicates skipped"
        )
        self.client.close()
        self.logger.info("✓ MongoDB connection closed")
    
    def process_item(self, item, spider):
        """Sauvegarde l'item dans MongoDB."""
        if spider.name != "perfume_data":
            return item
        
        try:
            adapter = ItemAdapter(item)
            self.db[self.collection_name].insert_one(dict(adapter))
            self.items_saved += 1
            
            if self.items_saved % 10 == 0:
                self.logger.info(f"Progress: {self.items_saved} perfumes saved")
        
        except DuplicateKeyError:
            self.items_skipped += 1
            self.logger.debug(f"⊘ Duplicate perfume skipped: {item.get('url')}")
        
        except PyMongoError as e:
            self.logger.error(f"✗ MongoDB insert error for {item.get('url')}: {e}")
        
        return item


class DataCleaningPipeline:
    """Pipeline optionnel pour nettoyer/valider les données avant sauvegarde."""
    
    def process_item(self, item, spider):
        """Nettoie et valide les données."""
        adapter = ItemAdapter(item)
        
        # Nettoyer les espaces dans le nom
        if adapter.get('name'):
            adapter['name'] = adapter['name'].strip()
        
        # Nettoyer la marque
        if adapter.get('brand'):
            adapter['brand'] = adapter['brand'].strip()
        
        # Valider que les accords sont bien un dictionnaire
        if spider.name == "perfume_data":
            if not isinstance(adapter.get('accords'), dict):
                adapter['accords'] = {}
        
        return item