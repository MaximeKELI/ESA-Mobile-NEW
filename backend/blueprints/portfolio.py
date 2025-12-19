"""
Blueprint pour le Portfolio Numérique
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from database.db import get_db
from utils.auth import get_current_user, role_required, log_action
from utils.validators import validate_required
from datetime import datetime
import json
import os

portfolio_bp = Blueprint('portfolio', __name__)

@portfolio_bp.route('/mon-portfolio', methods=['GET'])
@jwt_required()
def get_my_portfolio():
    """Obtient le portfolio de l'étudiant connecté"""
    current_user = get_current_user()
    db = get_db()
    
    if current_user['role'] != 'etudiant':
        return jsonify({'error': 'Accès réservé aux étudiants'}), 403
    
    etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Profil étudiant non trouvé'}), 404
    
    # Créer le portfolio s'il n'existe pas
    portfolio = db.execute("SELECT * FROM portfolios WHERE etudiant_id = ?", 
                          (etudiant['id'],)).fetchone()
    
    if not portfolio:
        cursor = db.execute("""
            INSERT INTO portfolios (etudiant_id, titre, description, is_public)
            VALUES (?, ?, ?, ?)
        """, (
            etudiant['id'],
            f"Portfolio de {current_user['nom']} {current_user['prenom']}",
            "Mon portfolio académique et professionnel",
            False
        ))
        db.commit()
        portfolio = db.execute("SELECT * FROM portfolios WHERE id = ?", 
                              (cursor.lastrowid,)).fetchone()
    
    # Récupérer les compétences
    competences = db.execute("""
        SELECT ca.*, c.libelle as competence_libelle, c.code as competence_code
        FROM competences_acquises ca
        JOIN competences c ON ca.competence_id = c.id
        WHERE ca.portfolio_id = ?
    """, (portfolio['id'],)).fetchall()
    
    # Récupérer les projets
    projets = db.execute("""
        SELECT * FROM projets_portfolio
        WHERE portfolio_id = ? AND is_visible = 1
        ORDER BY ordre, date_realisation DESC
    """, (portfolio['id'],)).fetchall()
    
    # Récupérer les certifications
    certifications = db.execute("""
        SELECT * FROM certifications_portfolio
        WHERE portfolio_id = ? AND is_visible = 1
        ORDER BY date_obtention DESC
    """, (portfolio['id'],)).fetchall()
    
    # Récupérer les réalisations
    realisations = db.execute("""
        SELECT * FROM realisations
        WHERE portfolio_id = ? AND is_visible = 1
        ORDER BY date_realisation DESC
    """, (portfolio['id'],)).fetchall()
    
    return jsonify({
        **dict(portfolio),
        'competences': [dict(c) for c in competences],
        'projets': [dict(p) for p in projets],
        'certifications': [dict(c) for c in certifications],
        'realisations': [dict(r) for r in realisations]
    }), 200

@portfolio_bp.route('/competences', methods=['GET'])
@jwt_required()
def list_competences():
    """Liste toutes les compétences disponibles"""
    db = get_db()
    competences = db.execute("""
        SELECT * FROM competences WHERE is_active = 1 ORDER BY libelle
    """).fetchall()
    return jsonify([dict(c) for c in competences]), 200

@portfolio_bp.route('/competences/acquises', methods=['POST'])
@jwt_required()
def ajouter_competence():
    """Ajoute une compétence acquise au portfolio"""
    data = request.get_json()
    valid, error = validate_required(data, ['competence_id', 'niveau'])
    if not valid:
        return jsonify({'error': error}), 400
    
    current_user = get_current_user()
    db = get_db()
    
    if current_user['role'] != 'etudiant':
        return jsonify({'error': 'Accès réservé aux étudiants'}), 403
    
    etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Profil étudiant non trouvé'}), 404
    
    # Obtenir ou créer le portfolio
    portfolio = db.execute("SELECT id FROM portfolios WHERE etudiant_id = ?", 
                          (etudiant['id'],)).fetchone()
    if not portfolio:
        cursor = db.execute("""
            INSERT INTO portfolios (etudiant_id, titre, description)
            VALUES (?, ?, ?)
        """, (etudiant['id'], f"Portfolio", "Mon portfolio"))
        db.commit()
        portfolio_id = cursor.lastrowid
    else:
        portfolio_id = portfolio['id']
    
    # Vérifier si la compétence existe déjà
    existing = db.execute("""
        SELECT id FROM competences_acquises
        WHERE portfolio_id = ? AND competence_id = ?
    """, (portfolio_id, data['competence_id'])).fetchone()
    
    if existing:
        # Mettre à jour
        db.execute("""
            UPDATE competences_acquises
            SET niveau = ?, date_acquisition = ?, preuve_path = ?
            WHERE id = ?
        """, (
            data['niveau'],
            data.get('date_acquisition', datetime.now().date()),
            data.get('preuve_path'),
            existing['id']
        ))
    else:
        # Créer
        db.execute("""
            INSERT INTO competences_acquises (portfolio_id, competence_id, niveau,
                                            date_acquisition, preuve_path)
            VALUES (?, ?, ?, ?, ?)
        """, (
            portfolio_id,
            data['competence_id'],
            data['niveau'],
            data.get('date_acquisition', datetime.now().date()),
            data.get('preuve_path')
        ))
    
    db.commit()
    return jsonify({'message': 'Compétence ajoutée au portfolio'}), 201

