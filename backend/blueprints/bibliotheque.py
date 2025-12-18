"""
Blueprint pour la gestion de la bibliothèque
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import role_required, get_current_user, log_action
from utils.validators import validate_required
from datetime import datetime, timedelta

bibliotheque_bp = Blueprint('bibliotheque', __name__)

@bibliotheque_bp.route('/ouvrages', methods=['GET'])
@jwt_required()
def list_ouvrages():
    """Liste les ouvrages de la bibliothèque"""
    recherche = request.args.get('q')
    categorie = request.args.get('categorie')
    db = get_db()
    
    query = """
        SELECT o.*, 
               (SELECT COUNT(*) FROM exemplaires e WHERE e.ouvrage_id = o.id AND e.etat != 'perdu') as total_exemplaires,
               (SELECT COUNT(*) FROM exemplaires e 
                JOIN emprunts em ON e.id = em.exemplaire_id 
                WHERE e.ouvrage_id = o.id AND em.statut = 'en_cours') as exemplaires_empruntes
        FROM ouvrages o
        WHERE o.is_active = 1
    """
    params = []
    
    if recherche:
        query += " AND (o.titre LIKE ? OR o.auteur LIKE ? OR o.isbn LIKE ?)"
        search_term = f"%{recherche}%"
        params.extend([search_term, search_term, search_term])
    
    if categorie:
        query += " AND o.categorie = ?"
        params.append(categorie)
    
    query += " ORDER BY o.titre"
    
    ouvrages = db.execute(query, params).fetchall()
    return jsonify([dict(o) for o in ouvrages]), 200

@bibliotheque_bp.route('/ouvrages', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_ouvrage():
    """Ajoute un nouvel ouvrage"""
    data = request.get_json()
    valid, error = validate_required(data, ['titre'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO ouvrages (isbn, titre, auteur, editeur, annee_publication, langue,
                             categorie, nombre_exemplaires, nombre_disponibles, cote, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('isbn'),
        data['titre'],
        data.get('auteur'),
        data.get('editeur'),
        data.get('annee_publication'),
        data.get('langue', 'français'),
        data.get('categorie'),
        data.get('nombre_exemplaires', 1),
        data.get('nombre_disponibles', 1),
        data.get('cote'),
        data.get('description')
    ))
    db.commit()
    
    ouvrage_id = cursor.lastrowid
    
    # Créer les exemplaires
    nombre_exemplaires = data.get('nombre_exemplaires', 1)
    for i in range(nombre_exemplaires):
        numero_exemplaire = f"EX{ouvrage_id:04d}-{i+1:03d}"
        db.execute("""
            INSERT INTO exemplaires (ouvrage_id, numero_exemplaire, etat, date_acquisition,
                                   prix_acquisition, localisation)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            ouvrage_id,
            numero_exemplaire,
            'neuf',
            datetime.now().date(),
            data.get('prix_acquisition'),
            data.get('localisation')
        ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_ouvrage', 'ouvrages', ouvrage_id)
    return jsonify({'message': 'Ouvrage ajouté avec succès', 'ouvrage_id': ouvrage_id}), 201

@bibliotheque_bp.route('/emprunts', methods=['GET'])
@jwt_required()
def list_emprunts():
    """Liste les emprunts"""
    emprunteur_id = request.args.get('emprunteur_id')
    statut = request.args.get('statut')
    db = get_db()
    current_user = get_current_user()
    
    query = """
        SELECT e.*, ex.numero_exemplaire, o.titre as ouvrage_titre, o.auteur as ouvrage_auteur,
               u.nom as emprunteur_nom, u.prenom as emprunteur_prenom
        FROM emprunts e
        JOIN exemplaires ex ON e.exemplaire_id = ex.id
        JOIN ouvrages o ON ex.ouvrage_id = o.id
        JOIN users u ON e.emprunteur_id = u.id
        WHERE 1=1
    """
    params = []
    
    if current_user['role'] == 'etudiant':
        etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                             (current_user['id'],)).fetchone()
        if etudiant:
            query += " AND e.emprunteur_id = ?"
            params.append(current_user['id'])
    
    if emprunteur_id and current_user['role'] in ['admin', 'comptabilite']:
        query += " AND e.emprunteur_id = ?"
        params.append(emprunteur_id)
    
    if statut:
        query += " AND e.statut = ?"
        params.append(statut)
    
    query += " ORDER BY e.date_emprunt DESC"
    
    emprunts = db.execute(query, params).fetchall()
    return jsonify([dict(e) for e in emprunts]), 200

