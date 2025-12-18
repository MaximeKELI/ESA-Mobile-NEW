"""
Blueprint pour l'intégration Mobile Money complète
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import role_required, get_current_user, log_action
from utils.validators import validate_required, validate_montant
from datetime import datetime
import hashlib
import hmac
import json

mobile_money_bp = Blueprint('mobile_money', __name__)

@mobile_money_bp.route('/config', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_config():
    """Obtient la configuration Mobile Money"""
    db = get_db()
    configs = db.execute("SELECT * FROM config_mobile_money WHERE is_actif = 1").fetchall()
    
    # Masquer les secrets
    result = []
    for config in configs:
        config_dict = dict(config)
        config_dict['api_secret'] = '***' if config_dict['api_secret'] else None
        result.append(config_dict)
    
    return jsonify(result), 200

@mobile_money_bp.route('/config', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_config():
    """Configure un opérateur Mobile Money"""
    data = request.get_json()
    valid, error = validate_required(data, ['operateur', 'api_url', 'api_key', 'api_secret'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    
    # Vérifier si la config existe déjà
    existing = db.execute("SELECT id FROM config_mobile_money WHERE operateur = ?", 
                         (data['operateur'],)).fetchone()
    
    if existing:
        # Mettre à jour
        db.execute("""
            UPDATE config_mobile_money
            SET api_url = ?, api_key = ?, api_secret = ?, merchant_id = ?,
                webhook_url = ?, is_actif = ?
            WHERE operateur = ?
        """, (
            data['api_url'],
            data['api_key'],
            data['api_secret'],
            data.get('merchant_id'),
            data.get('webhook_url'),
            data.get('is_actif', True),
            data['operateur']
        ))
        db.commit()
        return jsonify({'message': 'Configuration mise à jour'}), 200
    else:
        # Créer
        cursor = db.execute("""
            INSERT INTO config_mobile_money (operateur, api_url, api_key, api_secret,
                                           merchant_id, webhook_url, is_actif)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['operateur'],
            data['api_url'],
            data['api_key'],
            data['api_secret'],
            data.get('merchant_id'),
            data.get('webhook_url'),
            data.get('is_actif', True)
        ))
        db.commit()
        return jsonify({'message': 'Configuration créée', 'config_id': cursor.lastrowid}), 201

@mobile_money_bp.route('/initier-paiement', methods=['POST'])
@jwt_required()
def initier_paiement():
    """Initie un paiement Mobile Money"""
    data = request.get_json()
    valid, error = validate_required(data, ['etudiant_id', 'type_frais_id', 'montant', 'operateur', 'numero_telephone'])
    if not valid:
        return jsonify({'error': error}), 400
    
    montant_valid, montant_error = validate_montant(data['montant'])
    if not montant_valid:
        return jsonify({'error': montant_error}), 400
    
    db = get_db()
    current_user = get_current_user()
    
    # Vérifier les droits
    if current_user['role'] == 'etudiant':
        etudiant = db.execute("SELECT user_id FROM etudiants WHERE id = ?", 
                             (data['etudiant_id'],)).fetchone()
        if not etudiant or etudiant['user_id'] != current_user['id']:
            return jsonify({'error': 'Accès refusé'}), 403
    
    # Récupérer la configuration
    config = db.execute("SELECT * FROM config_mobile_money WHERE operateur = ? AND is_actif = 1", 
                       (data['operateur'],)).fetchone()
    
    if not config:
        return jsonify({'error': f'Opérateur {data["operateur"]} non configuré'}), 400
    
    # Générer une référence unique
    reference = f"MM{datetime.now().strftime('%Y%m%d%H%M%S')}{data['etudiant_id']}"
    
    # Créer la transaction
    cursor = db.execute("""
        INSERT INTO transactions_mobile_money (etudiant_id, type_frais_id, montant, operateur,
                                              numero_telephone, reference_transaction, statut)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data['etudiant_id'],
        data['type_frais_id'],
        data['montant'],
        data['operateur'],
        data['numero_telephone'],
        reference,
        'en_attente'
    ))
    db.commit()
    transaction_id = cursor.lastrowid
    
    # Appeler l'API Mobile Money (simulation)
    # En production, faire l'appel réel à l'API
    payment_result = appeler_api_mobile_money(
        config,
        data['numero_telephone'],
        data['montant'],
        reference
    )
    
    if payment_result['success']:
        # Mettre à jour la transaction
        db.execute("""
            UPDATE transactions_mobile_money
            SET statut = 'validee', date_validation = ?, callback_data = ?
            WHERE id = ?
        """, (datetime.now(), json.dumps(payment_result), transaction_id))
        db.commit()
        
        # Créer le paiement associé
        db.execute("""
            INSERT INTO paiements (etudiant_id, type_frais_id, montant, mode_paiement,
                                 reference_paiement, date_paiement, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data['etudiant_id'],
            data['type_frais_id'],
            data['montant'],
            'mobile_money',
            reference,
            datetime.now().date(),
            'valide'
        ))
        db.commit()
        
        log_action(current_user['id'], 'paiement_mobile_money', 'transactions_mobile_money', transaction_id)
        
        return jsonify({
            'message': 'Paiement initié avec succès',
            'transaction_id': transaction_id,
            'reference': reference,
            'statut': 'validee'
        }), 200
    else:
        return jsonify({
            'error': 'Échec du paiement',
            'details': payment_result.get('message')
        }), 400

