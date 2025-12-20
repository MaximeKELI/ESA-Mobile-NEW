"""
Améliorations de sécurité pour l'application ESA
"""
from flask import request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import hashlib
import secrets
from datetime import datetime, timedelta

# Rate Limiter
def init_rate_limiter(app):
    """Initialise le rate limiter"""
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"  # En production, utiliser Redis
    )
    return limiter

# Protection CSRF
def generate_csrf_token():
    """Génère un token CSRF"""
    return secrets.token_urlsafe(32)

def validate_csrf_token(token, session_token):
    """Valide un token CSRF"""
    return secrets.compare_digest(token, session_token)

# Validation d'email améliorée
def is_valid_email(email):
    """Valide un email avec vérifications supplémentaires"""
    from email_validator import validate_email, EmailNotValidError
    
    try:
        # Vérifier le format
        validation = validate_email(email, check_deliverability=False)
        email = validation.email
        
        # Vérifications supplémentaires
        if email.count('@') != 1:
            return False
        
        local, domain = email.split('@')
        
        # Longueur minimale
        if len(local) < 1 or len(domain) < 4:
            return False
        
        # Pas de caractères interdits
        forbidden_chars = ['<', '>', '"', "'", ';', ':', '\\', '/']
        if any(char in email for char in forbidden_chars):
            return False
        
        return True
    except EmailNotValidError:
        return False

# Protection contre les injections SQL
def sanitize_input(input_string):
    """Nettoie une chaîne d'entrée pour prévenir les injections"""
    if not isinstance(input_string, str):
        return input_string
    
    # Caractères dangereux
    dangerous_chars = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_']
    
    for char in dangerous_chars:
        input_string = input_string.replace(char, '')
    
    return input_string.strip()

# Validation de mot de passe fort
def validate_password_strength(password):
    """Valide la force d'un mot de passe"""
    errors = []
    
    if len(password) < 8:
        errors.append("Le mot de passe doit contenir au moins 8 caractères")
    
    if not any(c.isupper() for c in password):
        errors.append("Le mot de passe doit contenir au moins une majuscule")
    
    if not any(c.islower() for c in password):
        errors.append("Le mot de passe doit contenir au moins une minuscule")
    
    if not any(c.isdigit() for c in password):
        errors.append("Le mot de passe doit contenir au moins un chiffre")
    
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Le mot de passe doit contenir au moins un caractère spécial")
    
    return len(errors) == 0, errors

# Détection d'activité suspecte
def detect_suspicious_activity(user_id, action, ip_address):
    """Détecte une activité suspecte"""
    from database.db import get_db
    
    db = get_db()
    
    # Vérifier les tentatives de connexion échouées récentes
    recent_failures = db.execute("""
        SELECT COUNT(*) as count FROM logs_connexion
        WHERE user_id = ? AND statut = 'echec'
        AND created_at > datetime('now', '-15 minutes')
    """, (user_id,)).fetchone()
    
    if recent_failures['count'] > 5:
        return True, "Trop de tentatives de connexion échouées"
    
    # Vérifier les changements d'IP fréquents
    recent_ips = db.execute("""
        SELECT DISTINCT ip_address FROM logs_connexion
        WHERE user_id = ? AND statut = 'succes'
        AND created_at > datetime('now', '-1 hour')
    """, (user_id,)).fetchall()
    
    if len(recent_ips) > 3:
        return True, "Changements d'adresse IP suspects"
    
    return False, None

# Logging sécurisé
def log_security_event(event_type, user_id, details, severity='info'):
    """Enregistre un événement de sécurité"""
    from database.db import get_db
    
    db = get_db()
    
    db.execute("""
        INSERT INTO logs_actions (user_id, action, table_affectee, 
                                 nouvelles_valeurs, ip_address)
        VALUES (?, ?, ?, ?, ?)
    """, (
        user_id,
        f"security_{event_type}",
        'security',
        str(details),
        request.remote_addr
    ))
    db.commit()

# Décorateur pour vérifier les permissions granulaires
def permission_required(resource, action):
    """Décorateur pour vérifier les permissions granulaires"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from utils.auth import get_current_user
            from database.db import get_db
            
            user = get_current_user()
            if not user:
                return jsonify({'error': 'Non authentifié'}), 401
            
            db = get_db()
            
            # Vérifier la permission
            permission = db.execute("""
                SELECT allowed FROM permissions
                WHERE role = ? AND resource = ? AND action = ?
            """, (user['role'], resource, action)).fetchone()
            
            if not permission or not permission['allowed']:
                log_security_event('permission_denied', user['id'], {
                    'resource': resource,
                    'action': action
                }, 'warning')
                return jsonify({'error': 'Permission refusée'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Chiffrement de données sensibles
def encrypt_sensitive_data(data):
    """Chiffre des données sensibles"""
    from cryptography.fernet import Fernet
    import os
    
    key = os.getenv('ENCRYPTION_KEY', '').encode()
    if not key:
        # En production, générer une clé et la stocker de manière sécurisée
        key = Fernet.generate_key()
    
    f = Fernet(key)
    encrypted = f.encrypt(data.encode())
    return encrypted.decode()

def decrypt_sensitive_data(encrypted_data):
    """Déchiffre des données sensibles"""
    from cryptography.fernet import Fernet
    import os
    
    key = os.getenv('ENCRYPTION_KEY', '').encode()
    f = Fernet(key)
    decrypted = f.decrypt(encrypted_data.encode())
    return decrypted.decode()

# Validation de session
def validate_session(user_id, session_token):
    """Valide une session utilisateur"""
    from database.db import get_db
    
    db = get_db()
    
    session = db.execute("""
        SELECT * FROM user_sessions
        WHERE user_id = ? AND token = ? AND expires_at > datetime('now')
    """, (user_id, session_token)).fetchone()
    
    if not session:
        return False
    
    # Mettre à jour la dernière activité
    db.execute("""
        UPDATE user_sessions SET last_activity = datetime('now')
        WHERE id = ?
    """, (session['id'],))
    db.commit()
    
    return True