@portfolio_bp.route('/projets', methods=['POST'])
@jwt_required()
def ajouter_projet():
    """Ajoute un projet au portfolio"""
    data = request.get_json()
    valid, error = validate_required(data, ['titre'])
    if not valid:
        return jsonify({'error': error}), 400
    
    current_user = get_current_user()
    db = get_db()
    
    if current_user['role'] != 'etudiant':
        return jsonify({'error': 'Accès réservé aux étudiants'}), 403
    
    etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Profil étudiant non trouvé'}), 404
    
    portfolio = db.execute("SELECT id FROM portfolios WHERE etudiant_id = ?", 
                          (etudiant['id'],)).fetchone()
    if not portfolio:
        cursor = db.execute("INSERT INTO portfolios (etudiant_id, titre) VALUES (?, ?)",
                           (etudiant['id'], "Portfolio"))
        db.commit()
        portfolio_id = cursor.lastrowid
    else:
        portfolio_id = portfolio['id']
    
    cursor = db.execute("""
        INSERT INTO projets_portfolio (portfolio_id, titre, description, type_projet,
                                     date_realisation, technologies, fichiers_paths,
                                     lien_externe, is_visible, ordre)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        portfolio_id,
        data['titre'],
        data.get('description'),
        data.get('type_projet'),
        data.get('date_realisation'),
        json.dumps(data.get('technologies', [])),
        json.dumps(data.get('fichiers_paths', [])),
        data.get('lien_externe'),
        data.get('is_visible', True),
        data.get('ordre', 0)
    ))
    db.commit()
    
    return jsonify({'message': 'Projet ajouté', 'projet_id': cursor.lastrowid}), 201

@portfolio_bp.route('/certifications', methods=['POST'])
@jwt_required()
def ajouter_certification():
    """Ajoute une certification au portfolio"""
    data = request.get_json()
    valid, error = validate_required(data, ['nom_certification', 'date_obtention'])
    if not valid:
        return jsonify({'error': error}), 400
    
    current_user = get_current_user()
    db = get_db()
    
    if current_user['role'] != 'etudiant':
        return jsonify({'error': 'Accès réservé aux étudiants'}), 403
    
    etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Profil étudiant non trouvé'}), 404
    
    portfolio = db.execute("SELECT id FROM portfolios WHERE etudiant_id = ?", 
                          (etudiant['id'],)).fetchone()
    if not portfolio:
        cursor = db.execute("INSERT INTO portfolios (etudiant_id, titre) VALUES (?, ?)",
                           (etudiant['id'], "Portfolio"))
        db.commit()
        portfolio_id = cursor.lastrowid
    else:
        portfolio_id = portfolio['id']
    
    cursor = db.execute("""
        INSERT INTO certifications_portfolio (portfolio_id, nom_certification, organisme,
                                             date_obtention, date_expiration, numero_certificat,
                                             fichier_path, lien_verification, is_visible)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        portfolio_id,
        data['nom_certification'],
        data.get('organisme'),
        data['date_obtention'],
        data.get('date_expiration'),
        data.get('numero_certificat'),
        data.get('fichier_path'),
        data.get('lien_verification'),
        data.get('is_visible', True)
    ))
    db.commit()
    
    return jsonify({'message': 'Certification ajoutée', 'certification_id': cursor.lastrowid}), 201