@bibliotheque_bp.route('/emprunts', methods=['POST'])
@jwt_required()
@role_required('admin', 'comptabilite')
def create_emprunt():
    """Crée un nouvel emprunt"""
    data = request.get_json()
    valid, error = validate_required(data, ['exemplaire_id', 'emprunteur_id', 'date_retour_prevue'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    
    # Vérifier que l'exemplaire est disponible
    exemplaire = db.execute("""
        SELECT e.*, o.titre FROM exemplaires e
        JOIN ouvrages o ON e.ouvrage_id = o.id
        WHERE e.id = ?
    """, (data['exemplaire_id'],)).fetchone()
    
    if not exemplaire:
        return jsonify({'error': 'Exemplaire non trouvé'}), 404
    
    # Vérifier si l'exemplaire est déjà emprunté
    emprunt_actif = db.execute("""
        SELECT id FROM emprunts
        WHERE exemplaire_id = ? AND statut = 'en_cours'
    """, (data['exemplaire_id'],)).fetchone()
    
    if emprunt_actif:
        return jsonify({'error': 'Cet exemplaire est déjà emprunté'}), 400
    
    # Vérifier le nombre d'emprunts en cours de l'utilisateur
    emprunts_en_cours = db.execute("""
        SELECT COUNT(*) as count FROM emprunts
        WHERE emprunteur_id = ? AND statut = 'en_cours'
    """, (data['emprunteur_id'],)).fetchone()['count']
    
    if emprunts_en_cours >= 5:  # Limite de 5 emprunts
        return jsonify({'error': 'Limite d\'emprunts atteinte (5 maximum)'}), 400
    
    cursor = db.execute("""
        INSERT INTO emprunts (exemplaire_id, emprunteur_id, date_emprunt, date_retour_prevue, statut)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data['exemplaire_id'],
        data['emprunteur_id'],
        data.get('date_emprunt', datetime.now().date()),
        data['date_retour_prevue'],
        'en_cours'
    ))
    db.commit()
    
    # Mettre à jour le nombre d'exemplaires disponibles
    db.execute("""
        UPDATE ouvrages
        SET nombre_disponibles = nombre_disponibles - 1
        WHERE id = ?
    """, (exemplaire['ouvrage_id'],))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_emprunt', 'emprunts', cursor.lastrowid)
    
    return jsonify({'message': 'Emprunt créé avec succès', 'emprunt_id': cursor.lastrowid}), 201

@bibliotheque_bp.route('/emprunts/<int:emprunt_id>/retour', methods=['POST'])
@jwt_required()
@role_required('admin', 'comptabilite')
def retour_emprunt(emprunt_id):
    """Enregistre le retour d'un emprunt"""
    data = request.get_json()
    db = get_db()
    
    emprunt = db.execute("""
        SELECT e.*, ex.ouvrage_id FROM emprunts e
        JOIN exemplaires ex ON e.exemplaire_id = ex.id
        WHERE e.id = ?
    """, (emprunt_id,)).fetchone()
    
    if not emprunt:
        return jsonify({'error': 'Emprunt non trouvé'}), 404
    
    if emprunt['statut'] != 'en_cours':
        return jsonify({'error': 'Cet emprunt est déjà retourné'}), 400
    
    date_retour = data.get('date_retour_effective', datetime.now().date())
    
    # Vérifier les retards
    date_retour_prevue = datetime.strptime(emprunt['date_retour_prevue'], '%Y-%m-%d').date()
    jours_retard = (date_retour - date_retour_prevue).days if date_retour > date_retour_prevue else 0
    
    statut = 'retarde' if jours_retard > 0 else 'retourne'
    
    # Mettre à jour l'emprunt
    db.execute("""
        UPDATE emprunts
        SET date_retour_effective = ?, statut = ?
        WHERE id = ?
    """, (date_retour, statut, emprunt_id))
    
    # Mettre à jour le nombre d'exemplaires disponibles
    db.execute("""
        UPDATE ouvrages
        SET nombre_disponibles = nombre_disponibles + 1
        WHERE id = ?
    """, (emprunt['ouvrage_id'],))
    
    # Créer une amende si retard
    if jours_retard > 0:
        montant_amende = jours_retard * 100  # 100 FCFA par jour de retard
        db.execute("""
            INSERT INTO amendes (emprunt_id, type_amende, montant, date_amende, statut)
            VALUES (?, 'retard', ?, ?, 'impayee')
        """, (emprunt_id, montant_amende, datetime.now().date()))
    
    db.commit()
    
    log_action(get_current_user()['id'], 'retour_emprunt', 'emprunts', emprunt_id)
    
    return jsonify({
        'message': 'Retour enregistré avec succès',
        'jours_retard': jours_retard,
        'amende': jours_retard * 100 if jours_retard > 0 else 0
    }), 200

@bibliotheque_bp.route('/reservations', methods=['POST'])
@jwt_required()
def reserver_ouvrage():
    """Réserve un ouvrage"""
    data = request.get_json()
    valid, error = validate_required(data, ['ouvrage_id'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    current_user = get_current_user()
    
    # Vérifier si l'ouvrage est disponible
    ouvrage = db.execute("SELECT nombre_disponibles FROM ouvrages WHERE id = ?", 
                        (data['ouvrage_id'],)).fetchone()
    
    if not ouvrage or ouvrage['nombre_disponibles'] > 0:
        return jsonify({'error': 'L\'ouvrage est disponible, pas besoin de réserver'}), 400
    
    # Vérifier si l'utilisateur a déjà une réservation active
    existing = db.execute("""
        SELECT id FROM reservations_bibliotheque
        WHERE ouvrage_id = ? AND reserve_par = ? AND statut = 'active'
    """, (data['ouvrage_id'], current_user['id'])).fetchone()
    
    if existing:
        return jsonify({'error': 'Vous avez déjà une réservation active pour cet ouvrage'}), 400
    
    # Créer la réservation
    date_expiration = datetime.now().date() + timedelta(days=7)
    cursor = db.execute("""
        INSERT INTO reservations_bibliotheque (ouvrage_id, reserve_par, date_expiration, statut)
        VALUES (?, ?, ?, 'active')
    """, (data['ouvrage_id'], current_user['id'], date_expiration))
    db.commit()
    
    return jsonify({'message': 'Réservation créée avec succès', 'reservation_id': cursor.lastrowid}), 201

