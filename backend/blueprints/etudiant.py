"""
Blueprint pour les fonctionnalités étudiants
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import get_current_user
from utils.pdf_generator import generate_bulletin
from datetime import datetime
import os

etudiant_bp = Blueprint('etudiant', __name__)

@etudiant_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtient le profil de l'étudiant connecté"""
    current_user = get_current_user()
    db = get_db()
    
    etudiant = db.execute("""
        SELECT e.*, u.nom, u.prenom, u.email, u.telephone, u.adresse, u.photo_path,
               c.libelle as classe_libelle, c.code as classe_code
        FROM etudiants e
        JOIN users u ON e.user_id = u.id
        LEFT JOIN classes c ON e.classe_id = c.id
        WHERE e.user_id = ?
    """, (current_user['id'],)).fetchone()
    
    if not etudiant:
        return jsonify({'error': 'Profil étudiant non trouvé'}), 404
    
    return jsonify(dict(etudiant)), 200

@etudiant_bp.route('/notes', methods=['GET'])
@jwt_required()
def get_my_notes():
    """Obtient les notes de l'étudiant connecté"""
    current_user = get_current_user()
    matiere_id = request.args.get('matiere_id')
    type_note = request.args.get('type_note')
    db = get_db()
    
    # Vérifier que l'utilisateur est un étudiant
    etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Accès refusé'}), 403
    
    # Vérifier les impayés (verrouillage)
    has_unpaid = check_unpaid_fees(db, etudiant['id'])
    if has_unpaid:
        return jsonify({
            'error': 'Accès restreint: frais impayés',
            'has_unpaid': True
        }), 403
    
    query = """
        SELECT n.*, m.libelle as matiere_libelle, m.code as matiere_code, m.coefficient as matiere_coefficient
        FROM notes n
        JOIN matieres m ON n.matiere_id = m.id
        WHERE n.etudiant_id = ? AND n.is_valide = 1
    """
    params = [etudiant['id']]
    
    if matiere_id:
        query += " AND n.matiere_id = ?"
        params.append(matiere_id)
    
    if type_note:
        query += " AND n.type_note = ?"
        params.append(type_note)
    
    query += " ORDER BY n.date_note DESC"
    
    notes = db.execute(query, params).fetchall()
    return jsonify([dict(note) for note in notes]), 200

