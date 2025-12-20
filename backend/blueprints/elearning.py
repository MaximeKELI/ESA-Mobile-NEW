"""
Blueprint pour l'E-Learning intégré
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import role_required, get_current_user, log_action
from utils.validators import validate_required
from datetime import datetime
import os

elearning_bp = Blueprint('elearning', __name__)

@elearning_bp.route('/cours', methods=['GET'])
@jwt_required()
def list_cours():
    """Liste les cours en ligne"""
    matiere_id = request.args.get('matiere_id')
    classe_id = request.args.get('classe_id')
    is_public = request.args.get('is_public')
    db = get_db()
    current_user = get_current_user()
    
    query = """
        SELECT c.*, m.libelle as matiere_libelle, cl.libelle as classe_libelle,
               u.nom as enseignant_nom, u.prenom as enseignant_prenom
        FROM cours_online c
        LEFT JOIN matieres m ON c.matiere_id = m.id
        LEFT JOIN classes cl ON c.classe_id = cl.id
        JOIN users u ON c.enseignant_id = u.id
        WHERE c.is_active = 1
    """
    params = []
    
    if matiere_id:
        query += " AND c.matiere_id = ?"
        params.append(matiere_id)
    
    if classe_id:
        query += " AND c.classe_id = ?"
        params.append(classe_id)
    
    if is_public == 'true':
        query += " AND c.is_public = 1"
    elif current_user['role'] == 'etudiant':
        # Étudiants voient seulement les cours de leur classe ou publics
        etudiant = db.execute("SELECT classe_id FROM etudiants WHERE user_id = ?", 
                             (current_user['id'],)).fetchone()
        if etudiant and etudiant['classe_id']:
            query += " AND (c.classe_id = ? OR c.is_public = 1)"
            params.append(etudiant['classe_id'])
        else:
            query += " AND c.is_public = 1"
    
    query += " ORDER BY c.date_creation DESC"
    
    cours = db.execute(query, params).fetchall()
    return jsonify([dict(c) for c in cours]), 200

@elearning_bp.route('/cours', methods=['POST'])
@jwt_required()
@role_required('enseignant', 'admin')
def create_cours():
    """Crée un nouveau cours en ligne"""
    data = request.get_json()
    valid, error = validate_required(data, ['code', 'titre', 'enseignant_id'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO cours_online (code, titre, description, matiere_id, classe_id, enseignant_id,
                                 type_cours, duree_estimee, niveau_difficulte, is_public, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['code'],
        data['titre'],
        data.get('description'),
        data.get('matiere_id'),
        data.get('classe_id'),
        data['enseignant_id'],
        data.get('type_cours', 'mixte'),
        data.get('duree_estimee'),
        data.get('niveau_difficulte', 'intermediaire'),
        data.get('is_public', False),
        data.get('is_active', True)
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_cours_online', 'cours_online', cursor.lastrowid)
    return jsonify({'message': 'Cours créé avec succès', 'cours_id': cursor.lastrowid}), 201

@elearning_bp.route('/cours/<int:cours_id>/modules', methods=['GET'])
@jwt_required()
def list_modules(cours_id):
    """Liste les modules d'un cours"""
    db = get_db()
    modules = db.execute("""
        SELECT * FROM modules_cours
        WHERE cours_id = ?
        ORDER BY ordre
    """, (cours_id,)).fetchall()
    return jsonify([dict(m) for m in modules]), 200

@elearning_bp.route('/cours/<int:cours_id>/modules', methods=['POST'])
@jwt_required()
@role_required('enseignant', 'admin')
def create_module(cours_id):
    """Crée un module pour un cours"""
    data = request.get_json()
    valid, error = validate_required(data, ['titre', 'ordre', 'type_module'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO modules_cours (cours_id, titre, description, ordre, type_module, contenu,
                                 duree_estimee, is_obligatoire)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cours_id,
        data['titre'],
        data.get('description'),
        data['ordre'],
        data['type_module'],
        data.get('contenu'),
        data.get('duree_estimee'),
        data.get('is_obligatoire', True)
    ))
    db.commit()
    
    return jsonify({'message': 'Module créé avec succès', 'module_id': cursor.lastrowid}), 201

@elearning_bp.route('/quiz', methods=['POST'])
@jwt_required()
@role_required('enseignant', 'admin')
def create_quiz():
    """Crée un quiz"""
    data = request.get_json()
    valid, error = validate_required(data, ['titre', 'cours_id'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO quiz (module_id, cours_id, titre, description, type_quiz, duree_minutes,
                         nombre_tentatives_max, note_minimale, is_actif)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get('module_id'),
        data['cours_id'],
        data['titre'],
        data.get('description'),
        data.get('type_quiz', 'formative'),
        data.get('duree_minutes'),
        data.get('nombre_tentatives_max', 3),
        data.get('note_minimale', 10.0),
        data.get('is_actif', True)
    ))
    db.commit()
    
    return jsonify({'message': 'Quiz créé avec succès', 'quiz_id': cursor.lastrowid}), 201

