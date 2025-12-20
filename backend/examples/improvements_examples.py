"""
Exemples d'implémentation des améliorations prioritaires
"""

# ============================================
# 1. HASHAGE BCRYPT (Sécurité)
# ============================================

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def hash_password_secure(password):
    """Hash un mot de passe avec bcrypt"""
    return bcrypt.generate_password_hash(password).decode('utf-8')

def verify_password_secure(password, password_hash):
    """Vérifie un mot de passe avec bcrypt"""
    return bcrypt.check_password_hash(password_hash, password)

# Utilisation dans auth.py
# Remplacer :
# password_hash = hashlib.sha256(password.encode()).hexdigest()
# Par :
# password_hash = hash_password_secure(password)


# ============================================
# 2. RATE LIMITING (Sécurité)
# ============================================

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Dans auth.py
@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Max 5 tentatives par minute
def login():
    # ... code existant ...


# ============================================
# 3. CACHE REDIS (Performance)
# ============================================

from flask_caching import Cache

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Utilisation
@admin_bp.route('/dashboard/stats', methods=['GET'])
@cache.cached(timeout=300)  # Cache 5 minutes
@jwt_required()
@role_required('admin')
def get_dashboard_stats():
    # ... code existant ...
    return jsonify(stats), 200

# Invalider le cache après modification
def invalidate_stats_cache():
    cache.delete('view/get_dashboard_stats')


# ============================================
# 4. NOTIFICATIONS EMAIL (Communication)
# ============================================

from flask_mail import Mail, Message

mail = Mail(app)

def send_welcome_email(user_email, username):
    """Envoie un email de bienvenue"""
    msg = Message(
        subject='Bienvenue sur la plateforme ESA',
        recipients=[user_email],
        html=f"""
        <h1>Bienvenue {username} !</h1>
        <p>Votre compte a été créé avec succès.</p>
        <p>Vous pouvez maintenant accéder à la plateforme.</p>
        """
    )
    mail.send(msg)

def send_payment_reminder_email(user_email, montant_du, date_echeance):
    """Envoie un rappel de paiement"""
    msg = Message(
        subject='Rappel: Frais scolaires à régulariser',
        recipients=[user_email],
        html=f"""
        <h2>Rappel de paiement</h2>
        <p>Vous avez un solde impayé de <strong>{montant_du} FCFA</strong>.</p>
        <p>Date d'échéance : <strong>{date_echeance}</strong></p>
        <p>Veuillez régulariser votre situation au plus vite.</p>
        """
    )
    mail.send(msg)


# ============================================
# 5. NOTIFICATIONS PUSH (Mobile)
# ============================================

import firebase_admin
from firebase_admin import messaging

# Initialisation (une seule fois)
cred = firebase_admin.credentials.Certificate('path/to/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

def send_push_notification(user_fcm_token, title, body, data=None):
    """Envoie une notification push"""
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data=data or {},
        token=user_fcm_token,
    )
    
    try:
        response = messaging.send(message)
        return response
    except Exception as e:
        print(f"Erreur envoi push: {e}")
        return None


# ============================================
# 6. PAGINATION (Performance)
# ============================================

def paginate_query(query, page=1, per_page=20):
    """Pagine une requête SQL"""
    offset = (page - 1) * per_page
    
    # Compter le total
    total = db.execute(f"SELECT COUNT(*) as count FROM ({query})").fetchone()['count']
    
    # Requête paginée
    paginated_query = f"{query} LIMIT {per_page} OFFSET {offset}"
    results = db.execute(paginated_query).fetchall()
    
    return {
        'data': [dict(r) for r in results],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    }

# Utilisation
@admin_bp.route('/users', methods=['GET'])
def list_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    result = paginate_query(
        "SELECT * FROM users",
        page=page,
        per_page=per_page
    )
    
    return jsonify(result), 200


# ============================================
# 7. RECHERCHE FULL-TEXT (UX)
# ============================================

