"""
Blueprint pour la gestion des stages et alternances
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import role_required, get_current_user, log_action
from utils.validators import validate_required, validate_date
from datetime import datetime

stages_bp = Blueprint('stages', __name__)

@stages_bp.route('/entreprises', methods=['GET'])
@jwt_required()
def list_entreprises():
    """Liste les entreprises partenaires"""
    db = get_db()
    entreprises = db.execute("""
        SELECT * FROM entreprises WHERE is_active = 1 ORDER BY raison_sociale
    """).fetchall()
    return jsonify([dict(e) for e in entreprises]), 200

@stages_bp.route('/entreprises', methods=['POST'])
@jwt_required()
@role_required('admin', 'enseignant')
def create_entreprise():
    """Ajoute une nouvelle entreprise"""
    data = request.get_json()
    valid, error = validate_required(data, ['raison_sociale'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO entreprises (raison_sociale, secteur_activite, adresse, telephone, email,
                               site_web, contact_nom, contact_prenom, contact_poste,
                               contact_telephone, contact_email, type_partenaire, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['raison_sociale'],
        data.get('secteur_activite'),
        data.get('adresse'),
        data.get('telephone'),
        data.get('email'),
        data.get('site_web'),
        data.get('contact_nom'),
        data.get('contact_prenom'),
        data.get('contact_poste'),
        data.get('contact_telephone'),
        data.get('contact_email'),
        data.get('type_partenaire', 'stage'),
        data.get('is_active', True)
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_entreprise', 'entreprises', cursor.lastrowid)
    return jsonify({'message': 'Entreprise ajoutée avec succès', 'entreprise_id': cursor.lastrowid}), 201

@stages_bp.route('/offres', methods=['GET'])
@jwt_required()
def list_offres_stage():
    """Liste les offres de stage"""
    filiere_id = request.args.get('filiere_id')
    statut = request.args.get('statut', 'ouverte')
    db = get_db()
    
    query = """
        SELECT o.*, e.raison_sociale as entreprise_nom, f.libelle as filiere_libelle
        FROM offres_stage o
        JOIN entreprises e ON o.entreprise_id = e.id
        LEFT JOIN filieres f ON o.filiere_id = f.id
        WHERE o.statut = ?
    """
    params = [statut]
    
    if filiere_id:
        query += " AND o.filiere_id = ?"
        params.append(filiere_id)
    
    query += " ORDER BY o.date_publication DESC"
    
    offres = db.execute(query, params).fetchall()
    return jsonify([dict(o) for o in offres]), 200

@stages_bp.route('/offres', methods=['POST'])
@jwt_required()
@role_required('admin', 'enseignant')
def create_offre_stage():
    """Crée une nouvelle offre de stage"""
    data = request.get_json()
    valid, error = validate_required(data, ['entreprise_id', 'titre', 'description'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO offres_stage (entreprise_id, titre, description, duree_mois, date_debut,
                                 date_fin, remuneration, filiere_id, niveau_requis,
                                 nombre_places, competences_requises, statut, date_publication)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['entreprise_id'],
        data['titre'],
        data['description'],
        data.get('duree_mois'),
        data.get('date_debut'),
        data.get('date_fin'),
        data.get('remuneration'),
        data.get('filiere_id'),
        data.get('niveau_requis'),
        data.get('nombre_places', 1),
        data.get('competences_requises'),
        'ouverte',
        datetime.now().date()
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_offre_stage', 'offres_stage', cursor.lastrowid)
    return jsonify({'message': 'Offre de stage créée avec succès', 'offre_id': cursor.lastrowid}), 201

@stages_bp.route('/conventions', methods=['GET'])
@jwt_required()
def list_conventions():
    """Liste les conventions de stage"""
    etudiant_id = request.args.get('etudiant_id')
    statut = request.args.get('statut')
    db = get_db()
    current_user = get_current_user()
    
    query = """
        SELECT c.*, e.numero_etudiant, u.nom as etudiant_nom, u.prenom as etudiant_prenom,
               ent.raison_sociale as entreprise_nom, off.titre as offre_titre
        FROM conventions_stage c
        JOIN etudiants e ON c.etudiant_id = e.id
        JOIN users u ON e.user_id = u.id
        JOIN entreprises ent ON c.entreprise_id = ent.id
        JOIN offres_stage off ON c.offre_stage_id = off.id
        WHERE 1=1
    """
    params = []
    
    if current_user['role'] == 'etudiant':
        etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                             (current_user['id'],)).fetchone()
        if etudiant:
            query += " AND c.etudiant_id = ?"
            params.append(etudiant['id'])
    
    if etudiant_id and current_user['role'] in ['admin', 'enseignant']:
        query += " AND c.etudiant_id = ?"
        params.append(etudiant_id)
    
    if statut:
        query += " AND c.statut = ?"
        params.append(statut)
    
    query += " ORDER BY c.date_debut DESC"
    
    conventions = db.execute(query, params).fetchall()
    return jsonify([dict(c) for c in conventions]), 200

@stages_bp.route('/conventions', methods=['POST'])
@jwt_required()
@role_required('admin', 'enseignant')
def create_convention():
    """Crée une convention de stage"""
    data = request.get_json()
    valid, error = validate_required(data, ['etudiant_id', 'offre_stage_id', 'entreprise_id', 'date_debut', 'date_fin'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO conventions_stage (etudiant_id, offre_stage_id, entreprise_id, tuteur_entreprise,
                                      tuteur_ecole_id, date_debut, date_fin, objectifs, taches,
                                      remuneration, statut)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['etudiant_id'],
        data['offre_stage_id'],
        data['entreprise_id'],
        data.get('tuteur_entreprise'),
        data.get('tuteur_ecole_id'),
        data['date_debut'],
        data['date_fin'],
        data.get('objectifs'),
        data.get('taches'),
        data.get('remuneration'),
        'en_attente'
    ))
    db.commit()
    
    convention_id = cursor.lastrowid
    
    log_action(get_current_user()['id'], 'creation_convention', 'conventions_stage', convention_id)
    
    # Notifier l'étudiant
    from utils.notifications_service import send_notification
    etudiant = db.execute("SELECT user_id FROM etudiants WHERE id = ?", 
                         (data['etudiant_id'],)).fetchone()
    if etudiant:
        send_notification(
            etudiant['user_id'],
            'convention_stage',
            'Nouvelle convention de stage',
            'Une convention de stage vous a été proposée. Veuillez la consulter et la signer.',
            f'/etudiant/stages/conventions/{convention_id}'
        )
    
    return jsonify({'message': 'Convention créée avec succès', 'convention_id': convention_id}), 201

@stages_bp.route('/conventions/<int:convention_id>/signer', methods=['POST'])
@jwt_required()
def signer_convention(convention_id):
    """Signe une convention de stage"""
    data = request.get_json()
    signataire = data.get('signataire')  # 'etudiant', 'entreprise', 'ecole'
    
    if signataire not in ['etudiant', 'entreprise', 'ecole']:
        return jsonify({'error': 'Signataire invalide'}), 400
    
    db = get_db()
    convention = db.execute("SELECT * FROM conventions_stage WHERE id = ?", 
                           (convention_id,)).fetchone()
    
    if not convention:
        return jsonify({'error': 'Convention non trouvée'}), 404
    
    current_user = get_current_user()
    
    # Vérifier les droits
    if signataire == 'etudiant':
        etudiant = db.execute("SELECT user_id FROM etudiants WHERE id = ?", 
                             (convention['etudiant_id'],)).fetchone()
        if not etudiant or etudiant['user_id'] != current_user['id']:
            return jsonify({'error': 'Accès refusé'}), 403
        db.execute("UPDATE conventions_stage SET date_signature_etudiant = ? WHERE id = ?",
                  (datetime.now().date(), convention_id))
    
    elif signataire == 'ecole':
        if current_user['role'] not in ['admin', 'enseignant']:
            return jsonify({'error': 'Accès refusé'}), 403
        db.execute("UPDATE conventions_stage SET date_signature_ecole = ? WHERE id = ?",
                  (datetime.now().date(), convention_id))
    
    # Vérifier si toutes les signatures sont faites
    convention_updated = db.execute("SELECT * FROM conventions_stage WHERE id = ?", 
                                   (convention_id,)).fetchone()
    
    if convention_updated['date_signature_etudiant'] and convention_updated['date_signature_ecole']:
        db.execute("UPDATE conventions_stage SET statut = 'validee' WHERE id = ?", (convention_id,))
    
    db.commit()
    
    return jsonify({'message': 'Convention signée avec succès'}), 200

@stages_bp.route('/evaluations', methods=['POST'])
@jwt_required()
@role_required('admin', 'enseignant')
def create_evaluation_stage():
    """Crée une évaluation de stage"""
    data = request.get_json()
    valid, error = validate_required(data, ['convention_id', 'type_evaluation', 'note_globale'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO evaluations_stage (convention_id, type_evaluation, note_globale, commentaires,
                                      points_forts, points_amelioration, evalue_par, date_evaluation)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['convention_id'],
        data['type_evaluation'],
        data['note_globale'],
        data.get('commentaires'),
        data.get('points_forts'),
        data.get('points_amelioration'),
        get_current_user()['id'],
        datetime.now().date()
    ))
    db.commit()
    
    return jsonify({'message': 'Évaluation créée avec succès', 'evaluation_id': cursor.lastrowid}), 201


