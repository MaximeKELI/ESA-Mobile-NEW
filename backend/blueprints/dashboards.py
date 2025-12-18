"""
Blueprint pour les tableaux de bord personnalisables
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import get_current_user
from utils.validators import validate_required
import json

dashboards_bp = Blueprint('dashboards', __name__)

@dashboards_bp.route('/widgets', methods=['GET'])
@jwt_required()
def list_widgets():
    """Liste les widgets disponibles"""
    db = get_db()
    widgets = db.execute("""
        SELECT * FROM widgets
        WHERE is_systeme = 1 OR id IN (
            SELECT DISTINCT widget_id FROM widgets_tableaux_bord
            JOIN tableaux_bord ON widgets_tableaux_bord.tableau_bord_id = tableaux_bord.id
            WHERE tableaux_bord.user_id = ?
        )
        ORDER BY nom
    """, (get_current_user()['id'],)).fetchall()
    
    return jsonify([dict(w) for w in widgets]), 200

@dashboards_bp.route('/widgets', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_widget():
    """Crée un widget personnalisé"""
    data = request.get_json()
    valid, error = validate_required(data, ['code', 'nom', 'type_widget'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO widgets (code, nom, type_widget, description, configuration_defaut, is_systeme)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data['code'],
        data['nom'],
        data['type_widget'],
        data.get('description'),
        json.dumps(data.get('configuration_defaut', {})),
        data.get('is_systeme', False)
    ))
    db.commit()
    
    return jsonify({'message': 'Widget créé', 'widget_id': cursor.lastrowid}), 201

@dashboards_bp.route('/tableaux-bord', methods=['GET'])
@jwt_required()
def list_tableaux_bord():
    """Liste les tableaux de bord de l'utilisateur"""
    current_user = get_current_user()
    db = get_db()
    
    tableaux = db.execute("""
        SELECT * FROM tableaux_bord
        WHERE user_id = ?
        ORDER BY is_par_defaut DESC, updated_at DESC
    """, (current_user['id'],)).fetchall()
    
    return jsonify([dict(t) for t in tableaux]), 200

@dashboards_bp.route('/tableaux-bord', methods=['POST'])
@jwt_required()
def create_tableau_bord():
    """Crée un tableau de bord personnalisé"""
    data = request.get_json()
    valid, error = validate_required(data, ['nom'])
    if not valid:
        return jsonify({'error': error}), 400
    
    current_user = get_current_user()
    db = get_db()
    
    # Si c'est le tableau par défaut, désactiver les autres
    if data.get('is_par_defaut'):
        db.execute("""
            UPDATE tableaux_bord
            SET is_par_defaut = 0
            WHERE user_id = ?
        """, (current_user['id'],))
    
    cursor = db.execute("""
        INSERT INTO tableaux_bord (user_id, nom, is_par_defaut, layout)
        VALUES (?, ?, ?, ?)
    """, (
        current_user['id'],
        data['nom'],
        data.get('is_par_defaut', False),
        json.dumps(data.get('layout', {}))
    ))
    db.commit()
    tableau_id = cursor.lastrowid
    
    # Ajouter les widgets si fournis
    if 'widgets' in data:
        for idx, widget_data in enumerate(data['widgets']):
            db.execute("""
                INSERT INTO widgets_tableaux_bord (tableau_bord_id, widget_id, position_x, position_y,
                                                  largeur, hauteur, configuration, ordre)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                tableau_id,
                widget_data['widget_id'],
                widget_data.get('position_x', 0),
                widget_data.get('position_y', 0),
                widget_data.get('largeur', 1),
                widget_data.get('hauteur', 1),
                json.dumps(widget_data.get('configuration', {})),
                idx
            ))
        db.commit()
    
    return jsonify({'message': 'Tableau de bord créé', 'tableau_id': tableau_id}), 201

@dashboards_bp.route('/tableaux-bord/<int:tableau_id>', methods=['GET'])
@jwt_required()
def get_tableau_bord(tableau_id):
    """Obtient un tableau de bord avec ses widgets"""
    current_user = get_current_user()
    db = get_db()
    
    tableau = db.execute("""
        SELECT * FROM tableaux_bord
        WHERE id = ? AND user_id = ?
    """, (tableau_id, current_user['id'])).fetchone()
    
    if not tableau:
        return jsonify({'error': 'Tableau de bord non trouvé'}), 404
    
    widgets = db.execute("""
        SELECT wtb.*, w.code, w.nom, w.type_widget, w.configuration_defaut
        FROM widgets_tableaux_bord wtb
        JOIN widgets w ON wtb.widget_id = w.id
        WHERE wtb.tableau_bord_id = ?
        ORDER BY wtb.ordre
    """, (tableau_id,)).fetchall()
    
    return jsonify({
        **dict(tableau),
        'widgets': [dict(w) for w in widgets]
    }), 200

@dashboards_bp.route('/tableaux-bord/<int:tableau_id>/widgets', methods=['POST'])
@jwt_required()
def add_widget_to_tableau(tableau_id):
    """Ajoute un widget à un tableau de bord"""
    data = request.get_json()
    valid, error = validate_required(data, ['widget_id'])
    if not valid:
        return jsonify({'error': error}), 400
    
    current_user = get_current_user()
    db = get_db()
    
    # Vérifier que le tableau appartient à l'utilisateur
    tableau = db.execute("""
        SELECT id FROM tableaux_bord
        WHERE id = ? AND user_id = ?
    """, (tableau_id, current_user['id'])).fetchone()
    
    if not tableau:
        return jsonify({'error': 'Tableau de bord non trouvé'}), 404
    
    cursor = db.execute("""
        INSERT INTO widgets_tableaux_bord (tableau_bord_id, widget_id, position_x, position_y,
                                          largeur, hauteur, configuration, ordre)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        tableau_id,
        data['widget_id'],
        data.get('position_x', 0),
        data.get('position_y', 0),
        data.get('largeur', 1),
        data.get('hauteur', 1),
        json.dumps(data.get('configuration', {})),
        data.get('ordre', 0)
    ))
    db.commit()
    
    return jsonify({'message': 'Widget ajouté', 'widget_tableau_id': cursor.lastrowid}), 201

