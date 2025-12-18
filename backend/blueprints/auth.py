"""
Blueprint d'authentification
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from database.db import get_db
from utils.auth import hash_password, verify_password, log_connection, generate_reset_token
from utils.validators import validate_email_format, validate_required
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
    
    username = data.get('username')
    password = data.get('password')
    
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ? OR email = ?",
        (username, username)
    ).fetchone()
    
    # Log de la tentative de connexion
    ip_address = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    
    if not user or not verify_password(password, user['password_hash']):
        log_connection(None, username, ip_address, user_agent, 'echec', 'Identifiants invalides')
        return jsonify({'error': 'Identifiants invalides'}), 401
    
    if not user['is_active']:
        log_connection(user['id'], username, ip_address, user_agent, 'echec', 'Compte désactivé')
        return jsonify({'error': 'Compte désactivé'}), 403
    
    # Mettre à jour la dernière connexion
    db.execute(
        "UPDATE users SET last_login = ? WHERE id = ?",
        (datetime.now(), user['id'])
    )
    db.commit()
    
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
    
    if len(new_password) < 6:
        return jsonify({'error': 'Le mot de passe doit contenir au moins 6 caractères'}), 400
    
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

