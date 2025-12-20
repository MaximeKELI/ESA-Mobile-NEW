"""
Blueprint pour les fonctionnalités enseignants
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import role_required, get_current_user, log_action
from utils.validators import validate_required, validate_note
from datetime import datetime

enseignant_bp = Blueprint('enseignant', __name__)

@enseignant_bp.route('/classes', methods=['GET'])
@jwt_required()
@role_required('enseignant')
def get_my_classes():
    """Obtient les classes assignées à l'enseignant"""
    current_user = get_current_user()
    db = get_db()
    
    classes = db.execute("""
        SELECT DISTINCT c.*, f.libelle as filiere_libelle, n.libelle as niveau_libelle
        FROM classes c
        JOIN classe_matieres cm ON c.id = cm.classe_id
        JOIN filieres f ON c.filiere_id = f.id
        JOIN niveaux n ON c.niveau_id = n.id
        WHERE cm.enseignant_id = ? AND c.is_active = 1
    """, (current_user['id'],)).fetchall()
    
    return jsonify([dict(classe) for classe in classes]), 200

@enseignant_bp.route('/matieres', methods=['GET'])
@jwt_required()
@role_required('enseignant')
def get_my_matieres():
    """Obtient les matières enseignées par l'enseignant"""
    current_user = get_current_user()
    classe_id = request.args.get('classe_id')
    db = get_db()
    
    query = """
        SELECT DISTINCT m.*, c.libelle as classe_libelle
        FROM matieres m
        JOIN classe_matieres cm ON m.id = cm.matiere_id
        JOIN classes c ON cm.classe_id = c.id
        WHERE cm.enseignant_id = ?
    """
    params = [current_user['id']]
    
    if classe_id:
        query += " AND c.id = ?"
        params.append(classe_id)
    
    matieres = db.execute(query, params).fetchall()
    return jsonify([dict(matiere) for matiere in matieres]), 200

