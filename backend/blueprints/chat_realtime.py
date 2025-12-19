"""
Blueprint pour le chat en temps réel
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import get_current_user
from utils.validators import validate_required
from datetime import datetime
import json

chat_realtime_bp = Blueprint('chat_realtime', __name__)

@chat_realtime_bp.route('/conversations', methods=['GET'])
@jwt_required()
def list_conversations():
    """Liste les conversations de l'utilisateur"""
    current_user = get_current_user()
    db = get_db()
    
    conversations = db.execute("""
        SELECT c.*, 
               (SELECT COUNT(*) FROM messages_chat m 
                WHERE m.conversation_id = c.id AND m.created_at > 
                (SELECT date_derniere_lecture FROM participants_conversations 
                 WHERE conversation_id = c.id AND user_id = ?)) as messages_non_lus
        FROM conversations c
        JOIN participants_conversations p ON c.id = p.conversation_id
        WHERE p.user_id = ? AND c.is_active = 1
        ORDER BY c.created_at DESC
    """, (current_user['id'], current_user['id'])).fetchall()
    
    return jsonify([dict(c) for c in conversations]), 200

@chat_realtime_bp.route('/conversations', methods=['POST'])
@jwt_required()
def create_conversation():
    """Crée une nouvelle conversation"""
    data = request.get_json()
    valid, error = validate_required(data, ['type_conversation', 'participants'])
    if not valid:
        return jsonify({'error': error}), 400
    
    current_user = get_current_user()
    db = get_db()
    
    # Créer la conversation
    cursor = db.execute("""
        INSERT INTO conversations (type_conversation, titre, createur_id, is_active)
        VALUES (?, ?, ?, ?)
    """, (
        data['type_conversation'],
        data.get('titre'),
        current_user['id'],
        True
    ))
    db.commit()
    conversation_id = cursor.lastrowid
    
    # Ajouter les participants
    participants = data['participants']
    if current_user['id'] not in participants:
        participants.append(current_user['id'])
    
    for user_id in participants:
        db.execute("""
            INSERT INTO participants_conversations (conversation_id, user_id, role)
            VALUES (?, ?, ?)
        """, (conversation_id, user_id, 'admin' if user_id == current_user['id'] else 'membre'))
    
    db.commit()
    
    return jsonify({'message': 'Conversation créée', 'conversation_id': conversation_id}), 201

@chat_realtime_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conversation_id):
    """Obtient les messages d'une conversation"""
    limit = request.args.get('limit', 50, type=int)
    before_id = request.args.get('before_id', type=int)
    current_user = get_current_user()
    db = get_db()
    
    # Vérifier que l'utilisateur participe à la conversation
    participant = db.execute("""
        SELECT id FROM participants_conversations
        WHERE conversation_id = ? AND user_id = ?
    """, (conversation_id, current_user['id'])).fetchone()
    
    if not participant:
        return jsonify({'error': 'Accès refusé'}), 403
    
    query = """
        SELECT m.*, u.nom as expediteur_nom, u.prenom as expediteur_prenom, u.role as expediteur_role
        FROM messages_chat m
        JOIN users u ON m.expediteur_id = u.id
        WHERE m.conversation_id = ? AND m.is_supprime = 0
    """
    params = [conversation_id]
    
    if before_id:
        query += " AND m.id < ?"
        params.append(before_id)
    
    query += " ORDER BY m.created_at DESC LIMIT ?"
    params.append(limit)
    
    messages = db.execute(query, params).fetchall()
    
    # Mettre à jour la date de dernière lecture
    db.execute("""
        UPDATE participants_conversations
        SET date_derniere_lecture = ?
        WHERE conversation_id = ? AND user_id = ?
    """, (datetime.now(), conversation_id, current_user['id']))
    db.commit()
    
    return jsonify([dict(m) for m in reversed(messages)]), 200

@chat_realtime_bp.route('/conversations/<int:conversation_id>/messages', methods=['POST'])
@jwt_required()
def send_message(conversation_id):
    """Envoie un message dans une conversation"""
    data = request.get_json()
    valid, error = validate_required(data, ['contenu'])
    if not valid:
        return jsonify({'error': error}), 400
    
    current_user = get_current_user()
    db = get_db()
    
    # Vérifier que l'utilisateur participe à la conversation
    participant = db.execute("""
        SELECT id FROM participants_conversations
        WHERE conversation_id = ? AND user_id = ?
    """, (conversation_id, current_user['id'])).fetchone()
    
    if not participant:
        return jsonify({'error': 'Accès refusé'}), 403
    
    # Créer le message
    cursor = db.execute("""
        INSERT INTO messages_chat (conversation_id, expediteur_id, contenu, type_message,
                                  fichier_path, reponse_a)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        conversation_id,
        current_user['id'],
        data['contenu'],
        data.get('type_message', 'texte'),
        data.get('fichier_path'),
        data.get('reponse_a')
    ))
    db.commit()
    
    message_id = cursor.lastrowid
    
    # Mettre à jour la présence
    db.execute("""
        INSERT OR REPLACE INTO presence_users (user_id, is_online, derniere_activite)
        VALUES (?, 1, ?)
    """, (current_user['id'], datetime.now()))
    db.commit()
    
    # En production, envoyer via WebSocket aux autres participants
    # notify_participants_via_websocket(conversation_id, message_id)
    
    return jsonify({'message': 'Message envoyé', 'message_id': message_id}), 201

@chat_realtime_bp.route('/presence', methods=['GET'])
@jwt_required()
def get_presence():
    """Obtient le statut de présence des utilisateurs"""
    user_ids = request.args.getlist('user_ids')
    if not user_ids:
        return jsonify({'error': 'user_ids requis'}), 400
    
    db = get_db()
    
    placeholders = ','.join(['?'] * len(user_ids))
    presence = db.execute(f"""
        SELECT user_id, is_online, derniere_activite
        FROM presence_users
        WHERE user_id IN ({placeholders})
    """, user_ids).fetchall()
    
    return jsonify([dict(p) for p in presence]), 200

@chat_realtime_bp.route('/presence', methods=['POST'])
@jwt_required()
def update_presence():
    """Met à jour le statut de présence"""
    data = request.get_json()
    current_user = get_current_user()
    db = get_db()
    
    is_online = data.get('is_online', True)
    
    db.execute("""
        INSERT OR REPLACE INTO presence_users (user_id, is_online, derniere_activite, device_info)
        VALUES (?, ?, ?, ?)
    """, (current_user['id'], is_online, datetime.now(), json.dumps(data.get('device_info', {}))))
    db.commit()
    
    return jsonify({'message': 'Présence mise à jour'}), 200

