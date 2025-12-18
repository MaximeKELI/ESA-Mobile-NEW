"""
Blueprint pour les fonctionnalités communes à tous les utilisateurs
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import get_current_user
from datetime import datetime

commun_bp = Blueprint('commun', __name__)

@commun_bp.route('/annonces', methods=['GET'])
@jwt_required()
def list_annonces():
    """Liste les annonces"""
    type_annonce = request.args.get('type')
    is_urgent = request.args.get('urgent')
    db = get_db()
    current_user = get_current_user()
    
    query = """
        SELECT a.*, u.nom as auteur_nom, u.prenom as auteur_prenom
        FROM annonces a
        JOIN users u ON a.auteur_id = u.id
        WHERE a.is_active = 1
    """
    params = []
    
    if type_annonce:
        query += " AND a.type_annonce = ?"
        params.append(type_annonce)
    
    if is_urgent == 'true':
        query += " AND a.is_urgent = 1"
    
    # Filtrer par destinataires selon le rôle
    if current_user['role'] == 'etudiant':
        # Obtenir la classe de l'étudiant
        etudiant = db.execute("SELECT classe_id FROM etudiants WHERE user_id = ?", 
                             (current_user['id'],)).fetchone()
        if etudiant and etudiant['classe_id']:
            query += " AND (a.type_annonce = 'generale' OR a.type_annonce = 'classe')"
    
    query += " ORDER BY a.is_urgent DESC, a.date_publication DESC LIMIT 50"
    
    annonces = db.execute(query, params).fetchall()
    return jsonify([dict(annonce) for annonce in annonces]), 200

@commun_bp.route('/annonces/<int:annonce_id>', methods=['GET'])
@jwt_required()
def get_annonce(annonce_id):
    """Obtient une annonce spécifique"""
    db = get_db()
    annonce = db.execute("""
        SELECT a.*, u.nom as auteur_nom, u.prenom as auteur_prenom
        FROM annonces a
        JOIN users u ON a.auteur_id = u.id
        WHERE a.id = ?
    """, (annonce_id,)).fetchone()
    
    if not annonce:
        return jsonify({'error': 'Annonce non trouvée'}), 404
    
    return jsonify(dict(annonce)), 200

@commun_bp.route('/messages', methods=['GET'])
@jwt_required()
def list_messages():
    """Liste les messages de l'utilisateur"""
    type_message = request.args.get('type', 'recus')  # recus ou envoyes
    is_lu = request.args.get('is_lu')
    db = get_db()
    current_user = get_current_user()
    
    if type_message == 'recus':
        query = """
            SELECT m.*, u.nom as expediteur_nom, u.prenom as expediteur_prenom, u.role as expediteur_role
            FROM messages m
            JOIN users u ON m.expediteur_id = u.id
            WHERE m.destinataire_id = ?
        """
        params = [current_user['id']]
    else:
        query = """
            SELECT m.*, u.nom as destinataire_nom, u.prenom as destinataire_prenom, u.role as destinataire_role
            FROM messages m
            JOIN users u ON m.destinataire_id = u.id
            WHERE m.expediteur_id = ?
        """
        params = [current_user['id']]
    
    if is_lu is not None:
        query += " AND m.is_lu = ?"
        params.append(1 if is_lu == 'true' else 0)
    
    query += " ORDER BY m.created_at DESC LIMIT 50"
    
    messages = db.execute(query, params).fetchall()
    return jsonify([dict(message) for message in messages]), 200

@commun_bp.route('/messages', methods=['POST'])
@jwt_required()
def send_message():
    """Envoie un message"""
    data = request.get_json()
    current_user = get_current_user()
    db = get_db()
    
    if not data.get('destinataire_id') or not data.get('contenu'):
        return jsonify({'error': 'Destinataire et contenu requis'}), 400
    
    cursor = db.execute("""
        INSERT INTO messages (expediteur_id, destinataire_id, sujet, contenu)
        VALUES (?, ?, ?, ?)
    """, (
        current_user['id'],
        data['destinataire_id'],
        data.get('sujet'),
        data['contenu']
    ))
    db.commit()
    
    # Créer une notification pour le destinataire
    db.execute("""
        INSERT INTO notifications (user_id, type_notification, titre, message, lien)
        VALUES (?, 'message', ?, ?, ?)
    """, (
        data['destinataire_id'],
        'Nouveau message',
        f"Vous avez reçu un message de {current_user['nom']} {current_user['prenom']}",
        f"/messages/{cursor.lastrowid}"
    ))
    db.commit()
    
    return jsonify({'message': 'Message envoyé avec succès', 'message_id': cursor.lastrowid}), 201

@commun_bp.route('/messages/<int:message_id>/read', methods=['POST'])
@jwt_required()
def mark_message_read(message_id):
    """Marque un message comme lu"""
    current_user = get_current_user()
    db = get_db()
    
    db.execute("""
        UPDATE messages SET is_lu = 1, date_lecture = ?
        WHERE id = ? AND destinataire_id = ?
    """, (datetime.now(), message_id, current_user['id']))
    db.commit()
    
    return jsonify({'message': 'Message marqué comme lu'}), 200

@commun_bp.route('/users/search', methods=['GET'])
@jwt_required()
def search_users():
    """Recherche des utilisateurs (pour la messagerie)"""
    query_param = request.args.get('q', '')
    role = request.args.get('role')
    db = get_db()
    
    if not query_param or len(query_param) < 2:
        return jsonify([]), 200
    
    sql_query = """
        SELECT id, username, nom, prenom, email, role
        FROM users
        WHERE (nom LIKE ? OR prenom LIKE ? OR username LIKE ? OR email LIKE ?)
        AND is_active = 1
    """
    params = [f"%{query_param}%", f"%{query_param}%", f"%{query_param}%", f"%{query_param}%"]
    
    if role:
        sql_query += " AND role = ?"
        params.append(role)
    
    sql_query += " LIMIT 20"
    
    users = db.execute(sql_query, params).fetchall()
    return jsonify([dict(user) for user in users]), 200

@commun_bp.route('/parametres', methods=['GET'])
@jwt_required()
def get_parametres():
    """Obtient les paramètres globaux"""
    db = get_db()
    parametres = db.execute("SELECT * FROM parametres").fetchall()
    
    result = {}
    for param in parametres:
        valeur = param['valeur']
        if param['type_valeur'] == 'integer':
            valeur = int(valeur)
        elif param['type_valeur'] == 'float':
            valeur = float(valeur)
        elif param['type_valeur'] == 'boolean':
            valeur = valeur.lower() == 'true'
        
        result[param['cle']] = valeur
    
    return jsonify(result), 200

