"""
Modèle Perfume pour l'application.
"""
from webapp.utils.formatters import format_accords, get_top_accords, extract_perfume_id


class Perfume:
    """
    Modèle représentant un parfum.
    """
    
    def __init__(self, data):
        """
        Initialise un parfum depuis les données MongoDB.
        
        Args:
            data (dict): Données du parfum depuis MongoDB
        """
        self._data = data
        self.id = str(data.get('_id', ''))
        self.url = data.get('url', '')
        self.name = data.get('name', 'Unknown')
        self.brand = data.get('brand', 'Unknown Brand')
        self.accords = data.get('accords', {})
        
        # Données optionnelles (pour extension future)
        self.description = data.get('description', '')
        self.notes = data.get('notes', {})
        self.rating = data.get('rating')
        self.image_url = data.get('image_url', '')
    
    @property
    def perfume_id(self):
        """Retourne l'ID du parfum extrait de l'URL."""
        return extract_perfume_id(self.url)
    
    @property
    def sorted_accords(self):
        """Retourne les accords triés par valeur décroissante."""
        return format_accords(self.accords)
    
    @property
    def top_accords(self, limit=5):
        """Retourne les 5 premiers accords."""
        return get_top_accords(self.accords, limit)
    
    @property
    def dominant_accord(self):
        """Retourne l'accord dominant."""
        if self.sorted_accords:
            return self.sorted_accords[0]
        return None
    
    def to_dict(self):
        """
        Convertit le parfum en dictionnaire (pour API JSON).
        
        Returns:
            dict: Représentation du parfum
        """
        return {
            'id': self.id,
            'perfume_id': self.perfume_id,
            'name': self.name,
            'brand': self.brand,
            'url': self.url,
            'accords': dict(self.sorted_accords),
            'dominant_accord': self.dominant_accord[0] if self.dominant_accord else None,
            'description': self.description,
            'rating': self.rating,
            'image_url': self.image_url
        }
    
    def __repr__(self):
        """Représentation du parfum."""
        return f"<Perfume {self.name} by {self.brand}>"
    
    @staticmethod
    def from_db(data):
        """
        Factory method pour créer un Perfume depuis MongoDB.
        
        Args:
            data (dict): Données MongoDB
        
        Returns:
            Perfume: Instance de Perfume
        """
        return Perfume(data) if data else None
    
    @staticmethod
    def list_from_db(data_list):
        """
        Convertit une liste de données MongoDB en liste de Perfume.
        
        Args:
            data_list (list): Liste de dictionnaires MongoDB
        
        Returns:
            list: Liste d'instances Perfume
        """
        return [Perfume(data) for data in data_list]