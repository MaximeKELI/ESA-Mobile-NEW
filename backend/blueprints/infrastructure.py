"""
Blueprint pour la gestion de l'infrastructure (salles, équipements)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import role_required, get_current_user, log_action
from utils.validators import validate_required, validate_date
from datetime import datetime, date, time

infrastructure_bp = Blueprint('infrastructure', __name__)

@infrastructure_bp.route('/salles', methods=['GET'])
@jwt_required()
def list_salles():
    """Liste les salles"""
    type_salle = request.args.get('type_salle')
    is_disponible = request.args.get('disponible')
    date_recherche = request.args.get('date')
    heure_debut = request.args.get('heure_debut')
    heure_fin = request.args.get('heure_fin')
    
    db = get_db()
    
    query = "SELECT * FROM salles WHERE is_active = 1"
    params = []
    
    if type_salle:
        query += " AND type_salle = ?"
        params.append(type_salle)
    
    query += " ORDER BY code"
    
    salles = db.execute(query, params).fetchall()
    salles_list = []
    
    for salle in salles:
        salle_dict = dict(salle)
        
        # Vérifier la disponibilité si demandé
        if is_disponible == 'true' and date_recherche and heure_debut and heure_fin:
            reservations = db.execute("""
                SELECT id FROM reservations_salles
                WHERE salle_id = ? AND date_reservation = ? 
                AND statut = 'confirmee'
                AND (
                    (heure_debut <= ? AND heure_fin > ?) OR
                    (heure_debut < ? AND heure_fin >= ?) OR
                    (heure_debut >= ? AND heure_fin <= ?)
                )
            """, (
                salle['id'], date_recherche,
                heure_debut, heure_debut,
                heure_fin, heure_fin,
                heure_debut, heure_fin
            )).fetchone()
            
            salle_dict['disponible'] = reservations is None
        else:
            salle_dict['disponible'] = True
        
        salles_list.append(salle_dict)
    
    return jsonify(salles_list), 200

@infrastructure_bp.route('/salles', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_salle():
    """Crée une nouvelle salle"""
    data = request.get_json()
    valid, error = validate_required(data, ['code', 'libelle', 'type_salle'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO salles (code, libelle, type_salle, capacite, equipements, batiment,
                          etage, is_active, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['code'],
        data['libelle'],
        data['type_salle'],
        data.get('capacite'),
        data.get('equipements'),
        data.get('batiment'),
        data.get('etage'),
        data.get('is_active', True),
        data.get('notes')
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_salle', 'salles', cursor.lastrowid)
    return jsonify({'message': 'Salle créée avec succès', 'salle_id': cursor.lastrowid}), 201

@infrastructure_bp.route('/reservations', methods=['GET'])
@jwt_required()
def list_reservations():
    """Liste les réservations de salles"""
    salle_id = request.args.get('salle_id')
    date_recherche = request.args.get('date')
    db = get_db()
    current_user = get_current_user()
    
    query = """
        SELECT r.*, s.libelle as salle_libelle, s.code as salle_code,
               u.nom as reserve_par_nom, u.prenom as reserve_par_prenom
        FROM reservations_salles r
        JOIN salles s ON r.salle_id = s.id
        JOIN users u ON r.reserve_par = u.id
        WHERE 1=1
    """
    params = []
    
    if salle_id:
        query += " AND r.salle_id = ?"
        params.append(salle_id)
    
    if date_recherche:
        query += " AND r.date_reservation = ?"
        params.append(date_recherche)
    
    if current_user['role'] == 'etudiant':
        query += " AND r.reserve_par = ?"
        params.append(current_user['id'])
    
    query += " ORDER BY r.date_reservation, r.heure_debut"
    
    reservations = db.execute(query, params).fetchall()
    return jsonify([dict(r) for r in reservations]), 200

@infrastructure_bp.route('/reservations', methods=['POST'])
@jwt_required()
def create_reservation():
    """Crée une réservation de salle"""
    data = request.get_json()
    valid, error = validate_required(data, ['salle_id', 'date_reservation', 'heure_debut', 'heure_fin'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    current_user = get_current_user()
    
    # Vérifier la disponibilité
    conflit = db.execute("""
        SELECT id FROM reservations_salles
        WHERE salle_id = ? AND date_reservation = ? AND statut = 'confirmee'
        AND (
            (heure_debut <= ? AND heure_fin > ?) OR
            (heure_debut < ? AND heure_fin >= ?) OR
            (heure_debut >= ? AND heure_fin <= ?)
        )
    """, (
        data['salle_id'],
        data['date_reservation'],
        data['heure_debut'], data['heure_debut'],
        data['heure_fin'], data['heure_fin'],
        data['heure_debut'], data['heure_fin']
    )).fetchone()
    
    if conflit:
        return jsonify({'error': 'La salle n\'est pas disponible à cette heure'}), 400
    
    cursor = db.execute("""
        INSERT INTO reservations_salles (salle_id, reserve_par, date_reservation, heure_debut,
                                       heure_fin, motif, type_reservation, statut)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['salle_id'],
        current_user['id'],
        data['date_reservation'],
        data['heure_debut'],
        data['heure_fin'],
        data.get('motif'),
        data.get('type_reservation', 'autre'),
        'confirmee'
    ))
    db.commit()
    
    log_action(current_user['id'], 'creation_reservation', 'reservations_salles', cursor.lastrowid)
    return jsonify({'message': 'Réservation créée avec succès', 'reservation_id': cursor.lastrowid}), 201

