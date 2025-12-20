"""
Blueprint pour les fonctionnalités d'administration
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import role_required, get_current_user, log_action
from utils.validators import validate_required, validate_email_format, validate_phone, validate_date, validate_montant
from utils.qr_code import generate_student_qr
from utils.pdf_generator import generate_receipt, generate_bulletin
from datetime import datetime
import os

admin_bp = Blueprint('admin', __name__)

# ========== GESTION DES UTILISATEURS ==========

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_users():
    """Liste tous les utilisateurs"""
    role_filter = request.args.get('role')
    db = get_db()
    
    if role_filter:
        users = db.execute(
            "SELECT id, username, email, role, nom, prenom, telephone, is_active, created_at FROM users WHERE role = ?",
            (role_filter,)
        ).fetchall()
    else:
        users = db.execute(
            "SELECT id, username, email, role, nom, prenom, telephone, is_active, created_at FROM users"
        ).fetchall()
    
    return jsonify([dict(user) for user in users]), 200

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_user(user_id):
    """Obtient les détails d'un utilisateur"""
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    return jsonify(dict(user)), 200

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_user():
    """Crée un nouvel utilisateur"""
    data = request.get_json()
    
    required_fields = ['username', 'email', 'password', 'role', 'nom', 'prenom']
    valid, error = validate_required(data, required_fields)
    if not valid:
        return jsonify({'error': error}), 400
    
    # Validation email
    email_valid, email_error = validate_email_format(data['email'])
    if not email_valid:
        return jsonify({'error': email_error}), 400
    
    # Validation téléphone si fourni
    if 'telephone' in data and data['telephone']:
        phone_valid, phone_error = validate_phone(data['telephone'])
        if not phone_valid:
            return jsonify({'error': phone_error}), 400
    
    db = get_db()
    
    # Vérifier si l'username ou l'email existe déjà
    existing = db.execute(
        "SELECT id FROM users WHERE username = ? OR email = ?",
        (data['username'], data['email'])
    ).fetchone()
    
    if existing:
        return jsonify({'error': 'Username ou email déjà utilisé'}), 400
    
    from utils.auth import hash_password
    password_hash = hash_password(data['password'])
    
    # Créer l'utilisateur
    cursor = db.execute("""
        INSERT INTO users (username, email, password_hash, role, nom, prenom, telephone, adresse, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data['username'],
        data['email'],
        password_hash,
        data['role'],
        data['nom'],
        data['prenom'],
        data.get('telephone'),
        data.get('adresse'),
        data.get('is_active', True)
    ))
    db.commit()
    
    user_id = cursor.lastrowid
    
    # Créer le profil spécifique selon le rôle
    if data['role'] == 'etudiant':
        numero_etudiant = data.get('numero_etudiant', f"ESA{user_id:06d}")
        db.execute("""
            INSERT INTO etudiants (user_id, numero_etudiant, date_naissance, sexe, classe_id, annee_academique_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            numero_etudiant,
            data.get('date_naissance'),
            data.get('sexe'),
            data.get('classe_id'),
            data.get('annee_academique_id', 1)  # Par défaut première année académique
        ))
        
        # Générer le QR code
        qr_path = generate_student_qr(user_id, numero_etudiant, 
                                      os.path.join(request.application.config['UPLOAD_FOLDER'], 'qr_codes'))
        db.execute("UPDATE etudiants SET qr_code_path = ? WHERE user_id = ?", (qr_path, user_id))
        
    elif data['role'] == 'enseignant':
        matricule = data.get('matricule', f"ENS{user_id:04d}")
        db.execute("""
            INSERT INTO enseignants (user_id, matricule, specialite, date_embauche)
            VALUES (?, ?, ?, ?)
        """, (
            user_id,
            matricule,
            data.get('specialite'),
            data.get('date_embauche')
        ))
    
    elif data['role'] == 'parent':
        db.execute("""
            INSERT INTO parents (user_id, profession, lien_parente)
            VALUES (?, ?, ?)
        """, (
            user_id,
            data.get('profession'),
            data.get('lien_parente', 'tuteur')
        ))
    
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_utilisateur', 'users', user_id, None, data)
    
    return jsonify({'message': 'Utilisateur créé avec succès', 'user_id': user_id}), 201

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_user(user_id):
    """Met à jour un utilisateur"""
    data = request.get_json()
    db = get_db()
    
    # Récupérer les anciennes valeurs
    old_user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not old_user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    # Mettre à jour les champs fournis
    updates = []
    values = []
    
    if 'email' in data:
        email_valid, email_error = validate_email_format(data['email'])
        if not email_valid:
            return jsonify({'error': email_error}), 400
        updates.append("email = ?")
        values.append(data['email'])
    
    if 'nom' in data:
        updates.append("nom = ?")
        values.append(data['nom'])
    
    if 'prenom' in data:
        updates.append("prenom = ?")
        values.append(data['prenom'])
    
    if 'telephone' in data:
        phone_valid, phone_error = validate_phone(data['telephone'])
        if not phone_valid:
            return jsonify({'error': phone_error}), 400
        updates.append("telephone = ?")
        values.append(data['telephone'])
    
    if 'adresse' in data:
        updates.append("adresse = ?")
        values.append(data['adresse'])
    
    if 'is_active' in data:
        updates.append("is_active = ?")
        values.append(data['is_active'])
    
    if updates:
        updates.append("updated_at = ?")
        values.append(datetime.now())
        values.append(user_id)
        
        db.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", values)
        db.commit()
        
        log_action(get_current_user()['id'], 'modification_utilisateur', 'users', user_id, 
                  dict(old_user), data)
    
    return jsonify({'message': 'Utilisateur mis à jour avec succès'}), 200