@mobile_money_bp.route('/webhook', methods=['POST'])
def webhook_mobile_money():
    """Webhook pour recevoir les confirmations de paiement"""
    data = request.get_json()
    reference = data.get('reference') or data.get('transaction_id')
    
    if not reference:
        return jsonify({'error': 'Reference manquante'}), 400
    
    db = get_db()
    
    # Trouver la transaction
    transaction = db.execute("""
        SELECT * FROM transactions_mobile_money
        WHERE reference_transaction = ?
    """, (reference,)).fetchone()
    
    if not transaction:
        return jsonify({'error': 'Transaction non trouvée'}), 404
    
    # Vérifier la signature (sécurité)
    # En production, vérifier la signature HMAC
    
    # Mettre à jour la transaction
    statut = 'validee' if data.get('status') == 'success' else 'echec'
    
    db.execute("""
        UPDATE transactions_mobile_money
        SET statut = ?, webhook_received = 1, date_webhook = ?, callback_data = ?
        WHERE id = ?
    """, (statut, datetime.now(), json.dumps(data), transaction['id']))
    db.commit()
    
    # Si validé, créer le paiement
    if statut == 'validee' and transaction['statut'] != 'validee':
        db.execute("""
            INSERT INTO paiements (etudiant_id, type_frais_id, montant, mode_paiement,
                                 reference_paiement, date_paiement, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction['etudiant_id'],
            transaction['type_frais_id'],
            transaction['montant'],
            'mobile_money',
            reference,
            datetime.now().date(),
            'valide'
        ))
        db.commit()
    
    return jsonify({'message': 'Webhook traité avec succès'}), 200

@mobile_money_bp.route('/transactions', methods=['GET'])
@jwt_required()
def list_transactions():
    """Liste les transactions Mobile Money"""
    etudiant_id = request.args.get('etudiant_id')
    statut = request.args.get('statut')
    db = get_db()
    current_user = get_current_user()
    
    query = """
        SELECT t.*, e.numero_etudiant, u.nom as etudiant_nom, u.prenom as etudiant_prenom,
               tf.libelle as type_frais_libelle
        FROM transactions_mobile_money t
        JOIN etudiants e ON t.etudiant_id = e.id
        JOIN users u ON e.user_id = u.id
        JOIN types_frais tf ON t.type_frais_id = tf.id
        WHERE 1=1
    """
    params = []
    
    if current_user['role'] == 'etudiant':
        etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                             (current_user['id'],)).fetchone()
        if etudiant:
            query += " AND t.etudiant_id = ?"
            params.append(etudiant['id'])
    
    if etudiant_id and current_user['role'] in ['admin', 'comptabilite']:
        query += " AND t.etudiant_id = ?"
        params.append(etudiant_id)
    
    if statut:
        query += " AND t.statut = ?"
        params.append(statut)
    
    query += " ORDER BY t.date_transaction DESC"
    
    transactions = db.execute(query, params).fetchall()
    return jsonify([dict(t) for t in transactions]), 200

def appeler_api_mobile_money(config, numero, montant, reference):
    """Appelle l'API Mobile Money (simulation)"""
    # En production, implémenter l'appel réel selon l'opérateur
    # Moov Money API ou Togocel Flooz API
    
    # Simulation pour le développement
    return {
        'success': True,
        'message': 'Paiement simulé avec succès',
        'transaction_id': reference,
        'status': 'success'
    }

