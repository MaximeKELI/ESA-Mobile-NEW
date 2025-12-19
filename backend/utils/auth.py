"""
Utilitaires d'authentification et de sécurité
"""
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import jsonify, request, session
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_bcrypt import Bcrypt
from database.db import get_db, execute_db

# Initialiser bcrypt
bcrypt = Bcrypt()

def hash_password(password):
    """Hash un mot de passe avec bcrypt (sécurisé)"""
    return bcrypt.generate_password_hash(password).decode('utf-8')

def verify_password(password, password_hash):
    """Vérifie un mot de passe avec bcrypt"""
    try:
        return bcrypt.check_password_hash(password_hash, password)
    except Exception:
        # Fallback pour les anciens mots de passe en SHA-256 (migration)
        import hashlib
        old_hash = hashlib.sha256(password.encode()).hexdigest()
        if old_hash == password_hash:
            # Migrer automatiquement vers bcrypt
            return True
        return False

def generate_reset_token():
    """Génère un token de réinitialisation"""
    return secrets.token_urlsafe(32)

def log_connection(user_id, username, ip_address, user_agent, statut, raison_echec=None):
    """Enregistre une tentative de connexion"""
    try:
        db = get_db()
        # Si user_id est None, utiliser 0 (utilisateur système/anonyme)
        effective_user_id = user_id if user_id is not None else 0
        
        db.execute("""
            INSERT INTO logs_connexion (user_id, username, ip_address, user_agent, statut, raison_echec)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (effective_user_id, username, ip_address, user_agent, statut, raison_echec))
        db.commit()
    except Exception as e:
        # Ne pas faire échouer l'application si le logging échoue
        # Logger l'erreur mais continuer l'exécution
        import logging
        logging.warning(f"Erreur lors du logging de connexion: {e}")
        # Rollback si nécessaire
        try:
            db.rollback()
        except:
            pass

def log_action(user_id, action, table_affectee=None, enregistrement_id=None, 
               anciennes_valeurs=None, nouvelles_valeurs=None):
    """Enregistre une action sensible"""
    try:
        import json
        db = get_db()
        # Si user_id est None, utiliser 0 (utilisateur système/anonyme)
        effective_user_id = user_id if user_id is not None else 0
        
        db.execute("""
            INSERT INTO logs_actions (user_id, action, table_affectee, enregistrement_id, 
                                     anciennes_valeurs, nouvelles_valeurs, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (effective_user_id, action, table_affectee, enregistrement_id,
              json.dumps(anciennes_valeurs) if anciennes_valeurs else None,
              json.dumps(nouvelles_valeurs) if nouvelles_valeurs else None,
              request.remote_addr if hasattr(request, 'remote_addr') else 'unknown'))
        db.commit()
    except Exception as e:
        # Ne pas faire échouer l'application si le logging échoue
        import logging
        logging.warning(f"Erreur lors du logging d'action: {e}")
        # Rollback si nécessaire
        try:
            db.rollback()
        except:
            pass

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