@dashboards_bp.route('/widgets/<int:widget_id>/data', methods=['GET'])
@jwt_required()
def get_widget_data(widget_id):
    """Obtient les données d'un widget"""
    configuration = request.args.get('configuration', '{}')
    config = json.loads(configuration)
    db = get_db()
    
    widget = db.execute("SELECT * FROM widgets WHERE id = ?", (widget_id,)).fetchone()
    if not widget:
        return jsonify({'error': 'Widget non trouvé'}), 404
    
    # Générer les données selon le type de widget
    data = generer_donnees_widget(db, widget, config)
    
    return jsonify(data), 200

def generer_donnees_widget(db, widget, config):
    """Génère les données pour un widget"""
    widget_code = widget['code']
    
    if widget_code == 'stats_etudiants':
        total = db.execute("SELECT COUNT(*) as count FROM etudiants WHERE is_active = 1").fetchone()['count']
        return {'valeur': total, 'label': 'Total étudiants'}
    
    elif widget_code == 'stats_paiements':
        mois = config.get('mois', datetime.now().strftime('%Y-%m'))
        total = db.execute("""
            SELECT COALESCE(SUM(montant), 0) as total FROM paiements
            WHERE statut = 'valide' AND strftime('%Y-%m', date_paiement) = ?
        """, (mois,)).fetchone()['total']
        return {'valeur': total, 'label': f'Paiements {mois}'}
    
    elif widget_code == 'graphique_notes':
        # Graphique des notes par matière
        notes = db.execute("""
            SELECT m.libelle, AVG(n.note) as moyenne
            FROM notes n
            JOIN matieres m ON n.matiere_id = m.id
            WHERE n.is_valide = 1
            GROUP BY m.id, m.libelle
            LIMIT 10
        """).fetchall()
        return {'donnees': [dict(n) for n in notes]}
    
    elif widget_code == 'calendrier_events':
        # Événements à venir
        events = db.execute("""
            SELECT * FROM evenements
            WHERE date_debut >= date('now')
            ORDER BY date_debut
            LIMIT 10
        """).fetchall()
        return {'evenements': [dict(e) for e in events]}
    
    return {'donnees': []}

