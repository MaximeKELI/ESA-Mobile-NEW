"""
Utilitaires d'authentification et de sécurité
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from database.db import get_db, execute_db

def hash_password(password):
    """Hash un mot de passe (en production, utiliser bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Vérifie un mot de passe"""
    return hash_password(password) == password_hash

def generate_reset_token():
    """Génère un token de réinitialisation"""
    return secrets.token_urlsafe(32)

def log_connection(user_id, username, ip_address, user_agent, statut, raison_echec=None):
    """Enregistre une tentative de connexion"""
    db = get_db()
    db.execute("""
        INSERT INTO logs_connexion (user_id, username, ip_address, user_agent, statut, raison_echec)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, username, ip_address, user_agent, statut, raison_echec))
    db.commit()

def log_action(user_id, action, table_affectee=None, enregistrement_id=None, 
               anciennes_valeurs=None, nouvelles_valeurs=None):
    """Enregistre une action sensible"""
    import json
    db = get_db()
    db.execute("""
        INSERT INTO logs_actions (user_id, action, table_affectee, enregistrement_id, 
                                 anciennes_valeurs, nouvelles_valeurs, ip_address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, action, table_affectee, enregistrement_id,
          json.dumps(anciennes_valeurs) if anciennes_valeurs else None,
          json.dumps(nouvelles_valeurs) if nouvelles_valeurs else None,
          request.remote_addr))
    db.commit()

def role_required(*roles):
    """Décorateur pour vérifier le rôle de l'utilisateur"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            db = get_db()
            user = db.execute(
                "SELECT role FROM users WHERE id = ? AND is_active = 1",
                (user_id,)
            ).fetchone()
            
            if not user or user['role'] not in roles:
                return jsonify({'error': 'Accès refusé'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Obtient l'utilisateur actuellement connecté"""
    verify_jwt_in_request()
    user_id = get_jwt_identity()
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    return dict(user) if user else None

