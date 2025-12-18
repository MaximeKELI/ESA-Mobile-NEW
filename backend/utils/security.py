"""
Module de sécurité avancé pour l'application ESA
"""
import re
import secrets
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from flask import jsonify, request, session, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from database.db import get_db
from utils.auth import log_action, log_connection

# Rate limiting storage (en production, utiliser Redis)
_rate_limit_storage = {}

def init_security(app):
    """Initialise les mesures de sécurité"""
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"  # En production, utiliser Redis
    )
    
    # Headers de sécurité
    @app.after_request
    def set_security_headers(response):
        """Ajoute les headers de sécurité HTTP"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
        return response
    
    return limiter

def generate_csrf_token():
    """Génère un token CSRF"""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']

def validate_csrf_token(token):
    """Valide un token CSRF"""
    if 'csrf_token' not in session:
        return False
    return secrets.compare_digest(token, session['csrf_token'])

def csrf_protect(f):
    """Décorateur pour protéger contre CSRF"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            token = request.headers.get('X-CSRF-Token') or request.json.get('csrf_token') if request.is_json else None
            if not token or not validate_csrf_token(token):
                return jsonify({'error': 'Token CSRF invalide ou manquant'}), 403
        return f(*args, **kwargs)
    return decorated_function

def sanitize_input(input_string):
    """Nettoie une chaîne d'entrée pour prévenir les injections SQL et XSS"""
    if not isinstance(input_string, str):
        return input_string
    
    # Caractères dangereux pour SQL
    dangerous_sql = ["'", '"', ';', '--', '/*', '*/', 'xp_', 'sp_', 'exec', 'execute', 'union', 'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter']
    
    # Caractères dangereux pour XSS
    dangerous_xss = ['<script', '</script>', '<iframe', 'javascript:', 'onerror=', 'onclick=', 'onload=']
    
    cleaned = input_string
    for char in dangerous_sql:
        cleaned = cleaned.replace(char, '')
    
    for char in dangerous_xss:
        cleaned = cleaned.replace(char, '', flags=re.IGNORECASE)
    
    return cleaned.strip()

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
    
    # Vérifier les mots de passe communs
    common_passwords = ['password', '12345678', 'qwerty', 'admin', 'password123']
    if password.lower() in common_passwords:
        errors.append("Ce mot de passe est trop commun")
    
    return len(errors) == 0, errors

def detect_suspicious_activity(user_id, action, ip_address):
    """Détecte une activité suspecte"""
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
    
    # Vérifier les actions suspectes
    suspicious_actions = ['suppression', 'modification_massive', 'export_donnees']
    if action in suspicious_actions:
        count = db.execute("""
            SELECT COUNT(*) as count FROM logs_actions
            WHERE user_id = ? AND action = ?
            AND created_at > datetime('now', '-1 hour')
        """, (user_id, action)).fetchone()
        
        if count['count'] > 10:
            return True, "Trop d'actions suspectes détectées"
    
    return False, None

def log_security_event(event_type, user_id, details, severity='info', ip_address=None):
    """Enregistre un événement de sécurité"""
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
        ip_address or request.remote_addr
    ))
    db.commit()

def check_rate_limit(identifier, limit=5, window=60):
    """Vérifie le rate limiting manuel"""
    key = f"rate_limit_{identifier}"
    now = datetime.now()
    
    if key not in _rate_limit_storage:
        _rate_limit_storage[key] = []
    
    # Nettoyer les anciennes entrées
    _rate_limit_storage[key] = [
        timestamp for timestamp in _rate_limit_storage[key]
        if (now - timestamp).total_seconds() < window
    ]
    
    if len(_rate_limit_storage[key]) >= limit:
        return False
    
    _rate_limit_storage[key].append(now)
    return True

def encrypt_sensitive_data(data):
    """Chiffre des données sensibles (basique, utiliser cryptography en production)"""
    import os
    from cryptography.fernet import Fernet
    
    key = os.getenv('ENCRYPTION_KEY', '').encode()
    if not key:
        # Générer une clé si elle n'existe pas (à stocker de manière sécurisée en production)
        key = Fernet.generate_key()
        os.environ['ENCRYPTION_KEY'] = key.decode()
    
    try:
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        return encrypted.decode()
    except Exception:
        # Fallback si le chiffrement échoue
        return data

def decrypt_sensitive_data(encrypted_data):
    """Déchiffre des données sensibles"""
    import os
    from cryptography.fernet import Fernet
    
    key = os.getenv('ENCRYPTION_KEY', '').encode()
    if not key:
        return encrypted_data
    
    try:
        f = Fernet(key)
        decrypted = f.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except Exception:
        return encrypted_data

def validate_session(user_id, session_token):
    """Valide une session utilisateur"""
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

def ip_whitelist_check(ip_address):
    """Vérifie si une IP est dans la whitelist (optionnel)"""
    whitelist = []  # À configurer selon les besoins
    if whitelist:
        return ip_address in whitelist
    return True

def validate_file_upload(file, allowed_extensions=None, max_size=5*1024*1024):
    """Valide un fichier uploadé"""
    if allowed_extensions is None:
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
    
    if not file:
        return False, "Aucun fichier fourni"
    
    # Vérifier l'extension
    filename = file.filename
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        return False, f"Extension non autorisée. Autorisées: {', '.join(allowed_extensions)}"
    
    # Vérifier la taille
    file.seek(0, 2)  # Aller à la fin
    size = file.tell()
    file.seek(0)  # Retourner au début
    
    if size > max_size:
        return False, f"Fichier trop volumineux. Maximum: {max_size / 1024 / 1024}MB"
    
    # Vérifier le type MIME (basique)
    # En production, utiliser python-magic pour une vérification plus stricte
    
    return True, None

def sql_injection_check(query_params):
    """Détecte les tentatives d'injection SQL"""
    sql_keywords = ['union', 'select', 'insert', 'update', 'delete', 'drop', 'create', 'alter', 'exec', 'execute']
    
    for param in query_params.values():
        if isinstance(param, str):
            param_lower = param.lower()
            for keyword in sql_keywords:
                if keyword in param_lower:
                    return True, f"Tentative d'injection SQL détectée: {keyword}"
    
    return False, None

def xss_check(input_string):
    """Détecte les tentatives de XSS"""
    if not isinstance(input_string, str):
        return False, None
    
    xss_patterns = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>',
        r'<object[^>]*>',
        r'<embed[^>]*>',
    ]
    
    for pattern in xss_patterns:
        if re.search(pattern, input_string, re.IGNORECASE):
            return True, f"Tentative de XSS détectée"
    
    return False, None

def secure_headers_middleware():
    """Middleware pour les headers de sécurité"""
    pass  # Déjà géré dans init_security