@infrastructure_bp.route('/equipements', methods=['GET'])
@jwt_required()
def list_equipements():
    """Liste les équipements"""
    salle_id = request.args.get('salle_id')
    etat = request.args.get('etat')
    db = get_db()
    
    query = """
        SELECT e.*, s.libelle as salle_libelle, s.code as salle_code
        FROM equipements e
        LEFT JOIN salles s ON e.salle_id = s.id
        WHERE 1=1
    """
    params = []
    
    if salle_id:
        query += " AND e.salle_id = ?"
        params.append(salle_id)
    
    if etat:
        query += " AND e.etat = ?"
        params.append(etat)
    
    query += " ORDER BY e.code"
    
    equipements = db.execute(query, params).fetchall()
    return jsonify([dict(e) for e in equipements]), 200

@infrastructure_bp.route('/equipements', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_equipement():
    """Ajoute un nouvel équipement"""
    data = request.get_json()
    valid, error = validate_required(data, ['code', 'libelle'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO equipements (code, libelle, type_equipement, marque, modele, numero_serie,
                               date_acquisition, valeur_acquisition, etat, salle_id, fournisseur,
                               garantie_jusqu_a, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['code'],
        data['libelle'],
        data.get('type_equipement'),
        data.get('marque'),
        data.get('modele'),
        data.get('numero_serie'),
        data.get('date_acquisition'),
        data.get('valeur_acquisition'),
        data.get('etat', 'neuf'),
        data.get('salle_id'),
        data.get('fournisseur'),
        data.get('garantie_jusqu_a'),
        data.get('notes')
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_equipement', 'equipements', cursor.lastrowid)
    return jsonify({'message': 'Équipement ajouté avec succès', 'equipement_id': cursor.lastrowid}), 201

@infrastructure_bp.route('/maintenances', methods=['GET'])
@jwt_required()
def list_maintenances():
    """Liste les maintenances"""
    equipement_id = request.args.get('equipement_id')
    statut = request.args.get('statut')
    db = get_db()
    
    query = "SELECT * FROM maintenances WHERE 1=1"
    params = []
    
    if equipement_id:
        query += " AND equipement_id = ?"
        params.append(equipement_id)
    
    if statut:
        query += " AND statut = ?"
        params.append(statut)
    
    query += " ORDER BY date_intervention DESC"
    
    maintenances = db.execute(query, params).fetchall()
    return jsonify([dict(m) for m in maintenances]), 200

@infrastructure_bp.route('/maintenances', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_maintenance():
    """Crée une demande de maintenance"""
    data = request.get_json()
    valid, error = validate_required(data, ['description', 'date_intervention'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO maintenances (equipement_id, salle_id, type_maintenance, description,
                                date_intervention, technicien, cout, statut)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('equipement_id'),
        data.get('salle_id'),
        data.get('type_maintenance', 'corrective'),
        data['description'],
        data['date_intervention'],
        data.get('technicien'),
        data.get('cout'),
        data.get('statut', 'planifiee')
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_maintenance', 'maintenances', cursor.lastrowid)
    return jsonify({'message': 'Maintenance créée avec succès', 'maintenance_id': cursor.lastrowid}), 201


