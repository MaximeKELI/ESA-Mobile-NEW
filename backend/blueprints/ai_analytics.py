"""
Blueprint pour l'Intelligence Artificielle et Analytics
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import role_required, get_current_user
from datetime import datetime, timedelta
import json

ai_analytics_bp = Blueprint('ai_analytics', __name__)

@ai_analytics_bp.route('/prediction/reussite', methods=['GET'])
@jwt_required()
@role_required('admin', 'enseignant')
def predict_student_success():
    """Prédit la réussite d'un étudiant (version simplifiée)"""
    etudiant_id = request.args.get('etudiant_id')
    db = get_db()
    
    if not etudiant_id:
        return jsonify({'error': 'etudiant_id requis'}), 400
    
    # Récupérer les données de l'étudiant
    etudiant = db.execute("""
        SELECT e.*, u.nom, u.prenom FROM etudiants e
        JOIN users u ON e.user_id = u.id
        WHERE e.id = ?
    """, (etudiant_id,)).fetchone()
    
    if not etudiant:
        return jsonify({'error': 'Étudiant non trouvé'}), 404
    
    # Calculer le score de risque (algorithme simplifié)
    # En production, utiliser un modèle ML entraîné
    
    # Facteurs de risque
    facteurs = {
        'moyenne_basse': 0,
        'absences_elevees': 0,
        'paiements_en_retard': 0,
        'notes_descendantes': 0
    }
    
    # Moyenne actuelle
    moyenne = db.execute("""
        SELECT AVG(moyenne) as moyenne FROM moyennes
        WHERE etudiant_id = ? AND periode = 'annuel'
    """, (etudiant_id,)).fetchone()
    
    moyenne_actuelle = moyenne['moyenne'] if moyenne['moyenne'] else 0
    
    if moyenne_actuelle < 10:
        facteurs['moyenne_basse'] = 3
    elif moyenne_actuelle < 12:
        facteurs['moyenne_basse'] = 1
    
    # Absences
    absences = db.execute("""
        SELECT COUNT(*) as count FROM absences
        WHERE etudiant_id = ? AND date_absence >= date('now', '-30 days')
    """, (etudiant_id,)).fetchone()['count']
    
    if absences > 5:
        facteurs['absences_elevees'] = 2
    elif absences > 3:
        facteurs['absences_elevees'] = 1
    
    # Paiements en retard
    solde = db.execute("""
        SELECT 
            (SELECT COALESCE(SUM(fc.montant), 0) FROM frais_classes fc
             JOIN etudiants e2 ON fc.classe_id = e2.classe_id
             WHERE e2.id = ?) -
            (SELECT COALESCE(SUM(p.montant), 0) FROM paiements p
             WHERE p.etudiant_id = ? AND p.statut = 'valide') as solde
    """, (etudiant_id, etudiant_id)).fetchone()
    
    if solde and solde['solde'] > 0:
        facteurs['paiements_en_retard'] = 2
    
    # Tendance des notes
    notes_recentes = db.execute("""
        SELECT note FROM notes
        WHERE etudiant_id = ? AND is_valide = 1
        ORDER BY date_note DESC LIMIT 5
    """, (etudiant_id,)).fetchall()
    
    if len(notes_recentes) >= 3:
        recent_avg = sum(n['note'] for n in notes_recentes[:3]) / 3
        older_avg = sum(n['note'] for n in notes_recentes[3:]) / 2 if len(notes_recentes) >= 5 else recent_avg
        
        if recent_avg < older_avg - 2:
            facteurs['notes_descendantes'] = 2
    
    # Score de risque total (0-10)
    score_risque = sum(facteurs.values())
    probabilite_reussite = max(0, min(100, 100 - (score_risque * 10)))
    
    # Recommandations
    recommandations = []
    if facteurs['moyenne_basse'] > 0:
        recommandations.append("Soutien scolaire recommandé")
    if facteurs['absences_elevees'] > 0:
        recommandations.append("Suivi des absences nécessaire")
    if facteurs['paiements_en_retard'] > 0:
        recommandations.append("Régularisation de la situation financière")
    if facteurs['notes_descendantes'] > 0:
        recommandations.append("Entretien avec l'étudiant recommandé")
    
    return jsonify({
        'etudiant_id': etudiant_id,
        'etudiant_nom': f"{etudiant['nom']} {etudiant['prenom']}",
        'moyenne_actuelle': round(moyenne_actuelle, 2),
        'score_risque': score_risque,
        'probabilite_reussite': round(probabilite_reussite, 1),
        'facteurs_risque': facteurs,
        'recommandations': recommandations,
        'niveau_alerte': 'eleve' if score_risque >= 6 else 'moyen' if score_risque >= 3 else 'faible'
    }), 200