@portfolio_bp.route('/generer-cv', methods=['GET'])
@jwt_required()
def generer_cv():
    """Génère un CV PDF à partir du portfolio"""
    current_user = get_current_user()
    db = get_db()
    
    if current_user['role'] != 'etudiant':
        return jsonify({'error': 'Accès réservé aux étudiants'}), 403
    
    etudiant = db.execute("""
        SELECT e.*, u.nom, u.prenom, u.email, u.telephone, u.adresse,
               c.libelle as classe_libelle
        FROM etudiants e
        JOIN users u ON e.user_id = u.id
        LEFT JOIN classes c ON e.classe_id = c.id
        WHERE e.user_id = ?
    """, (current_user['id'],)).fetchone()
    
    if not etudiant:
        return jsonify({'error': 'Profil étudiant non trouvé'}), 404
    
    portfolio = db.execute("SELECT * FROM portfolios WHERE etudiant_id = ?", 
                          (etudiant['id'],)).fetchone()
    
    if not portfolio:
        return jsonify({'error': 'Portfolio non trouvé'}), 404
    
    # Générer le CV PDF (utiliser reportlab)
    from utils.pdf_generator import generate_cv_pdf
    
    output_path = os.path.join(
        request.application.config['UPLOAD_FOLDER'],
        'pdf',
        f'cv_{etudiant["numero_etudiant"]}.pdf'
    )
    
    generate_cv_pdf(etudiant, portfolio, output_path)
    
    return send_file(output_path, mimetype='application/pdf', as_attachment=True,
                    download_name=f'cv_{etudiant["numero_etudiant"]}.pdf')

@portfolio_bp.route('/partager', methods=['POST'])
@jwt_required()
def partager_portfolio():
    """Rend le portfolio public et génère une URL de partage"""
    data = request.get_json()
    current_user = get_current_user()
    db = get_db()
    
    if current_user['role'] != 'etudiant':
        return jsonify({'error': 'Accès réservé aux étudiants'}), 403
    
    etudiant = db.execute("SELECT id FROM etudiants WHERE user_id = ?", 
                         (current_user['id'],)).fetchone()
    if not etudiant:
        return jsonify({'error': 'Profil étudiant non trouvé'}), 404
    
    portfolio = db.execute("SELECT * FROM portfolios WHERE etudiant_id = ?", 
                          (etudiant['id'],)).fetchone()
    
    if not portfolio:
        return jsonify({'error': 'Portfolio non trouvé'}), 404
    
    is_public = data.get('is_public', True)
    
    # Générer une URL publique unique
    import secrets
    url_public = secrets.token_urlsafe(16) if is_public else None
    
    db.execute("""
        UPDATE portfolios
        SET is_public = ?, url_public = ?, date_modification = ?
        WHERE id = ?
    """, (is_public, url_public, datetime.now(), portfolio['id']))
    db.commit()
    
    return jsonify({
        'message': 'Portfolio partagé' if is_public else 'Portfolio rendu privé',
        'url_public': f'/portfolio/public/{url_public}' if url_public else None
    }), 200

@portfolio_bp.route('/public/<url_public>', methods=['GET'])
def voir_portfolio_public(url_public):
    """Affiche un portfolio public"""
    db = get_db()
    
    portfolio = db.execute("""
        SELECT p.*, e.numero_etudiant, u.nom, u.prenom
        FROM portfolios p
        JOIN etudiants e ON p.etudiant_id = e.id
        JOIN users u ON e.user_id = u.id
        WHERE p.url_public = ? AND p.is_public = 1
    """, (url_public,)).fetchone()
    
    if not portfolio:
        return jsonify({'error': 'Portfolio non trouvé ou non public'}), 404
    
    # Récupérer les éléments publics seulement
    competences = db.execute("""
        SELECT ca.*, c.libelle as competence_libelle
        FROM competences_acquises ca
        JOIN competences c ON ca.competence_id = c.id
        WHERE ca.portfolio_id = ?
    """, (portfolio['id'],)).fetchall()
    
    projets = db.execute("""
        SELECT * FROM projets_portfolio
        WHERE portfolio_id = ? AND is_visible = 1
        ORDER BY date_realisation DESC
    """, (portfolio['id'],)).fetchall()
    
    return jsonify({
        **dict(portfolio),
        'competences': [dict(c) for c in competences],
        'projets': [dict(p) for p in projets]
    }), 200

