"""
Fonctions utilitaires pour formater les données.
"""


def format_accords(accords_dict):
    """
    Formate les accords pour l'affichage.
    Trie par valeur décroissante et retourne une liste de tuples.
    
    Args:
        accords_dict (dict): Dictionnaire des accords {"accord": value}
    
    Returns:
        list: Liste triée de tuples (accord, value)
    """
    if not accords_dict:
        return []
    
    return sorted(
        accords_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )


def get_top_accords(accords_dict, limit=5):
    """
    Retourne les N premiers accords.
    
    Args:
        accords_dict (dict): Dictionnaire des accords
        limit (int): Nombre d'accords à retourner
    
    Returns:
        list: Liste des top accords
    """
    accords = format_accords(accords_dict)
    return accords[:limit]


def format_brand_name(brand_name):
    """
    Formate le nom de marque pour l'affichage.
    
    Args:
        brand_name (str): Nom de la marque
    
    Returns:
        str: Nom formaté
    """
    if not brand_name:
        return "Unknown Brand"
    
    return brand_name.strip()


def extract_perfume_id(url):
    """
    Extrait l'ID d'un parfum depuis son URL Fragrantica.
    
    Args:
        url (str): URL du parfum
    
    Returns:
        str: ID du parfum ou None
    
    Example:
        "https://www.fragrantica.com/perfume/Xerjoff/La-Tosca-32191.html"
        -> "32191"
    """
    if not url:
        return None
    
    try:
        # Extraire le numéro à la fin avant .html
        parts = url.rstrip('/').split('/')[-1].split('-')
        perfume_id = parts[-1].replace('.html', '')
        return perfume_id
    except (IndexError, AttributeError):
        return None


def format_percentage(value, decimals=1):
    """
    Formate un nombre en pourcentage.
    
    Args:
        value (float): Valeur à formater
        decimals (int): Nombre de décimales
    
    Returns:
        str: Pourcentage formaté
    """
    if value is None:
        return "0%"
    
    return f"{value:.{decimals}f}%"


def truncate_text(text, max_length=100, suffix="..."):
    """
    Tronque un texte s'il dépasse la longueur maximale.
    
    Args:
        text (str): Texte à tronquer
        max_length (int): Longueur maximale
        suffix (str): Suffixe à ajouter si tronqué
    
    Returns:
        str: Texte tronqué
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix