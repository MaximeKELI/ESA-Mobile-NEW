"""
Blueprint pour les fonctionnalités parents
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import get_current_user
import os

parent_bp = Blueprint('parent', __name__)

@parent_bp.route('/enfants', methods=['GET'])
@jwt_required()
def get_enfants():
    """Obtient la liste des enfants du parent"""
    current_user = get_current_user()
    db = get_db()
    
    # Obtenir l'ID du parent
    parent = db.execute("SELECT id FROM parents WHERE user_id = ?", 
                        (current_user['id'],)).fetchone()
    if not parent:
        return jsonify({'error': 'Profil parent non trouvé'}), 404
    
    # Obtenir les enfants
    enfants = db.execute("""
        SELECT e.*, u.nom, u.prenom, u.email, u.telephone,
               c.libelle as classe_libelle, c.code as classe_code
        FROM etudiants e
        JOIN parent_etudiants pe ON e.id = pe.etudiant_id
        JOIN users u ON e.user_id = u.id
        LEFT JOIN classes c ON e.classe_id = c.id
        WHERE pe.parent_id = ?
    """, (parent['id'],)).fetchall()
    
    return jsonify([dict(enfant) for enfant in enfants]), 200

@parent_bp.route('/enfants/<int:etudiant_id>/notes', methods=['GET'])
@jwt_required()
def get_enfant_notes(etudiant_id):
    """Obtient les notes d'un enfant"""
    current_user = get_current_user()
    db = get_db()
    
    # Vérifier que l'étudiant est bien un enfant du parent
    if not is_parent_of_student(db, current_user['id'], etudiant_id):
        return jsonify({'error': 'Accès refusé'}), 403
    
    # Utiliser la fonction du blueprint étudiant
    from blueprints.etudiant import get_my_notes as get_notes
    # Simuler l'utilisateur étudiant pour récupérer les notes
    etudiant = db.execute("SELECT user_id FROM etudiants WHERE id = ?", 
                         (etudiant_id,)).fetchone()
    
    notes = db.execute("""
        SELECT n.*, m.libelle as matiere_libelle, m.code as matiere_code
        FROM notes n
        JOIN matieres m ON n.matiere_id = m.id
        WHERE n.etudiant_id = ? AND n.is_valide = 1
        ORDER BY n.date_note DESC
    """, (etudiant_id,)).fetchall()
    
    return jsonify([dict(note) for note in notes]), 200

@parent_bp.route('/enfants/<int:etudiant_id>/moyennes', methods=['GET'])
@jwt_required()
def get_enfant_moyennes(etudiant_id):
    """Obtient les moyennes d'un enfant"""
    current_user = get_current_user()
    periode = request.args.get('periode', 'annuel')
    db = get_db()
    
    if not is_parent_of_student(db, current_user['id'], etudiant_id):
        return jsonify({'error': 'Accès refusé'}), 403
    
    moyennes = db.execute("""
        SELECT m.*, mat.libelle as matiere_libelle, mat.code as matiere_code
        FROM moyennes m
        JOIN matieres mat ON m.matiere_id = mat.id
        WHERE m.etudiant_id = ? AND m.periode = ?
        ORDER BY matiere_libelle
    """, (etudiant_id, periode)).fetchall()
    
    moyenne_generale = sum(m['moyenne'] for m in moyennes) / len(moyennes) if moyennes else 0
    
    return jsonify({
        'moyennes': [dict(m) for m in moyennes],
        'moyenne_generale': round(moyenne_generale, 2)
    }), 200

@parent_bp.route('/enfants/<int:etudiant_id>/absences', methods=['GET'])
@jwt_required()
def get_enfant_absences(etudiant_id):
    """Obtient les absences d'un enfant"""
    current_user = get_current_user()
    db = get_db()
    
    if not is_parent_of_student(db, current_user['id'], etudiant_id):
        return jsonify({'error': 'Accès refusé'}), 403
    
    absences = db.execute("""
        SELECT a.*, m.libelle as matiere_libelle, c.libelle as classe_libelle
        FROM absences a
        LEFT JOIN matieres m ON a.matiere_id = m.id
        JOIN classes c ON a.classe_id = c.id
        WHERE a.etudiant_id = ?
        ORDER BY a.date_absence DESC
    """, (etudiant_id,)).fetchall()
    
    return jsonify([dict(absence) for absence in absences]), 200

