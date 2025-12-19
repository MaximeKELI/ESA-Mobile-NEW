"""
Blueprint pour le Chatbot Intelligent
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import get_current_user, role_required
from datetime import datetime
import json
import re

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/conversation', methods=['POST'])
@jwt_required()
def chat():
    """Interagit avec le chatbot"""
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'Message requis'}), 400
    
    current_user = get_current_user()
    db = get_db()
    
    # Obtenir ou créer une session de conversation
    session_id = data.get('session_id')
    if not session_id:
        import secrets
        session_id = secrets.token_urlsafe(16)
        
        db.execute("""
            INSERT INTO conversations_chatbot (user_id, session_id, contexte, is_active)
            VALUES (?, ?, ?, ?)
        """, (current_user['id'], session_id, json.dumps({}), True))
        db.commit()
    
    # Analyser l'intention (simplifié, en production utiliser NLP/ML)
    intention, confiance = analyser_intention(message)
    
    # Générer la réponse
    reponse = generer_reponse(message, intention, current_user, db)
    
    # Enregistrer le message et la réponse
    conversation = db.execute("""
        SELECT id FROM conversations_chatbot WHERE session_id = ?
    """, (session_id,)).fetchone()
    
    if conversation:
        db.execute("""
            INSERT INTO messages_chatbot (conversation_id, message_utilisateur, reponse_bot,
                                        intention, confiance)
            VALUES (?, ?, ?, ?, ?)
        """, (conversation['id'], message, reponse, intention, confiance))
        
        db.execute("""
            UPDATE conversations_chatbot
            SET derniere_interaction = ?
            WHERE id = ?
        """, (datetime.now(), conversation['id']))
        db.commit()
    
    return jsonify({
        'reponse': reponse,
        'intention': intention,
        'confiance': confiance,
        'session_id': session_id
    }), 200

@chatbot_bp.route('/base-connaissances', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_base_connaissances():
    """Liste la base de connaissances"""
    categorie = request.args.get('categorie')
    recherche = request.args.get('q')
    db = get_db()
    
    query = "SELECT * FROM base_connaissances WHERE is_active = 1"
    params = []
    
    if categorie:
        query += " AND categorie = ?"
        params.append(categorie)
    
    if recherche:
        query += " AND (question LIKE ? OR reponse LIKE ?)"
        search_term = f"%{recherche}%"
        params.extend([search_term, search_term])
    
    query += " ORDER BY nombre_utilisations DESC"
    
    connaissances = db.execute(query, params).fetchall()
    return jsonify([dict(k) for k in connaissances]), 200

@chatbot_bp.route('/base-connaissances', methods=['POST'])
@jwt_required()
@role_required('admin')
def ajouter_connaissance():
    """Ajoute une entrée à la base de connaissances"""
    data = request.get_json()
    
    if not data.get('question') or not data.get('reponse'):
        return jsonify({'error': 'Question et réponse requises'}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO base_connaissances (question, reponse, categorie, tags)
        VALUES (?, ?, ?, ?)
    """, (
        data['question'],
        data['reponse'],
        data.get('categorie'),
        json.dumps(data.get('tags', []))
    ))
    db.commit()
    
    return jsonify({'message': 'Connaissance ajoutée', 'id': cursor.lastrowid}), 201

def analyser_intention(message):
    """Analyse l'intention du message (simplifié)"""
    message_lower = message.lower()
    
    # Patterns d'intention
    intentions = {
        'notes': ['note', 'moyenne', 'bulletin', 'resultat'],
        'paiement': ['paiement', 'payer', 'frais', 'solde', 'impaye'],
        'emploi_temps': ['emploi', 'horaire', 'cours', 'classe'],
        'absence': ['absence', 'present', 'retard'],
        'contact': ['contact', 'telephone', 'email', 'adresse'],
        'aide': ['aide', 'help', 'comment', 'comment faire'],
        'salutation': ['bonjour', 'salut', 'bonsoir', 'hello']
    }
    
    for intention, keywords in intentions.items():
        for keyword in keywords:
            if keyword in message_lower:
                return intention, 0.8
    
    return 'general', 0.5

def generer_reponse(message, intention, user, db):
    """Génère une réponse selon l'intention"""
    
    # Chercher dans la base de connaissances
    connaissances = db.execute("""
        SELECT * FROM base_connaissances
        WHERE is_active = 1
        AND (question LIKE ? OR reponse LIKE ?)
        ORDER BY score_utilite DESC, nombre_utilisations DESC
        LIMIT 1
    """, (f"%{message}%", f"%{message}%")).fetchone()
    
    if connaissances:
        # Mettre à jour le nombre d'utilisations
        db.execute("""
            UPDATE base_connaissances
            SET nombre_utilisations = nombre_utilisations + 1
            WHERE id = ?
        """, (connaissances['id'],))
        db.commit()
        return connaissances['reponse']
    
    # Réponses par intention
    reponses = {
        'notes': "Pour consulter vos notes, allez dans la section 'Notes' de l'application. Vous pouvez également télécharger votre bulletin.",
        'paiement': "Pour consulter votre situation financière, allez dans 'Finances'. Vous pouvez payer via Mobile Money directement depuis l'application.",
        'emploi_temps': "Votre emploi du temps est disponible dans la section 'Emploi du temps'. Vous pouvez le consulter à tout moment.",
        'absence': "Vos absences sont enregistrées dans la section 'Absences'. Contactez l'administration pour justifier une absence.",
        'contact': f"Vous pouvez contacter l'école par email à contact@esa.tg ou par téléphone. Votre email: {user.get('email', 'N/A')}",
        'aide': "Je peux vous aider avec vos notes, paiements, emploi du temps, absences et bien plus. Posez-moi une question !",
        'salutation': f"Bonjour {user.get('prenom', '')} ! Comment puis-je vous aider aujourd'hui ?"
    }
    
    return reponses.get(intention, "Je comprends votre demande. Pouvez-vous être plus précis ? Je peux vous aider avec vos notes, paiements, emploi du temps et bien plus.")

