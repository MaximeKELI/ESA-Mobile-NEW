"""
Blueprint d'authentification
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.db import get_db
from utils.auth import hash_password, verify_password, log_connection, generate_reset_token
from utils.validators import validate_email_format, validate_required
from utils.security import (
    check_rate_limit, detect_suspicious_activity, log_security_event,
    validate_password_strength, sanitize_input, sql_injection_check
)
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authentification d'un utilisateur"""
    data = request.get_json()
    
    # Validation
    valid, error = validate_required(data, ['username', 'password'])
    if not valid:
        return jsonify({'error': error}), 400
    
    # Sanitization des entrées
    username = sanitize_input(data.get('username'))
    password = data.get('password')
    
    # Vérification d'injection SQL
    sql_check, sql_error = sql_injection_check({'username': username})
    if sql_check:
        log_security_event('sql_injection_attempt', None, {'username': username}, 'high')
        return jsonify({'error': 'Requête invalide'}), 400
    
    # Rate limiting manuel supplémentaire
    ip_address = request.remote_addr
    if not check_rate_limit(f"login_{ip_address}", limit=5, window=60):
        log_security_event('rate_limit_exceeded', None, {'ip': ip_address}, 'warning')
        return jsonify({'error': 'Trop de tentatives. Veuillez réessayer plus tard.'}), 429
    
    try:
        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? OR email = ?",
            (username, username)
        ).fetchone()
    except Exception as e:
        # Erreur de base de données - retourner erreur générique
        import logging
        logging.error(f"Erreur DB lors de la connexion: {e}")
        return jsonify({'error': 'Erreur serveur. Veuillez réessayer.'}), 500
    
    # Log de la tentative de connexion
    user_agent = request.headers.get('User-Agent', '')
    
    if not user or not verify_password(password, user['password_hash']):
        log_connection(None, username, ip_address, user_agent, 'echec', 'Identifiants invalides')
        log_security_event('failed_login', None, {'username': username, 'ip': ip_address}, 'warning')
        return jsonify({'error': 'Identifiants invalides'}), 401
    
    if not user['is_active']:
        log_connection(user['id'], username, ip_address, user_agent, 'echec', 'Compte désactivé')
        log_security_event('disabled_account_login', user['id'], {'username': username}, 'warning')
        return jsonify({'error': 'Compte désactivé'}), 403
    
    # Détection d'activité suspecte
    try:
        is_suspicious, suspicion_reason = detect_suspicious_activity(user['id'], 'login', ip_address)
        if is_suspicious:
            log_security_event('suspicious_activity', user['id'], {'reason': suspicion_reason}, 'high')
            # Ne pas bloquer, mais logger
    except Exception:
        # Ne pas bloquer si la détection échoue
        pass
    
    # Mettre à jour la dernière connexion
    try:
        db.execute(
            "UPDATE users SET last_login = ? WHERE id = ?",
            (datetime.now(), user['id'])
        )
        db.commit()
    except Exception as e:
        # Ne pas bloquer si la mise à jour échoue
        import logging
        logging.warning(f"Erreur lors de la mise à jour last_login: {e}")
        try:
            db.rollback()
        except:
            pass
    
    # Log de connexion réussie
    log_connection(user['id'], username, ip_address, user_agent, 'succes', None)
    
    # Créer les tokens JWT
    access_token = create_access_token(identity=user['id'])
    refresh_token = create_refresh_token(identity=user['id'])
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'nom': user['nom'],
            'prenom': user['prenom']
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """Inscription d'un nouvel utilisateur"""
    data = request.get_json()
    
    # Validation
    valid, error = validate_required(data, ['username', 'email', 'password', 'nom', 'prenom', 'role'])
    if not valid:
        return jsonify({'error': error}), 400
    
    # Validation de l'email
    email_valid, email_error = validate_email_format(data['email'])
    if not email_valid:
        return jsonify({'error': 'Format d\'email invalide', 'details': email_error}), 400
    
    # Validation de la force du mot de passe
    is_strong, errors = validate_password_strength(data['password'])
    if not is_strong:
        return jsonify({'error': 'Mot de passe faible', 'details': errors}), 400
    
    # Sanitization
    username = sanitize_input(data['username'])
    email = sanitize_input(data['email'])
    
    # Vérification d'injection SQL
    sql_check, sql_error = sql_injection_check({'username': username, 'email': email})
    if sql_check:
        return jsonify({'error': 'Requête invalide'}), 400
    
    db = get_db()
    
    # Vérifier si l'utilisateur existe déjà
    existing_user = db.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (username, email)
    ).fetchone()
    
    if existing_user:
        return jsonify({'error': 'Nom d\'utilisateur ou email déjà utilisé'}), 400
    
    # Hashage du mot de passe
    password_hash = hash_password(data['password'])
    
    # Créer l'utilisateur
    cursor = db.execute("""
        INSERT INTO users (username, email, password_hash, role, nom, prenom, 
                         telephone, adresse, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        username,
        email,
        password_hash,
        data['role'],
        data['nom'],
        data['prenom'],
        data.get('telephone'),
        data.get('adresse'),
        data.get('is_active', True) if data['role'] != 'etudiant' else False  # Étudiants doivent être activés par admin
    ))
    db.commit()
    user_id = cursor.lastrowid
    
    # Créer le profil spécifique selon le rôle
    if data['role'] == 'etudiant':
        # L'étudiant sera créé lors de l'inscription académique
        pass
    elif data['role'] == 'enseignant':
        db.execute("""
            INSERT INTO enseignants (user_id, matricule, date_embauche, is_active)
            VALUES (?, ?, ?, ?)
        """, (user_id, f"ENS{user_id:04d}", datetime.now().date(), True))
        db.commit()
    elif data['role'] == 'parent':
        db.execute("""
            INSERT INTO parents (user_id, lien_parente)
            VALUES (?, ?)
        """, (user_id, data.get('lien_parente', 'tuteur')))
        db.commit()
    
    # Récupérer l'utilisateur créé
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    
    from utils.auth import log_action
    log_action(user_id, 'inscription', 'users', user_id)
    
    return jsonify({
        'message': 'Inscription réussie',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'role': user['role'],
            'nom': user['nom'],
            'prenom': user['prenom']
        }
    }), 201

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Rafraîchit le token d'accès"""
    current_user_id = get_jwt_identity()
    new_token = create_access_token(identity=current_user_id)
    return jsonify({'access_token': new_token}), 200

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Déconnexion (côté client, supprimer le token)"""
    return jsonify({'message': 'Déconnexion réussie'}), 200

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Changement de mot de passe"""
    data = request.get_json()
    current_user_id = get_jwt_identity()
    
    valid, error = validate_required(data, ['old_password', 'new_password'])
    if not valid:
        return jsonify({'error': error}), 400
    
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    # Validation de la force du mot de passe
    is_strong, errors = validate_password_strength(new_password)
    if not is_strong:
        return jsonify({'error': 'Mot de passe faible', 'details': errors}), 400
    
    # Vérifier que le nouveau mot de passe est différent de l'ancien
    if old_password == new_password:
        return jsonify({'error': 'Le nouveau mot de passe doit être différent de l\'ancien'}), 400
    
    db = get_db()
    user = db.execute("SELECT password_hash FROM users WHERE id = ?", (current_user_id,)).fetchone()
    
    if not user or not verify_password(old_password, user['password_hash']):
        return jsonify({'error': 'Ancien mot de passe incorrect'}), 400
    
    # Mettre à jour le mot de passe
    new_password_hash = hash_password(new_password)
    db.execute(
        "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
        (new_password_hash, datetime.now(), current_user_id)
    )
    db.commit()
    
    from utils.auth import log_action
    log_action(current_user_id, 'changement_mot_de_passe', 'users', current_user_id)
    
    return jsonify({'message': 'Mot de passe modifié avec succès'}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Demande de réinitialisation de mot de passe"""
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email requis'}), 400
    
    db = get_db()
    user = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    
    if user:
        # Générer un token de réinitialisation
        reset_token = generate_reset_token()
        expires = datetime.now() + timedelta(hours=24)
        
        db.execute(
            "UPDATE users SET reset_token = ?, reset_token_expires = ? WHERE id = ?",
            (reset_token, expires, user['id'])
        )
        db.commit()
        
        # En production, envoyer un email avec le token
        # Pour l'instant, on retourne le token (à ne pas faire en production)
        return jsonify({
            'message': 'Un email de réinitialisation a été envoyé',
            'reset_token': reset_token  # À retirer en production
        }), 200
    
    # Ne pas révéler si l'email existe ou non
    return jsonify({'message': 'Si cet email existe, un lien de réinitialisation a été envoyé'}), 200

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Réinitialisation du mot de passe avec token"""
    data = request.get_json()
    
    valid, error = validate_required(data, ['token', 'new_password'])
    if not valid:
        return jsonify({'error': error}), 400
    
    token = data.get('token')
    new_password = data.get('new_password')
    
    if len(new_password) < 6:
        return jsonify({'error': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
    
    db = get_db()
    user = db.execute(
        "SELECT id FROM users WHERE reset_token = ? AND reset_token_expires > ?",
        (token, datetime.now())
    ).fetchone()
    
    if not user:
        return jsonify({'error': 'Token invalide ou expiré'}), 400
    
    # Mettre à jour le mot de passe
    new_password_hash = hash_password(new_password)
    db.execute(
        "UPDATE users SET password_hash = ?, reset_token = NULL, reset_token_expires = NULL, updated_at = ? WHERE id = ?",
        (new_password_hash, datetime.now(), user['id'])
    )
    db.commit()
    
    return jsonify({'message': 'Mot de passe réinitialisé avec succès'}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtient les informations de l'utilisateur connecté"""
    current_user_id = get_jwt_identity()
    db = get_db()
    
    user = db.execute("SELECT id, username, email, role, nom, prenom, telephone, adresse, photo_path FROM users WHERE id = ?", 
                     (current_user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    return jsonify(dict(user)), 200

