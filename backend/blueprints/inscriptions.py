"""
Blueprint pour la gestion des inscriptions en ligne
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import role_required, get_current_user, log_action
from utils.validators import validate_required, validate_email_format, validate_date
from datetime import datetime

inscriptions_bp = Blueprint('inscriptions', __name__)

@inscriptions_bp.route('/candidatures', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_candidatures():
    """Liste toutes les candidatures"""
    statut = request.args.get('statut')
    db = get_db()
    
    query = """
        SELECT c.*, f.libelle as filiere_libelle, n.libelle as niveau_libelle,
               u.nom as traite_par_nom, u.prenom as traite_par_prenom
        FROM candidatures c
        LEFT JOIN filieres f ON c.filiere_souhaitee_id = f.id
        LEFT JOIN niveaux n ON c.niveau_souhaite_id = n.id
        LEFT JOIN users u ON c.traite_par = u.id
        WHERE 1=1
    """
    params = []
    
    if statut:
        query += " AND c.statut = ?"
        params.append(statut)
    
    query += " ORDER BY c.date_candidature DESC"
    
    candidatures = db.execute(query, params).fetchall()
    return jsonify([dict(c) for c in candidatures]), 200

@inscriptions_bp.route('/candidatures', methods=['POST'])
def create_candidature():
    """Crée une nouvelle candidature (publique)"""
    data = request.get_json()
    valid, error = validate_required(data, ['nom', 'prenom', 'email', 'date_naissance', 'filiere_souhaitee_id'])
    if not valid:
        return jsonify({'error': error}), 400
    
    email_valid, email_error = validate_email_format(data['email'])
    if not email_valid:
        return jsonify({'error': email_error}), 400
    
    db = get_db()
    
    # Générer un numéro de dossier unique
    import random
    numero_dossier = f"CAND{datetime.now().year}{random.randint(1000, 9999)}"
    
    # Vérifier l'unicité
    while db.execute("SELECT id FROM candidatures WHERE numero_dossier = ?", (numero_dossier,)).fetchone():
        numero_dossier = f"CAND{datetime.now().year}{random.randint(1000, 9999)}"
    
    cursor = db.execute("""
        INSERT INTO candidatures (
            numero_dossier, nom, prenom, date_naissance, lieu_naissance, sexe,
            nationalite, email, telephone, adresse, filiere_souhaitee_id,
            niveau_souhaite_id, diplome_obtenu, etablissement_origine,
            annee_obtention, documents_paths
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        numero_dossier,
        data['nom'],
        data['prenom'],
        data['date_naissance'],
        data.get('lieu_naissance'),
        data.get('sexe'),
        data.get('nationalite'),
        data['email'],
        data.get('telephone'),
        data.get('adresse'),
        data['filiere_souhaitee_id'],
        data.get('niveau_souhaite_id'),
        data.get('diplome_obtenu'),
        data.get('etablissement_origine'),
        data.get('annee_obtention'),
        data.get('documents_paths')
    ))
    db.commit()
    
    candidature_id = cursor.lastrowid
    
    return jsonify({
        'message': 'Candidature créée avec succès',
        'candidature_id': candidature_id,
        'numero_dossier': numero_dossier
    }), 201