@etudiant_bp.route('/moyennes', methods=['GET'])
@jwt_required()
def get_my_moyennes():
    """Obtient les moyennes de l'étudiant"""
    current_user = get_current_user()
    periode = request.args.get('periode', 'annuel')
    db = get_db()
    
    etudiant = db.execute("SELECT id, classe_id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Accès refusé'}), 403
    
    has_unpaid = check_unpaid_fees(db, etudiant['id'])
    if has_unpaid:
        return jsonify({
            'error': 'Accès restreint: frais impayés',
            'has_unpaid': True
        }), 403
    
    moyennes = db.execute("""
        SELECT m.*, mat.libelle as matiere_libelle, mat.code as matiere_code
        FROM moyennes m
        JOIN matieres mat ON m.matiere_id = mat.id
        WHERE m.etudiant_id = ? AND m.periode = ?
        ORDER BY matiere_libelle
    """, (etudiant['id'], periode)).fetchall()
    
    # Calculer la moyenne générale
    if moyennes:
        moyenne_generale = sum(m['moyenne'] * m.get('coefficient', 1) for m in moyennes) / len(moyennes)
    else:
        moyenne_generale = 0
    
    return jsonify({
        'moyennes': [dict(m) for m in moyennes],
        'moyenne_generale': round(moyenne_generale, 2)
    }), 200

@etudiant_bp.route('/classement', methods=['GET'])
@jwt_required()
def get_my_classement():
    """Obtient le classement de l'étudiant"""
    current_user = get_current_user()
    periode = request.args.get('periode', 'annuel')
    db = get_db()
    
    etudiant = db.execute("SELECT id, classe_id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Accès refusé'}), 403
    
    classement = db.execute("""
        SELECT * FROM classements
        WHERE etudiant_id = ? AND periode = ?
    """, (etudiant['id'], periode)).fetchone()
    
    if not classement:
        return jsonify({'error': 'Classement non disponible'}), 404
    
    # Obtenir le nombre total d'étudiants dans la classe
    total_etudiants = db.execute("""
        SELECT COUNT(*) as count FROM etudiants
        WHERE classe_id = ? AND is_active = 1
    """, (etudiant['classe_id'],)).fetchone()['count']
    
    return jsonify({
        **dict(classement),
        'total_etudiants': total_etudiants
    }), 200

@etudiant_bp.route('/bulletin', methods=['GET'])
@jwt_required()
def get_bulletin():
    """Génère le bulletin scolaire en PDF"""
    current_user = get_current_user()
    periode = request.args.get('periode', 'annuel')
    db = get_db()
    
    etudiant = db.execute("""
        SELECT e.*, u.nom, u.prenom, c.libelle as classe_libelle
        FROM etudiants e
        JOIN users u ON e.user_id = u.id
        LEFT JOIN classes c ON e.classe_id = c.id
        WHERE e.user_id = ?
    """, (current_user['id'],)).fetchone()
    
    if not etudiant:
        return jsonify({'error': 'Étudiant non trouvé'}), 404
    
    has_unpaid = check_unpaid_fees(db, etudiant['id'])
    if has_unpaid:
        return jsonify({
            'error': 'Accès restreint: frais impayés',
            'has_unpaid': True
        }), 403
    
    # Obtenir les moyennes
    moyennes = db.execute("""
        SELECT m.*, mat.libelle as matiere, mat.coefficient
        FROM moyennes m
        JOIN matieres mat ON m.matiere_id = mat.id
        WHERE m.etudiant_id = ? AND m.periode = ?
    """, (etudiant['id'], periode)).fetchall()
    
    # Générer le PDF
    output_path = os.path.join(
        request.application.config['UPLOAD_FOLDER'],
        'pdf',
        f'bulletin_{etudiant["id"]}_{periode}.pdf'
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

@etudiant_bp.route('/absences', methods=['GET'])
@jwt_required()
def get_my_absences():
    """Obtient les absences de l'étudiant"""
    current_user = get_current_user()
    db = get_db()
    
    etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Accès refusé'}), 403
    
    absences = db.execute("""
        SELECT a.*, m.libelle as matiere_libelle, c.libelle as classe_libelle
        FROM absences a
        LEFT JOIN matieres m ON a.matiere_id = m.id
        JOIN classes c ON a.classe_id = c.id
        WHERE a.etudiant_id = ?
        ORDER BY a.date_absence DESC
    """, (etudiant['id'],)).fetchall()
    
    return jsonify([dict(absence) for absence in absences]), 200

@etudiant_bp.route('/emploi-temps', methods=['GET'])
@jwt_required()
def get_emploi_temps():
    """Obtient l'emploi du temps de l'étudiant"""
    current_user = get_current_user()
    db = get_db()
    
    etudiant = db.execute("SELECT classe_id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant or not etudiant['classe_id']:
        return jsonify({'error': 'Classe non assignée'}), 404
    
    emploi_temps = db.execute("""
        SELECT et.*, m.libelle as matiere_libelle, u.nom as enseignant_nom, u.prenom as enseignant_prenom
        FROM emplois_temps et
        JOIN matieres m ON et.matiere_id = m.id
        JOIN users u ON et.enseignant_id = u.id
        WHERE et.classe_id = ?
        ORDER BY 
            CASE et.jour_semaine
                WHEN 'lundi' THEN 1
                WHEN 'mardi' THEN 2
                WHEN 'mercredi' THEN 3
                WHEN 'jeudi' THEN 4
                WHEN 'vendredi' THEN 5
                WHEN 'samedi' THEN 6
            END,
            et.heure_debut
    """, (etudiant['classe_id'],)).fetchall()
    
    return jsonify([dict(et) for et in emploi_temps]), 200

@etudiant_bp.route('/situation-financiere', methods=['GET'])
@jwt_required()
def get_financial_situation():
    """Obtient la situation financière"""
    current_user = get_current_user()
    db = get_db()
    
    etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Accès refusé'}), 403
    
    # Utiliser la fonction du blueprint comptabilite
    from blueprints.comptabilite import get_financial_situation as get_fin_sit
    return get_fin_sit(etudiant['id'])

@etudiant_bp.route('/decisions-academiques', methods=['GET'])
@jwt_required()
def get_decisions():
    """Obtient les décisions académiques"""
    current_user = get_current_user()
    db = get_db()
    
    etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Accès refusé'}), 403
    
    decisions = db.execute("""
        SELECT * FROM decisions_academiques
        WHERE etudiant_id = ?
        ORDER BY created_at DESC
    """, (etudiant['id'],)).fetchall()
    
    return jsonify([dict(d) for d in decisions]), 200

@etudiant_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Obtient les notifications de l'étudiant"""
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

@etudiant_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    """Marque une notification comme lue"""
    current_user = get_current_user()
    db = get_db()
    
    db.execute("""
        UPDATE notifications SET is_lu = 1, date_lecture = ?
        WHERE id = ? AND user_id = ?
    """, (datetime.now(), notification_id, current_user['id']))
    db.commit()
    
    return jsonify({'message': 'Notification marquée comme lue'}), 200

def check_unpaid_fees(db, etudiant_id):
    """Vérifie si l'étudiant a des frais impayés"""
    # Obtenir les frais dus
    etudiant = db.execute("SELECT classe_id, annee_academique_id FROM etudiants WHERE id = ?", 
                         (etudiant_id,)).fetchone()
    if not etudiant:
        return False
    
    frais_dus = db.execute("""
        SELECT SUM(montant) as total FROM frais_classes
        WHERE classe_id = ? AND annee_academique_id = ?
    """, (etudiant['classe_id'], etudiant['annee_academique_id'])).fetchone()
    
    total_due = frais_dus['total'] or 0
    
    # Obtenir les paiements validés
    paiements = db.execute("""
        SELECT SUM(montant) as total FROM paiements
        WHERE etudiant_id = ? AND statut = 'valide'
    """, (etudiant_id,)).fetchone()
    
    total_paid = paiements['total'] or 0
    
    # Vérifier le délai de verrouillage
    parametre = db.execute("""
        SELECT valeur FROM parametres WHERE cle = 'delai_verrouillage_impaye'
    """).fetchone()
    
    delai_jours = int(parametre['valeur']) if parametre else 30
    
    # Si solde > 0 et délai dépassé, verrouiller
    if total_due > total_paid:
        # Vérifier la date du dernier paiement
        dernier_paiement = db.execute("""
            SELECT MAX(date_paiement) as date FROM paiements
            WHERE etudiant_id = ? AND statut = 'valide'
        """, (etudiant_id,)).fetchone()
        
        if not dernier_paiement['date']:
            return True  # Jamais payé
        
        # Vérifier si le délai est dépassé
        from datetime import datetime, timedelta
        date_dernier_paiement = datetime.strptime(dernier_paiement['date'], '%Y-%m-%d')
        if datetime.now() - date_dernier_paiement > timedelta(days=delai_jours):
            return True
    
    return False