def search_global(query_text, limit=50):
    """Recherche globale dans tous les modules"""
    results = {
        'users': [],
        'etudiants': [],
        'classes': [],
        'matieres': []
    }
    
    search_term = f"%{query_text}%"
    
    # Recherche dans les utilisateurs
    users = db.execute("""
        SELECT id, nom, prenom, email, role
        FROM users
        WHERE nom LIKE ? OR prenom LIKE ? OR email LIKE ?
        LIMIT ?
    """, (search_term, search_term, search_term, limit)).fetchall()
    results['users'] = [dict(u) for u in users]
    
    # Recherche dans les étudiants
    etudiants = db.execute("""
        SELECT e.id, e.numero_etudiant, u.nom, u.prenom
        FROM etudiants e
        JOIN users u ON e.user_id = u.id
        WHERE e.numero_etudiant LIKE ? OR u.nom LIKE ? OR u.prenom LIKE ?
        LIMIT ?
    """, (search_term, search_term, search_term, limit)).fetchall()
    results['etudiants'] = [dict(e) for e in etudiants]
    
    # Recherche dans les classes
    classes = db.execute("""
        SELECT id, code, libelle
        FROM classes
        WHERE code LIKE ? OR libelle LIKE ?
        LIMIT ?
    """, (search_term, search_term, limit)).fetchall()
    results['classes'] = [dict(c) for c in classes]
    
    return results


# ============================================
# 8. EXPORT EXCEL (Rapports)
# ============================================

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

def export_students_to_excel(etudiants_data, filename):
    """Exporte la liste des étudiants en Excel"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Étudiants"
    
    # En-têtes
    headers = ['Numéro', 'Nom', 'Prénom', 'Email', 'Classe', 'Date inscription']
    ws.append(headers)
    
    # Style des en-têtes
    for cell in ws[1]:
        cell.font = Font(bold=True)
        cell.alignment = Alignment(horizontal='center')
    
    # Données
    for etudiant in etudiants_data:
        ws.append([
            etudiant['numero_etudiant'],
            etudiant['nom'],
            etudiant['prenom'],
            etudiant['email'],
            etudiant['classe_libelle'],
            etudiant['date_inscription']
        ])
    
    # Ajuster la largeur des colonnes
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        adjusted_width = min(max_length + 2, 50)
        ws.column_dimensions[column_letter].width = adjusted_width
    
    wb.save(filename)
    return filename


# ============================================
# 9. TÂCHES PLANIFIÉES (Automatisation)
# ============================================

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def check_unpaid_fees():
    """Vérifie les frais impayés et envoie des rappels"""
    db = get_db()
    
    # Trouver les étudiants avec frais impayés
    etudiants_impayes = db.execute("""
        SELECT e.id, e.user_id, u.email, u.telephone,
               (SELECT SUM(fc.montant) FROM frais_classes fc 
                WHERE fc.classe_id = e.classe_id) - 
               (SELECT COALESCE(SUM(p.montant), 0) FROM paiements p 
                WHERE p.etudiant_id = e.id AND p.statut = 'valide') as solde
        FROM etudiants e
        JOIN users u ON e.user_id = u.id
        HAVING solde > 0
    """).fetchall()
    
    for etudiant in etudiants_impayes:
        # Envoyer notification
        send_notification(
            etudiant['user_id'],
            'frais_impayes',
            'Rappel: Frais impayés',
            f'Vous avez un solde impayé de {etudiant["solde"]} FCFA'
        )
        
        # Envoyer email si disponible
        if etudiant['email']:
            send_payment_reminder_email(
                etudiant['email'],
                etudiant['solde'],
                datetime.now().date()
            )

# Planifier la tâche (tous les jours à 8h)
scheduler.add_job(
    func=check_unpaid_fees,
    trigger="cron",
    hour=8,
    minute=0
)

scheduler.start()


# ============================================
# 10. VALIDATION AVANCÉE (Sécurité)
# ============================================

from marshmallow import Schema, fields, validate, ValidationError

class UserSchema(Schema):
    """Schéma de validation pour les utilisateurs"""
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50),
        error_messages={'required': 'Le nom d\'utilisateur est requis'}
    )
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        error_messages={'required': 'Le mot de passe est requis'}
    )
    role = fields.Str(
        required=True,
        validate=validate.OneOf(['admin', 'comptabilite', 'enseignant', 'etudiant', 'parent'])
    )
    nom = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    prenom = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    telephone = fields.Str(validate=validate.Regexp(r'^\+?[0-9]{8,15}$'))

# Utilisation
@admin_bp.route('/users', methods=['POST'])
def create_user():
    schema = UserSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # ... créer l'utilisateur ...