@enseignant_bp.route('/notes', methods=['POST'])
@jwt_required()
@role_required('enseignant')
def create_note():
    """Crée une nouvelle note"""
    data = request.get_json()
    valid, error = validate_required(data, ['etudiant_id', 'matiere_id', 'classe_id', 'type_note', 'note'])
    if not valid:
        return jsonify({'error': error}), 400
    
    note_valid, note_error = validate_note(data['note'])
    if not note_valid:
        return jsonify({'error': note_error}), 400
    
    current_user = get_current_user()
    db = get_db()
    
    # Vérifier que l'enseignant enseigne cette matière dans cette classe
    enseigne = db.execute("""
        SELECT id FROM classe_matieres
        WHERE classe_id = ? AND matiere_id = ? AND enseignant_id = ?
    """, (data['classe_id'], data['matiere_id'], current_user['id'])).fetchone()
    
    if not enseigne:
        return jsonify({'error': 'Vous n\'enseignez pas cette matière dans cette classe'}), 403
    
    # Créer la note
    cursor = db.execute("""
        INSERT INTO notes (etudiant_id, matiere_id, classe_id, type_note, note, coefficient, 
                          date_note, enseignant_id, is_valide)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['etudiant_id'],
        data['matiere_id'],
        data['classe_id'],
        data['type_note'],
        data['note'],
        data.get('coefficient', 1.0),
        data.get('date_note', datetime.now().date().isoformat()),
        current_user['id'],
        False  # Par défaut non validée
    ))
    db.commit()
    
    note_id = cursor.lastrowid
    log_action(current_user['id'], 'creation_note', 'notes', note_id)
    
    return jsonify({'message': 'Note créée avec succès', 'note_id': note_id}), 201

@enseignant_bp.route('/notes/<int:note_id>', methods=['PUT'])
@jwt_required()
@role_required('enseignant')
def update_note(note_id):
    """Modifie une note"""
    data = request.get_json()
    current_user = get_current_user()
    db = get_db()
    
    # Récupérer la note existante
    old_note = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if not old_note:
        return jsonify({'error': 'Note non trouvée'}), 404
    
    # Vérifier que l'enseignant est propriétaire de la note
    if old_note['enseignant_id'] != current_user['id']:
        return jsonify({'error': 'Vous ne pouvez modifier que vos propres notes'}), 403
    
    # Vérifier si la note est déjà validée
    if old_note['is_valide']:
        return jsonify({'error': 'Note déjà validée, modification impossible'}), 400
    
    # Valider la nouvelle note si fournie
    if 'note' in data:
        note_valid, note_error = validate_note(data['note'])
        if not note_valid:
            return jsonify({'error': note_error}), 400
    
    # Mettre à jour la note
    updates = []
    values = []
    
    if 'note' in data:
        updates.append("note = ?")
        values.append(data['note'])
    
    if 'coefficient' in data:
        updates.append("coefficient = ?")
        values.append(data['coefficient'])
    
    if updates:
        updates.append("updated_at = ?")
        values.append(datetime.now())
        values.append(note_id)
        
        db.execute(f"UPDATE notes SET {', '.join(updates)} WHERE id = ?", values)
        
        # Enregistrer dans l'historique
        db.execute("""
            INSERT INTO notes_historique (note_id, ancienne_note, nouvelle_note, modifie_par, raison)
            VALUES (?, ?, ?, ?, ?)
        """, (
            note_id,
            old_note['note'],
            data.get('note', old_note['note']),
            current_user['id'],
            data.get('raison', 'Modification de note')
        ))
        db.commit()
        
        log_action(current_user['id'], 'modification_note', 'notes', note_id, 
                  dict(old_note), data)
    
    return jsonify({'message': 'Note modifiée avec succès'}), 200

@enseignant_bp.route('/notes/<int:note_id>/validate', methods=['POST'])
@jwt_required()
@role_required('enseignant')
def validate_note(note_id):
    """Valide une note"""
    current_user = get_current_user()
    db = get_db()
    
    note = db.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    if not note:
        return jsonify({'error': 'Note non trouvée'}), 404
    
    if note['enseignant_id'] != current_user['id']:
        return jsonify({'error': 'Vous ne pouvez valider que vos propres notes'}), 403
    
    db.execute("""
        UPDATE notes SET is_valide = 1, valide_par = ?, date_validation = ?
        WHERE id = ?
    """, (current_user['id'], datetime.now(), note_id))
    db.commit()
    
    # Recalculer les moyennes
    calculate_moyennes(db, note['etudiant_id'], note['classe_id'], note['matiere_id'])
    
    log_action(current_user['id'], 'validation_note', 'notes', note_id)
    
    return jsonify({'message': 'Note validée avec succès'}), 200

@enseignant_bp.route('/absences', methods=['POST'])
@jwt_required()
@role_required('enseignant')
def create_absence():
    """Enregistre une absence"""
    data = request.get_json()
    valid, error = validate_required(data, ['etudiant_id', 'classe_id', 'date_absence', 'type_absence'])
    if not valid:
        return jsonify({'error': error}), 400
    
    current_user = get_current_user()
    db = get_db()
    
    cursor = db.execute("""
        INSERT INTO absences (etudiant_id, classe_id, matiere_id, date_absence, 
                            heure_debut, heure_fin, type_absence, justificatif, enseignant_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['etudiant_id'],
        data['classe_id'],
        data.get('matiere_id'),
        data['date_absence'],
        data.get('heure_debut'),
        data.get('heure_fin'),
        data['type_absence'],
        data.get('justificatif'),
        current_user['id']
    ))
    db.commit()
    
    log_action(current_user['id'], 'creation_absence', 'absences', cursor.lastrowid)
    
    return jsonify({'message': 'Absence enregistrée avec succès'}), 201

