"""
Application Flask principale.
Point d'entrée de l'application web.
"""
from flask import Flask, render_template
from webapp.config import get_config
from webapp.utils.db import init_db
from webapp.routes import main_bp, perfumes_bp, api_bp


def create_app(config_class=None):
    """
    Factory function pour créer l'application Flask.
    
    Args:
        config_class: Classe de configuration (optionnel)
    
    Returns:
        Flask: Instance de l'application Flask
    """
    app = Flask(__name__)
    
    # Configuration
    if config_class is None:
        config_class = get_config()
    
    app.config.from_object(config_class)
    
    # Initialiser la connexion MongoDB
    init_db(app)
    
    # Enregistrer les blueprints (routes)
    app.register_blueprint(main_bp)
    app.register_blueprint(perfumes_bp)
    app.register_blueprint(api_bp)
    
    # Gestionnaires d'erreurs
    @app.errorhandler(404)
    def not_found(error):
        """Page 404 personnalisée."""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Page 500 personnalisée."""
        app.logger.error(f"Internal error: {error}")
        return render_template('errors/500.html'), 500
    
    # Template filters
    @app.template_filter('format_number')
    def format_number_filter(value):
        """Formate un nombre avec des séparateurs de milliers."""
        return f"{value:,}".replace(',', ' ')
    
    @app.template_filter('percentage')
    def percentage_filter(value, decimals=1):
        """Formate un nombre en pourcentage."""
        return f"{value:.{decimals}f}%"
    
    # Context processors (variables disponibles dans tous les templates)
    @app.context_processor
    def inject_globals():
        """Injecte des variables globales dans tous les templates."""
        return {
            'app_name': 'Fragrantica Explorer',
            'app_version': '1.0.0'
        }
    
    app.logger.info("✓ Flask application created successfully")
    
    return app


# Créer l'application
app = create_app()


if __name__ == '__main__':
    # Mode développement
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )