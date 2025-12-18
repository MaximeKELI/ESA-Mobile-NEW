"""
Blueprint pour la gestion des bourses et aides financières
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import role_required, get_current_user, log_action
from utils.validators import validate_required, validate_montant
from datetime import datetime

bourses_bp = Blueprint('bourses', __name__)

@bourses_bp.route('/types', methods=['GET'])
@jwt_required()
def list_types_bourses():
    """Liste les types de bourses"""
    db = get_db()
    types = db.execute("SELECT * FROM types_bourses WHERE is_active = 1").fetchall()
    return jsonify([dict(t) for t in types]), 200

@bourses_bp.route('/types', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_type_bourse():
    """Crée un type de bourse"""
    data = request.get_json()
    valid, error = validate_required(data, ['code', 'libelle', 'montant'])
    if not valid:
        return jsonify({'error': error}), 400
    
    montant_valid, montant_error = validate_montant(data['montant'])
    if not montant_valid:
        return jsonify({'error': montant_error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO types_bourses (code, libelle, montant, duree_mois, criteres_eligibilite, nombre_places, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data['code'],
        data['libelle'],
        data['montant'],
        data.get('duree_mois', 12),
        data.get('criteres_eligibilite'),
        data.get('nombre_places'),
        data.get('is_active', True)
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_type_bourse', 'types_bourses', cursor.lastrowid)
    return jsonify({'message': 'Type de bourse créé avec succès'}), 201

@bourses_bp.route('/attributions', methods=['GET'])
@jwt_required()
@role_required('admin', 'comptabilite')
def list_bourses():
    """Liste les bourses attribuées"""
    etudiant_id = request.args.get('etudiant_id')
    statut = request.args.get('statut')
    db = get_db()
    
    query = """
        SELECT b.*, e.numero_etudiant, u.nom as etudiant_nom, u.prenom as etudiant_prenom,
               tb.libelle as type_bourse_libelle, tb.code as type_bourse_code,
               u2.nom as attribue_par_nom, u2.prenom as attribue_par_prenom
        FROM bourses b
        JOIN etudiants e ON b.etudiant_id = e.id
        JOIN users u ON e.user_id = u.id
        JOIN types_bourses tb ON b.type_bourse_id = tb.id
        JOIN users u2 ON b.attribue_par = u2.id
        WHERE 1=1
    """
    params = []
    
    if etudiant_id:
        query += " AND b.etudiant_id = ?"
        params.append(etudiant_id)
    
    if statut:
        query += " AND b.statut = ?"
        params.append(statut)
    
    query += " ORDER BY b.date_attribution DESC"
    
    bourses = db.execute(query, params).fetchall()
    return jsonify([dict(b) for b in bourses]), 200

@bourses_bp.route('/attributions', methods=['POST'])
@jwt_required()
@role_required('admin')
def attribuer_bourse():
    """Attribue une bourse à un étudiant"""
    data = request.get_json()
    valid, error = validate_required(data, ['etudiant_id', 'type_bourse_id', 'montant_total', 'date_debut'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    current_user = get_current_user()
    
    # Vérifier si l'étudiant a déjà une bourse active du même type
    existing = db.execute("""
        SELECT id FROM bourses
        WHERE etudiant_id = ? AND type_bourse_id = ? AND statut = 'active'
    """, (data['etudiant_id'], data['type_bourse_id'])).fetchone()
    
    if existing:
        return jsonify({'error': 'L\'étudiant a déjà une bourse active de ce type'}), 400
    
    # Calculer le montant mensuel si non fourni
    type_bourse = db.execute("SELECT duree_mois FROM types_bourses WHERE id = ?", 
                            (data['type_bourse_id'],)).fetchone()
    duree = type_bourse['duree_mois'] if type_bourse else 12
    montant_mensuel = data['montant_total'] / duree if duree > 0 else data['montant_total']
    
    cursor = db.execute("""
        INSERT INTO bourses (etudiant_id, type_bourse_id, montant_total, montant_mensuel,
                           date_debut, date_fin, statut, attribue_par, date_attribution, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['etudiant_id'],
        data['type_bourse_id'],
        data['montant_total'],
        montant_mensuel,
        data['date_debut'],
        data.get('date_fin'),
        'active',
        current_user['id'],
        datetime.now().date(),
        data.get('notes')
    ))
    db.commit()
    
    bourse_id = cursor.lastrowid
    
    log_action(current_user['id'], 'attribution_bourse', 'bourses', bourse_id)
    
    # Envoyer une notification
    from utils.notifications_service import send_notification
    etudiant = db.execute("SELECT user_id FROM etudiants WHERE id = ?", 
                         (data['etudiant_id'],)).fetchone()
    if etudiant:
        send_notification(
            etudiant['user_id'],
            'bourse_attribuee',
            'Bourse attribuée',
            f'Une bourse de {data["montant_total"]} FCFA vous a été attribuée.',
            f'/etudiant/bourses'
        )
    
    return jsonify({'message': 'Bourse attribuée avec succès', 'bourse_id': bourse_id}), 201

@bourses_bp.route('/attributions/<int:bourse_id>/paiements', methods=['GET'])
@jwt_required()
@role_required('admin', 'comptabilite')
def list_paiements_bourse(bourse_id):
    """Liste les paiements d'une bourse"""
    db = get_db()
    paiements = db.execute("""
        SELECT pb.*, u.nom as valide_par_nom, u.prenom as valide_par_prenom
        FROM paiements_bourses pb
        LEFT JOIN users u ON pb.valide_par = u.id
        WHERE pb.bourse_id = ?
        ORDER BY pb.date_paiement DESC
    """, (bourse_id,)).fetchall()
    
    return jsonify([dict(p) for p in paiements]), 200

@bourses_bp.route('/attributions/<int:bourse_id>/paiements', methods=['POST'])
@jwt_required()
@role_required('admin', 'comptabilite')
def enregistrer_paiement_bourse(bourse_id):
    """Enregistre un paiement de bourse"""
    data = request.get_json()
    valid, error = validate_required(data, ['montant', 'mois_paye'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    current_user = get_current_user()
    
    cursor = db.execute("""
        INSERT INTO paiements_bourses (bourse_id, montant, mois_paye, date_paiement,
                                      mode_paiement, reference_paiement, valide_par, date_validation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        bourse_id,
        data['montant'],
        data['mois_paye'],
        data.get('date_paiement', datetime.now().date()),
        data.get('mode_paiement'),
        data.get('reference_paiement'),
        current_user['id'],
        datetime.now()
    ))
    db.commit()
    
    log_action(current_user['id'], 'paiement_bourse', 'paiements_bourses', cursor.lastrowid)
    
    return jsonify({'message': 'Paiement enregistré avec succès'}), 201

@bourses_bp.route('/etudiants/<int:etudiant_id>/bourses', methods=['GET'])
@jwt_required()
def get_etudiant_bourses(etudiant_id):
    """Obtient les bourses d'un étudiant"""
    current_user = get_current_user()
    db = get_db()
    
    # Vérifier les droits d'accès
    if current_user['role'] == 'etudiant':
        etudiant = db.execute("SELECT user_id FROM etudiants WHERE id = ?", 
                             (etudiant_id,)).fetchone()
        if not etudiant or etudiant['user_id'] != current_user['id']:
            return jsonify({'error': 'Accès refusé'}), 403
    
    bourses = db.execute("""
        SELECT b.*, tb.libelle as type_bourse_libelle, tb.code as type_bourse_code
        FROM bourses b
        JOIN types_bourses tb ON b.type_bourse_id = tb.id
        WHERE b.etudiant_id = ?
        ORDER BY b.date_attribution DESC
    """, (etudiant_id,)).fetchall()
    
    return jsonify([dict(b) for b in bourses]), 200

