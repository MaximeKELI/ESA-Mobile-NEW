"""
Application Flask principale - ESA Togo
Gestion scolaire complète avec API REST
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
import os
from datetime import timedelta

# Import des blueprints
from blueprints.auth import auth_bp
from blueprints.admin import admin_bp
from blueprints.comptabilite import comptabilite_bp
from blueprints.enseignant import enseignant_bp
from blueprints.etudiant import etudiant_bp
from blueprints.parent import parent_bp
from blueprints.commun import commun_bp
from blueprints.inscriptions import inscriptions_bp
from blueprints.bourses import bourses_bp
from blueprints.bibliotheque import bibliotheque_bp
from blueprints.stages import stages_bp
from blueprints.infrastructure import infrastructure_bp
from blueprints.ai_analytics import ai_analytics_bp
from blueprints.gamification import gamification_bp
from blueprints.elearning import elearning_bp
from blueprints.mobile_money import mobile_money_bp
from blueprints.chat_realtime import chat_realtime_bp
from blueprints.workflows import workflows_bp
from blueprints.dashboards import dashboards_bp
from blueprints.portfolio import portfolio_bp
from blueprints.chatbot import chatbot_bp
from blueprints.exports import exports_bp

# Import sécurité
from utils.security import init_security

def create_app():
    """Factory function pour créer l'application Flask"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'database', 'esa.db')
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Créer les dossiers nécessaires
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'photos'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'qr_codes'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'pdf'), exist_ok=True)
    
    # Initialiser les extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
    jwt = JWTManager(app)
    bcrypt = Bcrypt(app)
    
    # Initialiser la sécurité
    limiter = init_security(app)
    
    # Enregistrer les blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(comptabilite_bp, url_prefix='/api/comptabilite')
    app.register_blueprint(enseignant_bp, url_prefix='/api/enseignant')
    app.register_blueprint(etudiant_bp, url_prefix='/api/etudiant')
    app.register_blueprint(parent_bp, url_prefix='/api/parent')
    app.register_blueprint(commun_bp, url_prefix='/api/commun')
    app.register_blueprint(inscriptions_bp, url_prefix='/api/inscriptions')
    app.register_blueprint(bourses_bp, url_prefix='/api/bourses')
    app.register_blueprint(bibliotheque_bp, url_prefix='/api/bibliotheque')
    app.register_blueprint(stages_bp, url_prefix='/api/stages')
    app.register_blueprint(infrastructure_bp, url_prefix='/api/infrastructure')
    app.register_blueprint(ai_analytics_bp, url_prefix='/api/ai')
    app.register_blueprint(gamification_bp, url_prefix='/api/gamification')
    app.register_blueprint(elearning_bp, url_prefix='/api/elearning')
    app.register_blueprint(mobile_money_bp, url_prefix='/api/mobile-money')
    app.register_blueprint(chat_realtime_bp, url_prefix='/api/chat')
    app.register_blueprint(workflows_bp, url_prefix='/api/workflows')
    app.register_blueprint(dashboards_bp, url_prefix='/api/dashboards')
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    app.register_blueprint(chatbot_bp, url_prefix='/api/chatbot')
    app.register_blueprint(exports_bp, url_prefix='/api/exports')
    
    # Route de santé
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'ESA API is running'}, 200
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

