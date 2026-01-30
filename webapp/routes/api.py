"""
Routes API REST pour l'application.
Permet l'accès programmatique aux données.
"""
from flask import Blueprint, jsonify, request, current_app
from webapp.services import PerfumeService, StatsService

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/perfumes')
def api_perfumes():
    """
    API: Liste des parfums.
    
    Query params:
        - page (int): Numéro de page
        - per_page (int): Nombre d'éléments par page
        - brand (str): Filtre par marque
        - search (str): Recherche
    
    Returns:
        JSON avec les parfums et métadonnées de pagination
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 24, type=int)
    brand = request.args.get('brand')
    search = request.args.get('search')
    
    # Limiter per_page pour éviter les abus
    per_page = min(per_page, 100)
    
    results = PerfumeService.get_all(
        page=page,
        per_page=per_page,
        brand=brand,
        search=search
    )
    
    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in results['perfumes']],
        'pagination': {
            'page': results['page'],
            'per_page': results['per_page'],
            'total': results['total'],
            'pages': results['pages']
        }
    })


@api_bp.route('/perfumes/<perfume_id>')
def api_perfume_detail(perfume_id):
    """
    API: Détail d'un parfum.
    
    Returns:
        JSON avec les détails du parfum
    """
    perfume = PerfumeService.get_by_id(perfume_id)
    
    if not perfume:
        return jsonify({
            'success': False,
            'error': 'Perfume not found'
        }), 404
    
    return jsonify({
        'success': True,
        'data': perfume.to_dict()
    })


@api_bp.route('/search')
def api_search():
    """
    API: Recherche de parfums.
    
    Query params:
        - q (str): Terme de recherche
        - limit (int): Nombre max de résultats
    
    Returns:
        JSON avec les résultats de recherche
    """
    query = request.args.get('q', '')
    limit = request.args.get('limit', 20, type=int)
    
    if not query:
        return jsonify({
            'success': False,
            'error': 'Query parameter "q" is required'
        }), 400
    
    # Limiter le nombre de résultats
    limit = min(limit, 100)
    
    results = PerfumeService.search(query, limit=limit)
    
    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in results],
        'count': len(results)
    })


@api_bp.route('/brands')
def api_brands():
    """
    API: Liste des marques.
    
    Returns:
        JSON avec les statistiques de marques
    """
    brands = StatsService.get_brands_stats()
    
    return jsonify({
        'success': True,
        'data': brands
    })


@api_bp.route('/brands/<brand_name>')
def api_brand_perfumes(brand_name):
    """
    API: Parfums d'une marque.
    
    Returns:
        JSON avec les parfums de la marque
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 24, type=int)
    per_page = min(per_page, 100)
    
    results = PerfumeService.get_by_brand(
        brand_name=brand_name,
        page=page,
        per_page=per_page
    )
    
    return jsonify({
        'success': True,
        'brand': brand_name,
        'data': [p.to_dict() for p in results['perfumes']],
        'pagination': {
            'page': results['page'],
            'per_page': results['per_page'],
            'total': results['total'],
            'pages': results['pages']
        }
    })


@api_bp.route('/accords')
def api_accords():
    """
    API: Liste des accords.
    
    Returns:
        JSON avec les statistiques d'accords
    """
    accords = StatsService.get_accords_stats()
    
    return jsonify({
        'success': True,
        'data': accords
    })


@api_bp.route('/stats')
def api_stats():
    """
    API: Statistiques globales.
    
    Returns:
        JSON avec toutes les statistiques
    """
    stats = StatsService.get_dashboard_data()
    
    return jsonify({
        'success': True,
        'data': stats
    })


@api_bp.route('/random')
def api_random():
    """
    API: Parfums aléatoires.
    
    Query params:
        - limit (int): Nombre de parfums (max 50)
    
    Returns:
        JSON avec des parfums aléatoires
    """
    limit = request.args.get('limit', 6, type=int)
    limit = min(limit, 50)
    
    perfumes = PerfumeService.get_random(limit=limit)
    
    return jsonify({
        'success': True,
        'data': [p.to_dict() for p in perfumes],
        'count': len(perfumes)
    })


# Error handlers pour l'API
@api_bp.errorhandler(404)
def api_not_found(error):
    """Gestion des erreurs 404 pour l'API."""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@api_bp.errorhandler(500)
def api_internal_error(error):
    """Gestion des erreurs 500 pour l'API."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500