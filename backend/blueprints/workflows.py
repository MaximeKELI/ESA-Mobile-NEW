"""
Blueprint pour les workflows automatisés
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import role_required, get_current_user, log_action
from utils.validators import validate_required
from datetime import datetime, timedelta
import json

workflows_bp = Blueprint('workflows', __name__)

@workflows_bp.route('/workflows', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_workflows():
    """Liste tous les workflows"""
    db = get_db()
    workflows = db.execute("""
        SELECT w.*, u.nom as createur_nom, u.prenom as createur_prenom
        FROM workflows w
        JOIN users u ON w.created_by = u.id
        ORDER BY w.created_at DESC
    """).fetchall()
    return jsonify([dict(w) for w in workflows]), 200

@workflows_bp.route('/workflows', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_workflow():
    """Crée un nouveau workflow"""
    data = request.get_json()
    valid, error = validate_required(data, ['nom', 'type_workflow'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    current_user = get_current_user()
    
    cursor = db.execute("""
        INSERT INTO workflows (nom, description, type_workflow, is_actif, created_by)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data['nom'],
        data.get('description'),
        data['type_workflow'],
        data.get('is_actif', True),
        current_user['id']
    ))
    db.commit()
    workflow_id = cursor.lastrowid
    
    # Créer les étapes si fournies
    if 'etapes' in data:
        for idx, etape in enumerate(data['etapes']):
            db.execute("""
                INSERT INTO etapes_workflow (workflow_id, ordre, nom, type_etape, conditions,
                                          actions, approbateur_role, timeout_jours, is_obligatoire)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workflow_id,
                idx + 1,
                etape.get('nom', f'Étape {idx + 1}'),
                etape.get('type_etape', 'action'),
                json.dumps(etape.get('conditions', {})),
                json.dumps(etape.get('actions', {})),
                etape.get('approbateur_role'),
                etape.get('timeout_jours'),
                etape.get('is_obligatoire', True)
            ))
        db.commit()
    
    log_action(current_user['id'], 'creation_workflow', 'workflows', workflow_id)
    return jsonify({'message': 'Workflow créé avec succès', 'workflow_id': workflow_id}), 201

@workflows_bp.route('/workflows/<int:workflow_id>/etapes', methods=['GET'])
@jwt_required()
def get_etapes(workflow_id):
    """Obtient les étapes d'un workflow"""
    db = get_db()
    etapes = db.execute("""
        SELECT * FROM etapes_workflow
        WHERE workflow_id = ?
        ORDER BY ordre
    """, (workflow_id,)).fetchall()
    return jsonify([dict(e) for e in etapes]), 200

@workflows_bp.route('/workflows/<int:workflow_id>/declencher', methods=['POST'])
@jwt_required()
def declencher_workflow(workflow_id):
    """Déclenche une instance de workflow"""
    data = request.get_json()
    valid, error = validate_required(data, ['entite_type', 'entite_id'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    
    # Vérifier que le workflow existe et est actif
    workflow = db.execute("SELECT * FROM workflows WHERE id = ? AND is_actif = 1", 
                         (workflow_id,)).fetchone()
    if not workflow:
        return jsonify({'error': 'Workflow non trouvé ou inactif'}), 404
    
    # Obtenir la première étape
    premiere_etape = db.execute("""
        SELECT * FROM etapes_workflow
        WHERE workflow_id = ?
        ORDER BY ordre
        LIMIT 1
    """, (workflow_id,)).fetchone()
    
    if not premiere_etape:
        return jsonify({'error': 'Workflow sans étapes'}), 400
    
    # Créer l'instance
    cursor = db.execute("""
        INSERT INTO instances_workflow (workflow_id, entite_type, entite_id, etape_actuelle_id,
                                      statut, donnees_contexte)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        workflow_id,
        data['entite_type'],
        data['entite_id'],
        premiere_etape['id'],
        'en_cours',
        json.dumps(data.get('contexte', {}))
    ))
    db.commit()
    instance_id = cursor.lastrowid
    
    # Exécuter la première étape
    executer_etape(db, instance_id, premiere_etape['id'])
    
    return jsonify({'message': 'Workflow déclenché', 'instance_id': instance_id}), 201

@workflows_bp.route('/instances/<int:instance_id>/avancer', methods=['POST'])
@jwt_required()
def avancer_workflow(instance_id):
    """Fait avancer une instance de workflow"""
    data = request.get_json()
    db = get_db()
    current_user = get_current_user()
    
    instance = db.execute("SELECT * FROM instances_workflow WHERE id = ?", 
                         (instance_id,)).fetchone()
    if not instance:
        return jsonify({'error': 'Instance non trouvée'}), 404
    
    if instance['statut'] != 'en_cours':
        return jsonify({'error': 'Workflow terminé ou bloqué'}), 400
    
    etape_actuelle = db.execute("SELECT * FROM etapes_workflow WHERE id = ?", 
                               (instance['etape_actuelle_id'],)).fetchone()
    
    # Vérifier les conditions
    if etape_actuelle['type_etape'] == 'approbation':
        # Vérifier que l'utilisateur peut approuver
        if current_user['role'] != etape_actuelle['approbateur_role']:
            return jsonify({'error': 'Vous n\'avez pas l\'autorisation d\'approuver'}), 403
    
    # Exécuter les actions de l'étape
    actions = json.loads(etape_actuelle['actions']) if etape_actuelle['actions'] else {}
    executer_actions(db, instance, actions)
    
    # Enregistrer dans l'historique
    db.execute("""
        INSERT INTO historique_workflow (instance_id, etape_id, action_effectuee, acteur_id, resultat)
        VALUES (?, ?, ?, ?, ?)
    """, (
        instance_id,
        etape_actuelle['id'],
        'etape_completee',
        current_user['id'],
        json.dumps({'resultat': 'succes'})
    ))
    
    # Passer à l'étape suivante
    etape_suivante = db.execute("""
        SELECT * FROM etapes_workflow
        WHERE workflow_id = ? AND ordre > ?
        ORDER BY ordre
        LIMIT 1
    """, (instance['workflow_id'], etape_actuelle['ordre'])).fetchone()
    
    if etape_suivante:
        db.execute("""
            UPDATE instances_workflow
            SET etape_actuelle_id = ?
            WHERE id = ?
        """, (etape_suivante['id'], instance_id))
        
        # Exécuter la nouvelle étape
        executer_etape(db, instance_id, etape_suivante['id'])
    else:
        # Workflow terminé
        db.execute("""
            UPDATE instances_workflow
            SET statut = 'termine', date_fin = ?
            WHERE id = ?
        """, (datetime.now(), instance_id))
    
    db.commit()
    
    return jsonify({'message': 'Workflow avancé'}), 200

@workflows_bp.route('/instances', methods=['GET'])
@jwt_required()
def list_instances():
    """Liste les instances de workflow"""
    workflow_id = request.args.get('workflow_id')
    statut = request.args.get('statut')
    db = get_db()
    
    query = """
        SELECT i.*, w.nom as workflow_nom
        FROM instances_workflow i
        JOIN workflows w ON i.workflow_id = w.id
        WHERE 1=1
    """
    params = []
    
    if workflow_id:
        query += " AND i.workflow_id = ?"
        params.append(workflow_id)
    
    if statut:
        query += " AND i.statut = ?"
        params.append(statut)
    
    query += " ORDER BY i.date_debut DESC"
    
    instances = db.execute(query, params).fetchall()
    return jsonify([dict(i) for i in instances]), 200

def executer_etape(db, instance_id, etape_id):
    """Exécute une étape de workflow"""
    etape = db.execute("SELECT * FROM etapes_workflow WHERE id = ?", (etape_id,)).fetchone()
    
    if etape['type_etape'] == 'notification':
        # Envoyer une notification
        actions = json.loads(etape['actions']) if etape['actions'] else {}
        if 'notification' in actions:
            from utils.notifications_service import send_notification
            send_notification(
                actions['notification'].get('user_id'),
                actions['notification'].get('type', 'workflow'),
                actions['notification'].get('titre', 'Notification workflow'),
                actions['notification'].get('message', '')
            )

def executer_actions(db, instance, actions):
    """Exécute les actions d'une étape"""
    if 'creer_paiement' in actions:
        # Créer un paiement automatique
        pass
    
    if 'envoyer_email' in actions:
        # Envoyer un email
        pass
    
    if 'debloquer_acces' in actions:
        # Débloquer l'accès à certaines fonctionnalités
        pass