@ai_analytics_bp.route('/analytics/dashboard', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_analytics_dashboard():
    """Tableau de bord analytics avancé"""
    db = get_db()
    
    # Statistiques générales
    total_etudiants = db.execute("SELECT COUNT(*) as count FROM etudiants WHERE is_active = 1").fetchone()['count']
    total_enseignants = db.execute("SELECT COUNT(*) as count FROM enseignants WHERE is_active = 1").fetchone()['count']
    
    # Taux de réussite
    reussite = db.execute("""
        SELECT COUNT(*) as count FROM moyennes 
        WHERE moyenne >= 10 AND periode = 'annuel'
    """).fetchone()['count']
    total_moyennes = db.execute("SELECT COUNT(*) as count FROM moyennes WHERE periode = 'annuel'").fetchone()['count']
    taux_reussite = (reussite / total_moyennes * 100) if total_moyennes > 0 else 0
    
    # Évolution des inscriptions
    inscriptions_mois = []
    for i in range(6):
        date_debut = (datetime.now() - timedelta(days=30*(i+1))).strftime('%Y-%m-%d')
        date_fin = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m-%d')
        count = db.execute("""
            SELECT COUNT(*) as count FROM etudiants
            WHERE date_inscription BETWEEN ? AND ?
        """, (date_debut, date_fin)).fetchone()['count']
        inscriptions_mois.append({
            'mois': date_fin[:7],
            'nombre': count
        })
    
    # Répartition par filière
    repartition_filieres = db.execute("""
        SELECT f.libelle, COUNT(e.id) as nombre
        FROM filieres f
        LEFT JOIN classes c ON f.id = c.filiere_id
        LEFT JOIN etudiants e ON c.id = e.classe_id AND e.is_active = 1
        GROUP BY f.id, f.libelle
    """).fetchall()
    
    # Top 10 étudiants
    top_etudiants = db.execute("""
        SELECT e.id, u.nom, u.prenom, AVG(m.moyenne) as moyenne_generale
        FROM etudiants e
        JOIN users u ON e.user_id = u.id
        JOIN moyennes m ON e.id = m.etudiant_id
        WHERE m.periode = 'annuel' AND e.is_active = 1
        GROUP BY e.id, u.nom, u.prenom
        ORDER BY moyenne_generale DESC
        LIMIT 10
    """).fetchall()
    
    # Revenus par mois
    revenus_mois = []
    for i in range(6):
        date_debut = (datetime.now() - timedelta(days=30*(i+1))).strftime('%Y-%m-%d')
        date_fin = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m-%d')
        total = db.execute("""
            SELECT COALESCE(SUM(montant), 0) as total FROM paiements
            WHERE statut = 'valide' AND date_paiement BETWEEN ? AND ?
        """, (date_debut, date_fin)).fetchone()['total']
        revenus_mois.append({
            'mois': date_fin[:7],
            'montant': total
        })
    
    return jsonify({
        'statistiques_generales': {
            'total_etudiants': total_etudiants,
            'total_enseignants': total_enseignants,
            'taux_reussite': round(taux_reussite, 2)
        },
        'evolution_inscriptions': inscriptions_mois,
        'repartition_filieres': [dict(r) for r in repartition_filieres],
        'top_etudiants': [dict(t) for t in top_etudiants],
        'revenus_mois': revenus_mois
    }), 200

@ai_analytics_bp.route('/prediction/inscriptions', methods=['GET'])
@jwt_required()
@role_required('admin')
def predict_enrollments():
    """Prédit les inscriptions futures (simplifié)"""
    db = get_db()
    
    # Analyser les tendances historiques
    inscriptions_annees = db.execute("""
        SELECT strftime('%Y', date_inscription) as annee, COUNT(*) as nombre
        FROM etudiants
        GROUP BY strftime('%Y', date_inscription)
        ORDER BY annee DESC
        LIMIT 5
    """).fetchall()
    
    if len(inscriptions_annees) < 2:
        return jsonify({'error': 'Données insuffisantes pour prédiction'}), 400
    
    # Calcul simple de tendance (en production, utiliser ML)
    nombres = [i['nombre'] for i in inscriptions_annees]
    moyenne = sum(nombres) / len(nombres)
    
    # Prédiction pour l'année prochaine (moyenne + croissance estimée)
    croissance = (nombres[0] - nombres[-1]) / len(nombres) if len(nombres) > 1 else 0
    prediction = int(moyenne + croissance)
    
    return jsonify({
        'historique': [dict(i) for i in inscriptions_annees],
        'prediction_annee_prochaine': prediction,
        'tendance': 'croissance' if croissance > 0 else 'baisse' if croissance < 0 else 'stable',
        'confiance': 'moyenne'  # En production, calculer avec modèle ML
    }), 200

@ai_analytics_bp.route('/recommandations/parcours', methods=['GET'])
@jwt_required()
def recommend_pathway():
    """Recommandations de parcours académique"""
    etudiant_id = request.args.get('etudiant_id')
    db = get_db()
    current_user = get_current_user()
    
    # Vérifier les droits
    if current_user['role'] == 'etudiant':
        etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                             (current_user['id'],)).fetchone()
        if not etudiant or etudiant['id'] != int(etudiant_id):
            return jsonify({'error': 'Accès refusé'}), 403
    
    # Analyser les notes de l'étudiant
    notes_par_matiere = db.execute("""
        SELECT m.id, m.libelle, AVG(n.note) as moyenne
        FROM notes n
        JOIN matieres m ON n.matiere_id = m.id
        WHERE n.etudiant_id = ? AND n.is_valide = 1
        GROUP BY m.id, m.libelle
        ORDER BY moyenne DESC
    """, (etudiant_id,)).fetchall()
    
    if not notes_par_matiere:
        return jsonify({'error': 'Pas assez de données'}), 400
    
    # Identifier les matières fortes
    matieres_fortes = [m for m in notes_par_matiere if m['moyenne'] >= 14]
    
    # Recommander des filières basées sur les matières fortes
    recommandations = []
    
    # Logique simplifiée (en production, utiliser ML)
    if any('math' in m['libelle'].lower() or 'informatique' in m['libelle'].lower() 
           for m in matieres_fortes):
        recommandations.append({
            'filiere': 'Informatique',
            'score': 0.8,
            'raison': 'Forces en mathématiques/informatique'
        })
    
    if any('commerce' in m['libelle'].lower() or 'gestion' in m['libelle'].lower() 
           for m in matieres_fortes):
        recommandations.append({
            'filiere': 'Gestion',
            'score': 0.8,
            'raison': 'Forces en commerce/gestion'
        })
    
    return jsonify({
        'etudiant_id': etudiant_id,
        'matieres_fortes': [dict(m) for m in matieres_fortes],
        'recommandations': recommandations
    }), 200