@parent_bp.route('/enfants/<int:etudiant_id>/situation-financiere', methods=['GET'])
@jwt_required()
def get_enfant_financial_situation(etudiant_id):
    """Obtient la situation financière d'un enfant"""
    current_user = get_current_user()
    db = get_db()
    
    if not is_parent_of_student(db, current_user['id'], etudiant_id):
        return jsonify({'error': 'Accès refusé'}), 403
    
    from blueprints.comptabilite import get_financial_situation as get_fin_sit
    return get_fin_sit(etudiant_id)

@parent_bp.route('/enfants/<int:etudiant_id>/bulletin', methods=['GET'])
@jwt_required()
def get_enfant_bulletin(etudiant_id):
    """Obtient le bulletin d'un enfant"""
    current_user = get_current_user()
    periode = request.args.get('periode', 'annuel')
    db = get_db()
    
    if not is_parent_of_student(db, current_user['id'], etudiant_id):
        return jsonify({'error': 'Accès refusé'}), 403
    
    # Utiliser la fonction du blueprint étudiant
    from blueprints.etudiant import get_bulletin as get_bul
    # Note: Cette fonction nécessite d'être adaptée pour accepter un etudiant_id
    
    etudiant = db.execute("""
        SELECT e.*, u.nom, u.prenom, c.libelle as classe_libelle
        FROM etudiants e
        JOIN users u ON e.user_id = u.id
        LEFT JOIN classes c ON e.classe_id = c.id
        WHERE e.id = ?
    """, (etudiant_id,)).fetchone()
    
    if not etudiant:
        return jsonify({'error': 'Étudiant non trouvé'}), 404
    
    # Obtenir les moyennes
    moyennes = db.execute("""
        SELECT m.*, mat.libelle as matiere, mat.coefficient
        FROM moyennes m
        JOIN matieres mat ON m.matiere_id = mat.id
        WHERE m.etudiant_id = ? AND m.periode = ?
    """, (etudiant_id, periode)).fetchall()
    
    from utils.pdf_generator import generate_bulletin
    from flask import send_file
    
    output_path = os.path.join(
        request.application.config['UPLOAD_FOLDER'],
        'pdf',
        f'bulletin_{etudiant_id}_{periode}.pdf'
    )
    
    etudiant_data = {
        'nom': etudiant['nom'],
        'prenom': etudiant['prenom'],
        'classe': etudiant['classe_libelle'],
        'periode': periode,
        'moyenne_generale': sum(m['moyenne'] for m in moyennes) / len(moyennes) if moyennes else 0
    }
    
    notes_data = [{
        'matiere': m['matiere'],
        'note': m['moyenne'],
        'coefficient': m['coefficient'],
        'moyenne': m['moyenne']
    } for m in moyennes]
    
    generate_bulletin(etudiant_data, notes_data, output_path)
    
    return send_file(output_path, mimetype='application/pdf', as_attachment=True,
                    download_name=f'bulletin_{etudiant["numero_etudiant"]}.pdf')

@parent_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Obtient les notifications du parent"""
    current_user = get_current_user()
    is_lu = request.args.get('is_lu')
    db = get_db()
    
    query = "SELECT * FROM notifications WHERE user_id = ?"
    params = [current_user['id']]
    
    if is_lu is not None:
        query += " AND is_lu = ?"
        params.append(1 if is_lu == 'true' else 0)
    
    query += " ORDER BY created_at DESC LIMIT 50"
    
    notifications = db.execute(query, params).fetchall()
    return jsonify([dict(n) for n in notifications]), 200

def is_parent_of_student(db, parent_user_id, etudiant_id):
    """Vérifie si le parent est bien parent de l'étudiant"""
    parent = db.execute("SELECT id FROM parents WHERE user_id = ?", 
                       (parent_user_id,)).fetchone()
    if not parent:
        return False
    
    relation = db.execute("""
        SELECT id FROM parent_etudiants
        WHERE parent_id = ? AND etudiant_id = ?
    """, (parent['id'], etudiant_id)).fetchone()
    
    return relation is not None

