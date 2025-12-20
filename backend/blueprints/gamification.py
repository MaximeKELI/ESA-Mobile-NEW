"""
Blueprint pour la Gamification
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import get_current_user
from datetime import datetime

gamification_bp = Blueprint('gamification', __name__)

@gamification_bp.route('/points', methods=['GET'])
@jwt_required()
def get_user_points():
    """Obtient les points de l'utilisateur"""
    current_user = get_current_user()
    db = get_db()
    
    # Calculer les points (simplifié)
    points = 0
    badges = []
    
    if current_user['role'] == 'etudiant':
        etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                             (current_user['id'],)).fetchone()
        if etudiant:
            # Points pour les bonnes notes
            bonnes_notes = db.execute("""
                SELECT COUNT(*) as count FROM notes
                WHERE etudiant_id = ? AND note >= 15 AND is_valide = 1
            """, (etudiant['id'],)).fetchone()['count']
            points += bonnes_notes * 10
            
            # Points pour l'assiduité
            absences = db.execute("""
                SELECT COUNT(*) as count FROM absences
                WHERE etudiant_id = ? AND date_absence >= date('now', '-30 days')
            """, (etudiant['id'],)).fetchone()['count']
            if absences == 0:
                points += 50
                badges.append('assidu')
            
            # Points pour les paiements à jour
            solde = db.execute("""
                SELECT 
                    (SELECT COALESCE(SUM(fc.montant), 0) FROM frais_classes fc
                     JOIN etudiants e2 ON fc.classe_id = e2.classe_id
                     WHERE e2.id = ?) -
                    (SELECT COALESCE(SUM(p.montant), 0) FROM paiements p
                     WHERE p.etudiant_id = ? AND p.statut = 'valide') as solde
            """, (etudiant['id'], etudiant['id'])).fetchone()
            
            if solde and solde['solde'] <= 0:
                points += 30
                badges.append('financier_exemplaire')
            
            # Badge excellent élève
            moyenne = db.execute("""
                SELECT AVG(moyenne) as moyenne FROM moyennes
                WHERE etudiant_id = ? AND periode = 'annuel'
            """, (etudiant['id'],)).fetchone()
            
            if moyenne and moyenne['moyenne'] >= 16:
                badges.append('excellent_eleve')
            elif moyenne and moyenne['moyenne'] >= 14:
                badges.append('bon_eleve')
    
    return jsonify({
        'points': points,
        'badges': badges,
        'niveau': calculate_level(points)
    }), 200

@gamification_bp.route('/classement', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """Obtient le classement des étudiants"""
    type_classement = request.args.get('type', 'points')  # points, notes, assiduite
    db = get_db()
    
    if type_classement == 'points':
        # Classement par points (simplifié)
        etudiants = db.execute("""
            SELECT e.id, u.nom, u.prenom, 
                   (SELECT COUNT(*) * 10 FROM notes n 
                    WHERE n.etudiant_id = e.id AND n.note >= 15 AND n.is_valide = 1) as points
            FROM etudiants e
            JOIN users u ON e.user_id = u.id
            WHERE e.is_active = 1
            ORDER BY points DESC
            LIMIT 20
        """).fetchall()
    elif type_classement == 'notes':
        etudiants = db.execute("""
            SELECT e.id, u.nom, u.prenom, AVG(m.moyenne) as moyenne
            FROM etudiants e
            JOIN users u ON e.user_id = u.id
            JOIN moyennes m ON e.id = m.etudiant_id
            WHERE m.periode = 'annuel' AND e.is_active = 1
            GROUP BY e.id, u.nom, u.prenom
            ORDER BY moyenne DESC
            LIMIT 20
        """).fetchall()
    else:  # assiduite
        etudiants = db.execute("""
            SELECT e.id, u.nom, u.prenom,
                   (SELECT COUNT(*) FROM absences a 
                    WHERE a.etudiant_id = e.id AND a.date_absence >= date('now', '-30 days')) as absences
            FROM etudiants e
            JOIN users u ON e.user_id = u.id
            WHERE e.is_active = 1
            ORDER BY absences ASC
            LIMIT 20
        """).fetchall()
    
    return jsonify({
        'type': type_classement,
        'classement': [dict(e) for e in etudiants]
    }), 200

@gamification_bp.route('/defis', methods=['GET'])
@jwt_required()
def get_challenges():
    """Obtient les défis disponibles"""
    current_user = get_current_user()
    db = get_db()
    
    defis = []
    
    if current_user['role'] == 'etudiant':
        etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                             (current_user['id'],)).fetchone()
        if etudiant:
            # Défi : 5 bonnes notes ce mois
            bonnes_notes_mois = db.execute("""
                SELECT COUNT(*) as count FROM notes
                WHERE etudiant_id = ? AND note >= 15 AND is_valide = 1
                AND date_note >= date('now', 'start of month')
            """, (etudiant['id'],)).fetchone()['count']
            
            defis.append({
                'id': 'bonnes_notes_mois',
                'titre': '5 bonnes notes ce mois',
                'description': 'Obtenez 5 notes >= 15 ce mois',
                'progression': f"{bonnes_notes_mois}/5",
                'recompense': '50 points',
                'termine': bonnes_notes_mois >= 5
            })
            
            # Défi : Assiduité parfaite
            absences_mois = db.execute("""
                SELECT COUNT(*) as count FROM absences
                WHERE etudiant_id = ? AND date_absence >= date('now', 'start of month')
            """, (etudiant['id'],)).fetchone()['count']
            
            defis.append({
                'id': 'assiduite_parfaite',
                'titre': 'Assiduité parfaite',
                'description': 'Aucune absence ce mois',
                'progression': f"{30 - absences_mois}/30 jours",
                'recompense': 'Badge Assidu',
                'termine': absences_mois == 0
            })
    
    return jsonify({'defis': defis}), 200

def calculate_level(points):
    """Calcule le niveau selon les points"""
    if points < 100:
        return {'niveau': 1, 'nom': 'Débutant', 'points_restants': 100 - points}
    elif points < 300:
        return {'niveau': 2, 'nom': 'Intermédiaire', 'points_restants': 300 - points}
    elif points < 600:
        return {'niveau': 3, 'nom': 'Avancé', 'points_restants': 600 - points}
    elif points < 1000:
        return {'niveau': 4, 'nom': 'Expert', 'points_restants': 1000 - points}
    else:
        return {'niveau': 5, 'nom': 'Maître', 'points_restants': 0}


