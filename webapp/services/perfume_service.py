"""
Service de gestion des parfums.
Contient toute la logique métier pour les requêtes de parfums.
"""
from flask import current_app
from webapp.utils.db import get_db
from webapp.models.perfume import Perfume


class PerfumeService:
    """Service pour gérer les opérations liées aux parfums."""
    
    @staticmethod
    def get_all(page=1, per_page=24, brand=None, search=None):
        """
        Récupère tous les parfums avec pagination et filtres optionnels.
        
        Args:
            page (int): Numéro de page
            per_page (int): Nombre d'éléments par page
            brand (str): Filtre par marque (optionnel)
            search (str): Recherche dans le nom (optionnel)
        
        Returns:
            dict: {
                'perfumes': list[Perfume],
                'total': int,
                'page': int,
                'pages': int,
                'per_page': int
            }
        """
        db = get_db()
        collection = db[current_app.config['COLLECTION_DATA']]
        
        # Construire le filtre
        query = {}
        if brand:
            query['brand'] = brand
        if search:
            query['name'] = {'$regex': search, '$options': 'i'}
        
        # Compter le total
        total = collection.count_documents(query)
        
        # Calculer la pagination
        skip = (page - 1) * per_page
        pages = (total + per_page - 1) // per_page  # Arrondi supérieur
        
        # Récupérer les données
        cursor = collection.find(query).skip(skip).limit(per_page)
        perfumes = Perfume.list_from_db(list(cursor))
        
        return {
            'perfumes': perfumes,
            'total': total,
            'page': page,
            'pages': pages,
            'per_page': per_page
        }
    
    @staticmethod
    def get_by_id(perfume_id):
        """
        Récupère un parfum par son ID MongoDB.
        
        Args:
            perfume_id (str): ID MongoDB du parfum
        
        Returns:
            Perfume: Instance Perfume ou None
        """
        from bson import ObjectId
        
        db = get_db()
        collection = db[current_app.config['COLLECTION_DATA']]
        
        try:
            data = collection.find_one({'_id': ObjectId(perfume_id)})
            return Perfume.from_db(data)
        except Exception as e:
            current_app.logger.error(f"Error fetching perfume {perfume_id}: {e}")
            return None
    
    @staticmethod
    def get_by_url(url):
        """
        Récupère un parfum par son URL.
        
        Args:
            url (str): URL du parfum
        
        Returns:
            Perfume: Instance Perfume ou None
        """
        db = get_db()
        collection = db[current_app.config['COLLECTION_DATA']]
        
        data = collection.find_one({'url': url})
        return Perfume.from_db(data)
    
    @staticmethod
    def search(query, limit=20):
        """
        Recherche de parfums par nom ou marque.
        
        Args:
            query (str): Terme de recherche
            limit (int): Nombre max de résultats
        
        Returns:
            list[Perfume]: Liste de parfums correspondants
        """
        db = get_db()
        collection = db[current_app.config['COLLECTION_DATA']]
        
        # Recherche dans le nom ou la marque (case-insensitive)
        search_query = {
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'brand': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        cursor = collection.find(search_query).limit(limit)
        return Perfume.list_from_db(list(cursor))
    
    @staticmethod
    def get_by_brand(brand_name, page=1, per_page=24):
        """
        Récupère tous les parfums d'une marque.
        
        Args:
            brand_name (str): Nom de la marque
            page (int): Numéro de page
            per_page (int): Nombre d'éléments par page
        
        Returns:
            dict: Résultats paginés
        """
        return PerfumeService.get_all(page=page, per_page=per_page, brand=brand_name)
    
    @staticmethod
    def get_by_accord(accord_name, page=1, per_page=24):
        """
        Récupère les parfums contenant un accord spécifique.
        
        Args:
            accord_name (str): Nom de l'accord
            page (int): Numéro de page
            per_page (int): Nombre d'éléments par page
        
        Returns:
            dict: Résultats paginés
        """
        db = get_db()
        collection = db[current_app.config['COLLECTION_DATA']]
        
        # Recherche les parfums qui ont cet accord
        query = {f'accords.{accord_name}': {'$exists': True}}
        
        total = collection.count_documents(query)
        skip = (page - 1) * per_page
        pages = (total + per_page - 1) // per_page
        
        cursor = collection.find(query).skip(skip).limit(per_page)
        perfumes = Perfume.list_from_db(list(cursor))
        
        return {
            'perfumes': perfumes,
            'total': total,
            'page': page,
            'pages': pages,
            'per_page': per_page
        }
    
    @staticmethod
    def get_random(limit=6):
        """
        Récupère des parfums aléatoires.
        
        Args:
            limit (int): Nombre de parfums à retourner
        
        Returns:
            list[Perfume]: Liste de parfums aléatoires
        """
        db = get_db()
        collection = db[current_app.config['COLLECTION_DATA']]
        
        pipeline = [{'$sample': {'size': limit}}]
        cursor = collection.aggregate(pipeline)
        
        return Perfume.list_from_db(list(cursor))
    
    @staticmethod
    def get_latest(limit=12):
        """
        Récupère les derniers parfums ajoutés.
        
        Args:
            limit (int): Nombre de parfums
        
        Returns:
            list[Perfume]: Liste des derniers parfums
        """
        db = get_db()
        collection = db[current_app.config['COLLECTION_DATA']]
        
        # Tri par _id décroissant (les plus récents)
        cursor = collection.find().sort('_id', -1).limit(limit)
        
        return Perfume.list_from_db(list(cursor))