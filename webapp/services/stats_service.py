"""
Service de statistiques pour l'application.
"""
from flask import current_app
from webapp.utils.db import get_db


class StatsService:
    """Service pour les statistiques de la base de données."""
    
    @staticmethod
    def get_overview():
        """
        Récupère les statistiques générales de la base.
        
        Returns:
            dict: Statistiques globales
        """
        db = get_db()
        
        # Collections
        urls_collection = db[current_app.config['COLLECTION_URLS']]
        data_collection = db[current_app.config['COLLECTION_DATA']]
        
        # Comptages
        urls_count = urls_collection.count_documents({})
        data_count = data_collection.count_documents({})
        
        # Progression
        progress = (data_count / urls_count * 100) if urls_count > 0 else 0
        remaining = urls_count - data_count
        
        return {
            'total_urls': urls_count,
            'total_perfumes': data_count,
            'remaining': remaining,
            'progress': round(progress, 2)
        }
    
    @staticmethod
    def get_brands_stats():
        """
        Récupère les statistiques par marque.
        
        Returns:
            dict: {
                'total_brands': int,
                'top_brands': list[dict],
                'all_brands': list[str]
            }
        """
        db = get_db()
        collection = db[current_app.config['COLLECTION_DATA']]
        
        # Pipeline d'agrégation pour les marques
        pipeline = [
            {
                '$group': {
                    '_id': '$brand',
                    'count': {'$sum': 1}
                }
            },
            {
                '$sort': {'count': -1}
            }
        ]
        
        results = list(collection.aggregate(pipeline))
        
        # Top 10 marques
        top_brands = [
            {'name': r['_id'], 'count': r['count']}
            for r in results[:10]
        ]
        
        # Liste complète des marques
        all_brands = sorted([r['_id'] for r in results])
        
        return {
            'total_brands': len(results),
            'top_brands': top_brands,
            'all_brands': all_brands
        }
    
    @staticmethod
    def get_accords_stats():
        """
        Récupère les statistiques sur les accords.
        
        Returns:
            dict: Statistiques des accords
        """
        db = get_db()
        collection = db[current_app.config['COLLECTION_DATA']]
        
        # Récupérer tous les accords
        all_accords = {}
        
        for doc in collection.find({}, {'accords': 1}):
            accords = doc.get('accords', {})
            for accord, value in accords.items():
                if accord not in all_accords:
                    all_accords[accord] = {
                        'count': 0,
                        'total_value': 0,
                        'max_value': 0
                    }
                
                all_accords[accord]['count'] += 1
                all_accords[accord]['total_value'] += value
                all_accords[accord]['max_value'] = max(
                    all_accords[accord]['max_value'],
                    value
                )
        
        # Calculer les moyennes et trier
        accords_list = []
        for accord, stats in all_accords.items():
            avg_value = stats['total_value'] / stats['count']
            accords_list.append({
                'name': accord,
                'count': stats['count'],
                'avg_value': round(avg_value, 2),
                'max_value': stats['max_value']
            })
        
        # Trier par nombre d'occurrences
        accords_list.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'total_accords': len(all_accords),
            'top_accords': accords_list[:15],
            'all_accords': accords_list
        }
    
    @staticmethod
    def get_dashboard_data():
        """
        Récupère toutes les données pour le dashboard.
        
        Returns:
            dict: Données complètes pour le dashboard
        """
        overview = StatsService.get_overview()
        brands = StatsService.get_brands_stats()
        accords = StatsService.get_accords_stats()
        
        return {
            'overview': overview,
            'brands': brands,
            'accords': accords
        }
    
    @staticmethod
    def search_brand(query):
        """
        Recherche de marques par nom.
        
        Args:
            query (str): Terme de recherche
        
        Returns:
            list[str]: Liste des marques correspondantes
        """
        db = get_db()
        collection = db[current_app.config['COLLECTION_DATA']]
        
        # Recherche case-insensitive
        brands = collection.distinct('brand', {
            'brand': {'$regex': query, '$options': 'i'}
        })
        
        return sorted(brands)