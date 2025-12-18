"""
Blueprint pour le module comptabilité
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import role_required, get_current_user, log_action
from utils.validators import validate_required, validate_montant
from utils.pdf_generator import generate_receipt
from datetime import datetime, timedelta
import os

comptabilite_bp = Blueprint('comptabilite', __name__)

@comptabilite_bp.route('/paiements', methods=['GET'])
@jwt_required()
@role_required('comptabilite', 'admin')
def list_paiements():
    """Liste tous les paiements"""
    statut = request.args.get('statut')
    etudiant_id = request.args.get('etudiant_id')
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    
    db = get_db()
    query = """
        SELECT p.*, e.numero_etudiant, u.nom as etudiant_nom, u.prenom as etudiant_prenom,
               tf.libelle as type_frais_libelle
        FROM paiements p
        JOIN etudiants e ON p.etudiant_id = e.id
        JOIN users u ON e.user_id = u.id
        JOIN types_frais tf ON p.type_frais_id = tf.id
        WHERE 1=1
    """
    params = []
    
    if statut:
        query += " AND p.statut = ?"
        params.append(statut)
    
    if etudiant_id:
        query += " AND p.etudiant_id = ?"
        params.append(etudiant_id)
    
    if date_debut:
        query += " AND p.date_paiement >= ?"
        params.append(date_debut)
    
    if date_fin:
        query += " AND p.date_paiement <= ?"
        params.append(date_fin)
    
    query += " ORDER BY p.date_paiement DESC"
    
    paiements = db.execute(query, params).fetchall()
    return jsonify([dict(p) for p in paiements]), 200

@comptabilite_bp.route('/paiements', methods=['POST'])
@jwt_required()
@role_required('comptabilite', 'admin')
def create_paiement():
    """Enregistre un nouveau paiement"""
    data = request.get_json()
    valid, error = validate_required(data, ['etudiant_id', 'type_frais_id', 'montant', 'mode_paiement'])
    if not valid:
        return jsonify({'error': error}), 400
    
    montant_valid, montant_error = validate_montant(data['montant'])
    if not montant_valid:
        return jsonify({'error': montant_error}), 400
    
    db = get_db()
    
    # Créer le paiement
    cursor = db.execute("""
        INSERT INTO paiements (etudiant_id, type_frais_id, montant, mode_paiement, 
                              reference_paiement, date_paiement, statut, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['etudiant_id'],
        data['type_frais_id'],
        data['montant'],
        data['mode_paiement'],
        data.get('reference_paiement'),
        data.get('date_paiement', datetime.now().date().isoformat()),
        'en_attente',
        data.get('notes')
    ))
    db.commit()
    
    paiement_id = cursor.lastrowid
    
    # Mettre à jour les tranches de paiement si applicable
    update_tranches(db, data['etudiant_id'], data['type_frais_id'], data['montant'])
    
    log_action(get_current_user()['id'], 'creation_paiement', 'paiements', paiement_id)
    
    return jsonify({'message': 'Paiement enregistré avec succès', 'paiement_id': paiement_id}), 201

@comptabilite_bp.route('/paiements/<int:paiement_id>/validate', methods=['POST'])
@jwt_required()
@role_required('comptabilite', 'admin')
def validate_paiement(paiement_id):
    """Valide un paiement"""
    data = request.get_json()
    db = get_db()
    
    paiement = db.execute("SELECT * FROM paiements WHERE id = ?", (paiement_id,)).fetchone()
    if not paiement:
        return jsonify({'error': 'Paiement non trouvé'}), 404
    
    if paiement['statut'] == 'valide':
        return jsonify({'error': 'Paiement déjà validé'}), 400
    
    # Valider le paiement
    db.execute("""
        UPDATE paiements 
        SET statut = ?, valide_par = ?, date_validation = ?
        WHERE id = ?
    """, (
        'valide',
        get_current_user()['id'],
        datetime.now(),
        paiement_id
    ))
    db.commit()
    
    # Mettre à jour les tranches
    update_tranches(db, paiement['etudiant_id'], paiement['type_frais_id'], paiement['montant'])
    
    log_action(get_current_user()['id'], 'validation_paiement', 'paiements', paiement_id)
    
    return jsonify({'message': 'Paiement validé avec succès'}), 200

@comptabilite_bp.route('/paiements/<int:paiement_id>/reject', methods=['POST'])
@jwt_required()
@role_required('comptabilite', 'admin')
def reject_paiement(paiement_id):
    """Rejette un paiement"""
    data = request.get_json()
    raison = data.get('raison', 'Paiement rejeté')
    
    db = get_db()
    db.execute("""
        UPDATE paiements 
        SET statut = ?, notes = ?
        WHERE id = ?
    """, ('rejete', raison, paiement_id))
    db.commit()
    
    log_action(get_current_user()['id'], 'rejet_paiement', 'paiements', paiement_id)
    
    return jsonify({'message': 'Paiement rejeté'}), 200

