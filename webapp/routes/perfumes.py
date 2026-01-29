"""
Routes pour les parfums.
"""
from flask import Blueprint, render_template, abort, request, current_app
from webapp.services import PerfumeService

perfumes_bp = Blueprint('perfumes', __name__, url_prefix='/perfumes')


@perfumes_bp.route('/')
def list_perfumes():
    """
    Liste tous les parfums avec pagination.
    """
    page = request.args.get('page', 1, type=int)
    brand = request.args.get('brand')
    per_page = current_app.config['ITEMS_PER_PAGE']
    
    results = PerfumeService.get_all(
        page=page,
        per_page=per_page,
        brand=brand
    )
    
    return render_template(
        'perfumes_list.html',
        results=results,
        brand=brand
    )


@perfumes_bp.route('/<perfume_id>')
def perfume_detail(perfume_id):
    """
    Page de détail d'un parfum.
    """
    perfume = PerfumeService.get_by_id(perfume_id)
    
    if not perfume:
        abort(404)
    
    # Récupérer des parfums similaires (même marque)
    similar = PerfumeService.get_by_brand(
        brand_name=perfume.brand,
        page=1,
        per_page=6
    )
    
    # Exclure le parfum actuel des similaires
    similar_perfumes = [
        p for p in similar['perfumes']
        if p.id != perfume.id
    ][:5]
    
    return render_template(
        'perfume_detail.html',
        perfume=perfume,
        similar_perfumes=similar_perfumes
    )