@inscriptions_bp.route('/candidatures/<int:candidature_id>/traiter', methods=['POST'])
@jwt_required()
@role_required('admin')
def traiter_candidature(candidature_id):
    """Traite une candidature (accepter/refuser)"""
    data = request.get_json()
    statut = data.get('statut')  # 'acceptee', 'refusee', 'liste_attente'
    
    if statut not in ['acceptee', 'refusee', 'liste_attente']:
        return jsonify({'error': 'Statut invalide'}), 400
    
    db = get_db()
    candidature = db.execute("SELECT * FROM candidatures WHERE id = ?", (candidature_id,)).fetchone()
    
    if not candidature:
        return jsonify({'error': 'Candidature non trouvée'}), 404
    
    current_user = get_current_user()
    
    # Mettre à jour le statut
    db.execute("""
        UPDATE candidatures
        SET statut = ?, traite_par = ?, date_traitement = ?, notes_complementaires = ?
        WHERE id = ?
    """, (
        statut,
        current_user['id'],
        datetime.now().date(),
        data.get('notes'),
        candidature_id
    ))
    db.commit()
    
    # Si acceptée, créer un compte étudiant
    if statut == 'acceptee':
        # Créer l'utilisateur
        from utils.auth import hash_password
        import secrets
        
        username = f"{candidature['nom'].lower()}.{candidature['prenom'].lower()}"
        password = secrets.token_urlsafe(8)
        password_hash = hash_password(password)
        
        user_cursor = db.execute("""
            INSERT INTO users (username, email, password_hash, role, nom, prenom, telephone, adresse, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            username,
            candidature['email'],
            password_hash,
            'etudiant',
            candidature['nom'],
            candidature['prenom'],
            candidature['telephone'],
            candidature['adresse'],
            True
        ))
        db.commit()
        
        user_id = user_cursor.lastrowid
        
        # Créer le profil étudiant
        numero_etudiant = f"ESA{user_id:06d}"
        db.execute("""
            INSERT INTO etudiants (user_id, numero_etudiant, date_naissance, lieu_naissance, sexe,
                                  nationalite, classe_id, annee_academique_id, date_inscription)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            numero_etudiant,
            candidature['date_naissance'],
            candidature['lieu_naissance'],
            candidature['sexe'],
            candidature['nationalite'],
            None,  # À assigner plus tard
            1,  # Année académique par défaut
            datetime.now().date()
        ))
        db.commit()
        
        log_action(current_user['id'], 'candidature_acceptee', 'candidatures', candidature_id)
        
        return jsonify({
            'message': 'Candidature acceptée et compte étudiant créé',
            'numero_etudiant': numero_etudiant,
            'username': username,
            'password': password  # À envoyer par email en production
        }), 200
    
    log_action(current_user['id'], f'candidature_{statut}', 'candidatures', candidature_id)
    return jsonify({'message': f'Candidature {statut}'}), 200

@inscriptions_bp.route('/candidatures/<numero_dossier>', methods=['GET'])
def get_candidature_by_numero(numero_dossier):
    """Obtient une candidature par son numéro de dossier (publique)"""
    db = get_db()
    candidature = db.execute("""
        SELECT c.*, f.libelle as filiere_libelle, n.libelle as niveau_libelle
        FROM candidatures c
        LEFT JOIN filieres f ON c.filiere_souhaitee_id = f.id
        LEFT JOIN niveaux n ON c.niveau_souhaite_id = n.id
        WHERE c.numero_dossier = ?
    """, (numero_dossier,)).fetchone()
    
    if not candidature:
        return jsonify({'error': 'Candidature non trouvée'}), 404
    
    return jsonify(dict(candidature)), 200

@inscriptions_bp.route('/concours', methods=['GET'])
@jwt_required()
def list_concours():
    """Liste les concours"""
    db = get_db()
    concours = db.execute("""
        SELECT c.*, f.libelle as filiere_libelle, aa.libelle as annee_libelle
        FROM concours c
        LEFT JOIN filieres f ON c.filiere_id = f.id
        JOIN annees_academiques aa ON c.annee_academique_id = aa.id
        WHERE c.is_active = 1
        ORDER BY c.date_concours DESC
    """).fetchall()
    
    return jsonify([dict(c) for c in concours]), 200

@inscriptions_bp.route('/concours', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_concours():
    """Crée un nouveau concours"""
    data = request.get_json()
    valid, error = validate_required(data, ['code', 'libelle', 'date_concours', 'annee_academique_id'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO concours (code, libelle, date_concours, heure_debut, heure_fin,
                             lieu, nombre_places, filiere_id, annee_academique_id, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['code'],
        data['libelle'],
        data['date_concours'],
        data.get('heure_debut'),
        data.get('heure_fin'),
        data.get('lieu'),
        data.get('nombre_places'),
        data.get('filiere_id'),
        data['annee_academique_id'],
        data.get('is_active', True)
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_concours', 'concours', cursor.lastrowid)
    return jsonify({'message': 'Concours créé avec succès'}), 201