@comptabilite_bp.route('/paiements/<int:paiement_id>/receipt', methods=['GET'])
@jwt_required()
@role_required('comptabilite', 'admin', 'etudiant', 'parent')
def generate_payment_receipt(paiement_id):
    """Génère un reçu de paiement en PDF"""
    db = get_db()
    paiement = db.execute("""
        SELECT p.*, e.numero_etudiant, u.nom as etudiant_nom, u.prenom as etudiant_prenom,
               tf.libelle as type_frais
        FROM paiements p
        JOIN etudiants e ON p.etudiant_id = e.id
        JOIN users u ON e.user_id = u.id
        JOIN types_frais tf ON p.type_frais_id = tf.id
        WHERE p.id = ?
    """, (paiement_id,)).fetchone()
    
    if not paiement:
        return jsonify({'error': 'Paiement non trouvé'}), 404
    
    # Générer le PDF
    output_path = os.path.join(
        request.application.config['UPLOAD_FOLDER'],
        'pdf',
        f'receipt_{paiement_id}.pdf'
    )
    
    paiement_data = {
        'reference': paiement['reference_paiement'] or f"PAY{paiement_id:06d}",
        'date_paiement': paiement['date_paiement'],
        'etudiant_nom': paiement['etudiant_nom'],
        'etudiant_prenom': paiement['etudiant_prenom'],
        'type_frais': paiement['type_frais'],
        'montant': paiement['montant'],
        'mode_paiement': paiement['mode_paiement']
    }
    
    generate_receipt(paiement_data, output_path)
    
    return send_file(output_path, mimetype='application/pdf', as_attachment=True,
                    download_name=f'receipt_{paiement_id}.pdf')

@comptabilite_bp.route('/etudiants/<int:etudiant_id>/situation-financiere', methods=['GET'])
@jwt_required()
@role_required('comptabilite', 'admin', 'etudiant', 'parent')
def get_financial_situation(etudiant_id):
    """Obtient la situation financière d'un étudiant"""
    db = get_db()
    
    # Vérifier que l'utilisateur a le droit d'accéder à ces informations
    current_user = get_current_user()
    if current_user['role'] == 'etudiant':
        etudiant = db.execute("SELECT user_id FROM etudiants WHERE id = ?", (etudiant_id,)).fetchone()
        if not etudiant or etudiant['user_id'] != current_user['id']:
            return jsonify({'error': 'Accès refusé'}), 403
    
    # Obtenir tous les frais de la classe de l'étudiant
    etudiant_info = db.execute("""
        SELECT e.*, c.id as classe_id FROM etudiants e
        JOIN classes c ON e.classe_id = c.id
        WHERE e.id = ?
    """, (etudiant_id,)).fetchone()
    
    if not etudiant_info:
        return jsonify({'error': 'Étudiant non trouvé'}), 404
    
    # Frais dus
    frais_dus = db.execute("""
        SELECT fc.*, tf.libelle as type_frais_libelle, tf.code as type_frais_code
        FROM frais_classes fc
        JOIN types_frais tf ON fc.type_frais_id = tf.id
        WHERE fc.classe_id = ? AND fc.annee_academique_id = ?
    """, (etudiant_info['classe_id'], etudiant_info['annee_academique_id'])).fetchall()
    
    # Paiements effectués
    paiements = db.execute("""
        SELECT p.*, tf.libelle as type_frais_libelle
        FROM paiements p
        JOIN types_frais tf ON p.type_frais_id = tf.id
        WHERE p.etudiant_id = ? AND p.statut = 'valide'
    """, (etudiant_id,)).fetchall()
    
    # Calculer le solde
    total_due = sum(f['montant'] for f in frais_dus)
    total_paid = sum(p['montant'] for p in paiements)
    solde = total_due - total_paid
    
    # Vérifier les impayés
    has_unpaid = solde > 0
    
    return jsonify({
        'etudiant_id': etudiant_id,
        'total_due': total_due,
        'total_paid': total_paid,
        'solde': solde,
        'has_unpaid': has_unpaid,
        'frais_dus': [dict(f) for f in frais_dus],
        'paiements': [dict(p) for p in paiements]
    }), 200

@comptabilite_bp.route('/reports/financier', methods=['GET'])
@jwt_required()
@role_required('comptabilite', 'admin')
def get_financial_report():
    """Génère un rapport financier global"""
    date_debut = request.args.get('date_debut')
    date_fin = request.args.get('date_fin')
    
    db = get_db()
    
    query = """
        SELECT 
            SUM(montant) as total,
            COUNT(*) as nombre,
            mode_paiement
        FROM paiements
        WHERE statut = 'valide'
    """
    params = []
    
    if date_debut:
        query += " AND date_paiement >= ?"
        params.append(date_debut)
    
    if date_fin:
        query += " AND date_paiement <= ?"
        params.append(date_fin)
    
    query += " GROUP BY mode_paiement"
    
    stats = db.execute(query, params).fetchall()
    
    total_general = db.execute("""
        SELECT COALESCE(SUM(montant), 0) as total FROM paiements
        WHERE statut = 'valide'
    """, params[:len(params)//2] if date_debut and date_fin else []).fetchone()['total']
    
    return jsonify({
        'periode': {
            'debut': date_debut,
            'fin': date_fin
        },
        'total_general': total_general,
        'par_mode_paiement': [dict(s) for s in stats]
    }), 200

def update_tranches(db, etudiant_id, type_frais_id, montant):
    """Met à jour les tranches de paiement"""
    tranche = db.execute("""
        SELECT * FROM tranches_paiement
        WHERE etudiant_id = ? AND type_frais_id = ?
    """, (etudiant_id, type_frais_id)).fetchone()
    
    if tranche:
        nouveau_montant_paye = tranche['montant_paye'] + montant
        statut = 'paye' if nouveau_montant_paye >= tranche['montant_total'] else 'en_cours'
        
        db.execute("""
            UPDATE tranches_paiement
            SET montant_paye = ?, statut = ?
            WHERE id = ?
        """, (nouveau_montant_paye, statut, tranche['id']))
        db.commit()