@elearning_bp.route('/quiz/<int:quiz_id>/questions', methods=['POST'])
@jwt_required()
@role_required('enseignant', 'admin')
def add_question(quiz_id):
    """Ajoute une question à un quiz"""
    data = request.get_json()
    valid, error = validate_required(data, ['question', 'type_question', 'reponse_correcte'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO questions_quiz (quiz_id, question, type_question, points, ordre,
                                   reponses_possibles, reponse_correcte, explication)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        quiz_id,
        data['question'],
        data['type_question'],
        data.get('points', 1.0),
        data.get('ordre', 1),
        data.get('reponses_possibles'),
        data['reponse_correcte'],
        data.get('explication')
    ))
    db.commit()
    
    return jsonify({'message': 'Question ajoutée avec succès', 'question_id': cursor.lastrowid}), 201

@elearning_bp.route('/quiz/<int:quiz_id>/tenter', methods=['POST'])
@jwt_required()
def tenter_quiz(quiz_id):
    """Tente un quiz"""
    data = request.get_json()
    current_user = get_current_user()
    db = get_db()
    
    # Vérifier que l'utilisateur est étudiant
    if current_user['role'] != 'etudiant':
        return jsonify({'error': 'Seuls les étudiants peuvent tenter les quiz'}), 403
    
    etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Profil étudiant non trouvé'}), 404
    
    # Vérifier le nombre de tentatives
    quiz = db.execute("SELECT * FROM quiz WHERE id = ?", (quiz_id,)).fetchone()
    if not quiz:
        return jsonify({'error': 'Quiz non trouvé'}), 404
    
    tentatives = db.execute("""
        SELECT COUNT(*) as count FROM tentatives_quiz
        WHERE quiz_id = ? AND etudiant_id = ?
    """, (quiz_id, etudiant['id'])).fetchone()['count']
    
    if tentatives >= quiz['nombre_tentatives_max']:
        return jsonify({'error': 'Nombre maximum de tentatives atteint'}), 400
    
    # Récupérer les questions
    questions = db.execute("""
        SELECT * FROM questions_quiz
        WHERE quiz_id = ?
        ORDER BY ordre
    """, (quiz_id,)).fetchall()
    
    # Calculer la note
    reponses = data.get('reponses', {})  # {question_id: reponse}
    points_total = 0
    points_obtenus = 0
    
    for question in questions:
        points_total += question['points']
        reponse_etudiant = reponses.get(str(question['id']))
        if reponse_etudiant:
            # Comparer avec la réponse correcte (simplifié)
            import json
            reponse_correcte = json.loads(question['reponse_correcte']) if isinstance(question['reponse_correcte'], str) else question['reponse_correcte']
            if str(reponse_etudiant) == str(reponse_correcte):
                points_obtenus += question['points']
    
    note_obtenue = (points_obtenus / points_total * 20) if points_total > 0 else 0
    
    # Enregistrer la tentative
    cursor = db.execute("""
        INSERT INTO tentatives_quiz (quiz_id, etudiant_id, note_obtenue, nombre_tentative,
                                   duree_secondes, reponses, is_termine)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        quiz_id,
        etudiant['id'],
        note_obtenue,
        tentatives + 1,
        data.get('duree_secondes'),
        json.dumps(reponses),
        True
    ))
    db.commit()
    
    return jsonify({
        'message': 'Quiz terminé',
        'note_obtenue': round(note_obtenue, 2),
        'note_minimale': quiz['note_minimale'],
        'reussi': note_obtenue >= quiz['note_minimale']
    }), 200

@elearning_bp.route('/cours/<int:cours_id>/progression', methods=['GET'])
@jwt_required()
def get_progression(cours_id):
    """Obtient la progression d'un étudiant dans un cours"""
    current_user = get_current_user()
    db = get_db()
    
    if current_user['role'] != 'etudiant':
        return jsonify({'error': 'Accès réservé aux étudiants'}), 403
    
    etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Profil étudiant non trouvé'}), 404
    
    progression = db.execute("""
        SELECT * FROM progression_cours
        WHERE cours_id = ? AND etudiant_id = ?
    """, (cours_id, etudiant['id'])).fetchone()
    
    if not progression:
        # Créer une progression initiale
        db.execute("""
            INSERT INTO progression_cours (cours_id, etudiant_id, date_debut)
            VALUES (?, ?, ?)
        """, (cours_id, etudiant['id'], datetime.now().date()))
        db.commit()
        progression = db.execute("""
            SELECT * FROM progression_cours
            WHERE cours_id = ? AND etudiant_id = ?
        """, (cours_id, etudiant['id'])).fetchone()
    
    return jsonify(dict(progression)), 200

@elearning_bp.route('/cours/<int:cours_id>/progression', methods=['PUT'])
@jwt_required()
def update_progression(cours_id):
    """Met à jour la progression d'un étudiant"""
    data = request.get_json()
    current_user = get_current_user()
    db = get_db()
    
    if current_user['role'] != 'etudiant':
        return jsonify({'error': 'Accès réservé aux étudiants'}), 403
    
    etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Profil étudiant non trouvé'}), 404
    
    db.execute("""
        UPDATE progression_cours
        SET pourcentage_completion = ?, module_id = ?, temps_total_minutes = ?,
            date_derniere_activite = ?, is_termine = ?, date_completion = ?
        WHERE cours_id = ? AND etudiant_id = ?
    """, (
        data.get('pourcentage_completion', 0),
        data.get('module_id'),
        data.get('temps_total_minutes', 0),
        datetime.now(),
        data.get('is_termine', False),
        datetime.now().date() if data.get('is_termine') else None,
        cours_id,
        etudiant['id']
    ))
    db.commit()
    
    return jsonify({'message': 'Progression mise à jour'}), 200


