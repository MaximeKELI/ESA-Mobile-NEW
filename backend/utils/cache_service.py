"""
Service de cache pour améliorer les performances
"""
from flask_caching import Cache
import json
from functools import wraps

cache = Cache()

def init_cache(app):
    """Initialise le système de cache"""
    cache.init_app(app, config={
        'CACHE_TYPE': 'redis',  # En production
        'CACHE_REDIS_URL': 'redis://localhost:6379/0',
        'CACHE_DEFAULT_TIMEOUT': 300  # 5 minutes par défaut
    })
    return cache

# Cache en mémoire pour développement (si Redis non disponible)
cache_memory = {}

def cached(timeout=300, key_prefix='view'):
    """Décorateur pour mettre en cache une fonction"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Générer une clé de cache unique
            cache_key = f"{key_prefix}:{f.__name__}:{str(args)}:{str(kwargs)}"
            
            # Vérifier le cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Exécuter la fonction
            result = f(*args, **kwargs)
            
            # Mettre en cache
            cache.set(cache_key, result, timeout=timeout)
            
            return result
        return decorated_function
    return decorator

def invalidate_cache(pattern):
    """Invalide le cache selon un pattern"""
    try:
        # Si Redis est utilisé
        cache.cache.delete_many(pattern)
    except:
        # Fallback en mémoire
        keys_to_delete = [k for k in cache_memory.keys() if pattern in k]
        for key in keys_to_delete:
            del cache_memory[key]

def cache_user_data(user_id, data, timeout=600):
    """Cache les données d'un utilisateur"""
    cache_key = f"user:{user_id}:data"
    cache.set(cache_key, data, timeout=timeout)

def get_cached_user_data(user_id):
    """Récupère les données cachées d'un utilisateur"""
    cache_key = f"user:{user_id}:data"
    return cache.get(cache_key)

def clear_user_cache(user_id):
    """Efface le cache d'un utilisateur"""
    cache.delete(f"user:{user_id}:data")
    cache.delete(f"user:{user_id}:permissions")
    cache.delete(f"user:{user_id}:notifications")