@enseignant_bp.route('/etudiants/<int:etudiant_id>/notes', methods=['GET'])
@jwt_required()
@role_required('enseignant')
def get_student_notes(etudiant_id):
    """Obtient les notes d'un étudiant"""
    matiere_id = request.args.get('matiere_id')
    classe_id = request.args.get('classe_id')
    current_user = get_current_user()
    db = get_db()
    
    query = """
        SELECT n.*, m.libelle as matiere_libelle, m.code as matiere_code
        FROM notes n
        JOIN matieres m ON n.matiere_id = m.id
        WHERE n.etudiant_id = ? AND n.enseignant_id = ?
    """
    params = [etudiant_id, current_user['id']]
    
    if matiere_id:
        query += " AND n.matiere_id = ?"
        params.append(matiere_id)
    
    if classe_id:
        query += " AND n.classe_id = ?"
        params.append(classe_id)
    
    query += " ORDER BY n.date_note DESC"
    
    notes = db.execute(query, params).fetchall()
    return jsonify([dict(note) for note in notes]), 200

def calculate_moyennes(db, etudiant_id, classe_id, matiere_id):
    """Calcule les moyennes pour un étudiant dans une matière"""
    # Récupérer toutes les notes validées
    notes = db.execute("""
        SELECT note, coefficient FROM notes
        WHERE etudiant_id = ? AND matiere_id = ? AND classe_id = ? AND is_valide = 1
    """, (etudiant_id, matiere_id, classe_id)).fetchall()
    
    if not notes:
        return
    
    # Calculer la moyenne pondérée
    total_points = sum(note['note'] * note['coefficient'] for note in notes)
    total_coeff = sum(note['coefficient'] for note in notes)
    
    if total_coeff > 0:
        moyenne = total_points / total_coeff
        
        # Obtenir l'année académique
        classe = db.execute("SELECT annee_academique_id FROM classes WHERE id = ?", (classe_id,)).fetchone()
        
        # Insérer ou mettre à jour la moyenne
        existing = db.execute("""
            SELECT id FROM moyennes
            WHERE etudiant_id = ? AND matiere_id = ? AND classe_id = ? AND periode = 'annuel'
        """, (etudiant_id, matiere_id, classe_id)).fetchone()
        
        if existing:
            db.execute("""
                UPDATE moyennes SET moyenne = ?
                WHERE id = ?
            """, (moyenne, existing['id']))
        else:
            db.execute("""
                INSERT INTO moyennes (etudiant_id, matiere_id, classe_id, moyenne, periode, annee_academique_id)
                VALUES (?, ?, ?, ?, 'annuel', ?)
            """, (etudiant_id, matiere_id, classe_id, moyenne, classe['annee_academique_id']))
        
        db.commit()
        
        # Recalculer le classement
        calculate_classement(db, etudiant_id, classe_id)

def calculate_classement(db, etudiant_id, classe_id):
    """Calcule le classement d'un étudiant"""
    # Obtenir toutes les moyennes de la classe
    moyennes = db.execute("""
        SELECT e.id as etudiant_id, AVG(m.moyenne) as moyenne_generale
        FROM etudiants e
        JOIN moyennes m ON e.id = m.etudiant_id
        WHERE e.classe_id = ? AND m.periode = 'annuel'
        GROUP BY e.id
        ORDER BY moyenne_generale DESC
    """, (classe_id,)).fetchall()
    
    # Obtenir l'année académique
    classe = db.execute("SELECT annee_academique_id FROM classes WHERE id = ?", (classe_id,)).fetchone()
    
    # Mettre à jour les classements
    for rang, etudiant_moyenne in enumerate(moyennes, start=1):
        existing = db.execute("""
            SELECT id FROM classements
            WHERE etudiant_id = ? AND classe_id = ? AND periode = 'annuel'
        """, (etudiant_moyenne['etudiant_id'], classe_id)).fetchone()
        
        if existing:
            db.execute("""
                UPDATE classements SET rang = ?, moyenne_generale = ?
                WHERE id = ?
            """, (rang, etudiant_moyenne['moyenne_generale'], existing['id']))
        else:
            db.execute("""
                INSERT INTO classements (etudiant_id, classe_id, rang, moyenne_generale, periode, annee_academique_id)
                VALUES (?, ?, ?, ?, 'annuel', ?)
            """, (etudiant_moyenne['etudiant_id'], classe_id, rang, 
                  etudiant_moyenne['moyenne_generale'], classe['annee_academique_id']))
    
    db.commit()