@admin_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@jwt_required()
@role_required('admin')
def toggle_user_status(user_id):
    """Active ou désactive un utilisateur"""
    db = get_db()
    user = db.execute("SELECT is_active FROM users WHERE id = ?", (user_id,)).fetchone()
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    new_status = not bool(user['is_active'])
    db.execute("UPDATE users SET is_active = ?, updated_at = ? WHERE id = ?",
               (new_status, datetime.now(), user_id))
    db.commit()
    
    action = 'activation_utilisateur' if new_status else 'desactivation_utilisateur'
    log_action(get_current_user()['id'], action, 'users', user_id)
    
    return jsonify({'message': f'Utilisateur {"activé" if new_status else "désactivé"} avec succès'}), 200

# ========== GESTION DES ANNÉES ACADÉMIQUES ==========

@admin_bp.route('/annees-academiques', methods=['GET'])
@jwt_required()
@role_required('admin')
def list_annees():
    """Liste les années académiques"""
    db = get_db()
    annees = db.execute("SELECT * FROM annees_academiques ORDER BY date_debut DESC").fetchall()
    return jsonify([dict(annee) for annee in annees]), 200

@admin_bp.route('/annees-academiques', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_annee():
    """Crée une année académique"""
    data = request.get_json()
    valid, error = validate_required(data, ['code', 'libelle', 'date_debut', 'date_fin'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO annees_academiques (code, libelle, date_debut, date_fin, is_active)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data['code'],
        data['libelle'],
        data['date_debut'],
        data['date_fin'],
        data.get('is_active', False)
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_annee_academique', 'annees_academiques', cursor.lastrowid)
    return jsonify({'message': 'Année académique créée avec succès'}), 201

# ========== GESTION DES FILIÈRES ==========

@admin_bp.route('/filieres', methods=['GET'])
@jwt_required()
def list_filieres():
    """Liste les filières"""
    db = get_db()
    filieres = db.execute("SELECT * FROM filieres WHERE is_active = 1").fetchall()
    return jsonify([dict(filiere) for filiere in filieres]), 200

@admin_bp.route('/filieres', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_filiere():
    """Crée une filière"""
    data = request.get_json()
    valid, error = validate_required(data, ['code', 'libelle'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO filieres (code, libelle, description, is_active)
        VALUES (?, ?, ?, ?)
    """, (
        data['code'],
        data['libelle'],
        data.get('description'),
        data.get('is_active', True)
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_filiere', 'filieres', cursor.lastrowid)
    return jsonify({'message': 'Filière créée avec succès'}), 201

# ========== GESTION DES NIVEAUX ==========

@admin_bp.route('/niveaux', methods=['GET'])
@jwt_required()
def list_niveaux():
    """Liste les niveaux"""
    db = get_db()
    niveaux = db.execute("SELECT * FROM niveaux WHERE is_active = 1 ORDER BY ordre").fetchall()
    return jsonify([dict(niveau) for niveau in niveaux]), 200

@admin_bp.route('/niveaux', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_niveau():
    """Crée un niveau"""
    data = request.get_json()
    valid, error = validate_required(data, ['code', 'libelle', 'ordre'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO niveaux (code, libelle, ordre, is_active)
        VALUES (?, ?, ?, ?)
    """, (
        data['code'],
        data['libelle'],
        data['ordre'],
        data.get('is_active', True)
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_niveau', 'niveaux', cursor.lastrowid)
    return jsonify({'message': 'Niveau créé avec succès'}), 201

# ========== GESTION DES CLASSES ==========

@admin_bp.route('/classes', methods=['GET'])
@jwt_required()
def list_classes():
    """Liste les classes"""
    annee_id = request.args.get('annee_id')
    db = get_db()
    
    if annee_id:
        classes = db.execute("""
            SELECT c.*, f.libelle as filiere_libelle, n.libelle as niveau_libelle
            FROM classes c
            JOIN filieres f ON c.filiere_id = f.id
            JOIN niveaux n ON c.niveau_id = n.id
            WHERE c.annee_academique_id = ?
        """, (annee_id,)).fetchall()
    else:
        classes = db.execute("""
            SELECT c.*, f.libelle as filiere_libelle, n.libelle as niveau_libelle
            FROM classes c
            JOIN filieres f ON c.filiere_id = f.id
            JOIN niveaux n ON c.niveau_id = n.id
        """).fetchall()
    
    return jsonify([dict(classe) for classe in classes]), 200

@admin_bp.route('/classes', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_classe():
    """Crée une classe"""
    data = request.get_json()
    valid, error = validate_required(data, ['code', 'libelle', 'filiere_id', 'niveau_id', 'annee_academique_id'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO classes (code, libelle, filiere_id, niveau_id, annee_academique_id, effectif_max, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data['code'],
        data['libelle'],
        data['filiere_id'],
        data['niveau_id'],
        data['annee_academique_id'],
        data.get('effectif_max', 50),
        data.get('is_active', True)
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_classe', 'classes', cursor.lastrowid)
    return jsonify({'message': 'Classe créée avec succès'}), 201

# ========== GESTION DES MATIÈRES ==========

@admin_bp.route('/matieres', methods=['GET'])
@jwt_required()
def list_matieres():
    """Liste les matières"""
    db = get_db()
    matieres = db.execute("SELECT * FROM matieres WHERE is_active = 1").fetchall()
    return jsonify([dict(matiere) for matiere in matieres]), 200

@admin_bp.route('/matieres', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_matiere():
    """Crée une matière"""
    data = request.get_json()
    valid, error = validate_required(data, ['code', 'libelle'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO matieres (code, libelle, coefficient, volume_horaire, is_active)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data['code'],
        data['libelle'],
        data.get('coefficient', 1.0),
        data.get('volume_horaire', 0),
        data.get('is_active', True)
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_matiere', 'matieres', cursor.lastrowid)
    return jsonify({'message': 'Matière créée avec succès'}), 201

# ========== GESTION DES FRAIS SCOLAIRES ==========

@admin_bp.route('/types-frais', methods=['GET'])
@jwt_required()
def list_types_frais():
    """Liste les types de frais"""
    db = get_db()
    types_frais = db.execute("SELECT * FROM types_frais WHERE is_active = 1").fetchall()
    return jsonify([dict(tf) for tf in types_frais]), 200

@admin_bp.route('/types-frais', methods=['POST'])
@jwt_required()
@role_required('admin')
def create_type_frais():
    """Crée un type de frais"""
    data = request.get_json()
    valid, error = validate_required(data, ['code', 'libelle', 'montant'])
    if not valid:
        return jsonify({'error': error}), 400
    
    montant_valid, montant_error = validate_montant(data['montant'])
    if not montant_valid:
        return jsonify({'error': montant_error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO types_frais (code, libelle, montant, is_obligatoire, is_active)
        VALUES (?, ?, ?, ?, ?)
    """, (
        data['code'],
        data['libelle'],
        data['montant'],
        data.get('is_obligatoire', True),
        data.get('is_active', True)
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'creation_type_frais', 'types_frais', cursor.lastrowid)
    return jsonify({'message': 'Type de frais créé avec succès'}), 201

@admin_bp.route('/frais-classes', methods=['POST'])
@jwt_required()
@role_required('admin')
def assign_frais_classe():
    """Assigne des frais à une classe"""
    data = request.get_json()
    valid, error = validate_required(data, ['classe_id', 'type_frais_id', 'montant', 'annee_academique_id'])
    if not valid:
        return jsonify({'error': error}), 400
    
    db = get_db()
    cursor = db.execute("""
        INSERT INTO frais_classes (classe_id, type_frais_id, montant, annee_academique_id)
        VALUES (?, ?, ?, ?)
    """, (
        data['classe_id'],
        data['type_frais_id'],
        data['montant'],
        data['annee_academique_id']
    ))
    db.commit()
    
    log_action(get_current_user()['id'], 'assignation_frais_classe', 'frais_classes', cursor.lastrowid)
    return jsonify({'message': 'Frais assigné à la classe avec succès'}), 201

# ========== STATISTIQUES ET TABLEAU DE BORD ==========

@admin_bp.route('/dashboard/stats', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_dashboard_stats():
    """Obtient les statistiques du tableau de bord"""
    db = get_db()
    
    # Nombre total d'étudiants
    total_etudiants = db.execute("SELECT COUNT(*) as count FROM etudiants WHERE is_active = 1").fetchone()['count']
    
    # Nombre total d'enseignants
    total_enseignants = db.execute("SELECT COUNT(*) as count FROM enseignants WHERE is_active = 1").fetchone()['count']
    
    # Nombre total de classes
    total_classes = db.execute("SELECT COUNT(*) as count FROM classes WHERE is_active = 1").fetchone()['count']
    
    # Taux de réussite (moyenne >= 10)
    reussite = db.execute("""
        SELECT COUNT(*) as count FROM moyennes 
        WHERE moyenne >= 10 AND periode = 'annuel'
    """).fetchone()['count']
    
    total_moyennes = db.execute("SELECT COUNT(*) as count FROM moyennes WHERE periode = 'annuel'").fetchone()['count']
    taux_reussite = (reussite / total_moyennes * 100) if total_moyennes > 0 else 0
    
    # Total des paiements du mois
    total_paiements = db.execute("""
        SELECT COALESCE(SUM(montant), 0) as total FROM paiements 
        WHERE statut = 'valide' AND strftime('%Y-%m', date_paiement) = strftime('%Y-%m', 'now')
    """).fetchone()['total']
    
    # Absences du mois
    total_absences = db.execute("""
        SELECT COUNT(*) as count FROM absences 
        WHERE strftime('%Y-%m', date_absence) = strftime('%Y-%m', 'now')
    """).fetchone()['count']
    
    return jsonify({
        'total_etudiants': total_etudiants,
        'total_enseignants': total_enseignants,
        'total_classes': total_classes,
        'taux_reussite': round(taux_reussite, 2),
        'total_paiements_mois': total_paiements,
        'total_absences_mois': total_absences
    }), 200


