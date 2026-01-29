"""
Routes principales de l'application.
"""
from flask import Blueprint, render_template, request, current_app
from webapp.services import PerfumeService, StatsService

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Page d'accueil.
    Affiche des parfums mis en avant et les statistiques.
    """
    # Récupérer des parfums aléatoires pour la page d'accueil
    featured_perfumes = PerfumeService.get_random(limit=6)
    latest_perfumes = PerfumeService.get_latest(limit=12)
    
    # Statistiques globales
    stats = StatsService.get_overview()
    
    return render_template(
        'index.html',
        featured_perfumes=featured_perfumes,
        latest_perfumes=latest_perfumes,
        stats=stats
    )


@main_bp.route('/search')
def search():
    """
    Page de recherche.
    """
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']
    
    if not query:
        return render_template('search.html', results=None, query='')
    
    # Recherche dans les parfums
    results = PerfumeService.get_all(
        page=page,
        per_page=per_page,
        search=query
    )
    
    return render_template(
        'search.html',
        results=results,
        query=query
    )


@main_bp.route('/brands')
def brands():
    """
    Page listant toutes les marques.
    """
    brands_stats = StatsService.get_brands_stats()
    
    return render_template(
        'brands.html',
        brands=brands_stats
    )


@main_bp.route('/brand/<brand_name>')
def brand_detail(brand_name):
    """
    Page détaillant les parfums d'une marque.
    """
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']
    
    results = PerfumeService.get_by_brand(
        brand_name=brand_name,
        page=page,
        per_page=per_page
    )
    
    return render_template(
        'brand_detail.html',
        brand_name=brand_name,
        results=results
    )


@main_bp.route('/accord/<accord_name>')
def accord_detail(accord_name):
    """
    Page listant les parfums par accord.
    """
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['ITEMS_PER_PAGE']
    
    results = PerfumeService.get_by_accord(
        accord_name=accord_name,
        page=page,
        per_page=per_page
    )
    
    return render_template(
        'accord_detail.html',
        accord_name=accord_name,
        results=results
    )


@main_bp.route('/stats')
def stats():
    """
    Page de statistiques.
    """
    dashboard_data = StatsService.get_dashboard_data()
    
    return render_template(
        'stats.html',
        data=dashboard_data
    )


@main_bp.route('/about')
def about():
    """
    Page À propos.
    """
    return render_template('about.html')