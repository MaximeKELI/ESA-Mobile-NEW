"""
Vérification rapide de la configuration
"""
import os
import sqlite3
import sys

def check_database():
    """Vérifie la base de données"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'esa.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Base de données non trouvée: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier les tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        essential = ['users', 'etudiants', 'enseignants', 'parents']
        missing = [t for t in essential if t not in tables]
        
        if missing:
            print(f"❌ Tables manquantes: {', '.join(missing)}")
            conn.close()
            return False
        
        # Compter les utilisateurs
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        conn.close()
        print(f"✅ Base de données OK: {len(tables)} tables, {count} utilisateurs")
        return True
    except Exception as e:
        print(f"❌ Erreur base de données: {e}")
        return False

def check_backend_config():
    """Vérifie la configuration backend"""
    app_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app.py')
    
    if not os.path.exists(app_file):
        print(f"❌ Fichier app.py non trouvé: {app_file}")
        return False
    
    with open(app_file, 'r') as f:
        content = f.read()
        
        checks = {
            'CORS': 'flask_cors' in content or 'CORS' in content,
            'JWT': 'JWTManager' in content or 'flask_jwt_extended' in content,
            'Database': 'DATABASE' in content,
            'Blueprints': 'register_blueprint' in content,
        }
        
        all_ok = all(checks.values())
        
        if all_ok:
            print("✅ Configuration backend OK")
            for key, value in checks.items():
                print(f"   - {key}: {'✅' if value else '❌'}")
        else:
            print("❌ Configuration backend incomplète")
            for key, value in checks.items():
                print(f"   - {key}: {'✅' if value else '❌'}")
        
        return all_ok

def check_frontend_config():
    """Vérifie la configuration frontend"""
    api_constants = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        'esa', 'lib', 'core', 'constants', 'api_constants.dart'
    )
    
    if not os.path.exists(api_constants):
        print(f"⚠️  Fichier api_constants.dart non trouvé")
        return False
    
    with open(api_constants, 'r') as f:
        content = f.read()
        
        checks = {
            'baseUrl': 'baseUrl' in content,
            'localhost': 'localhost:5000' in content or '127.0.0.1:5000' in content,
            'endpoints': 'login' in content and 'register' in content,
        }
        
        all_ok = all(checks.values())
        
        if all_ok:
            print("✅ Configuration frontend OK")
            for key, value in checks.items():
                print(f"   - {key}: {'✅' if value else '❌'}")
        else:
            print("❌ Configuration frontend incomplète")
            for key, value in checks.items():
                print(f"   - {key}: {'✅' if value else '❌'}")
        
        return all_ok

def main():
    print("🔍 VÉRIFICATION RAPIDE DE LA CONFIGURATION\n")
    
    results = {
        'Database': check_database(),
        'Backend': check_backend_config(),
        'Frontend': check_frontend_config(),
    }
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ")
    print("=" * 60)
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {component}")
    
    all_ok = all(results.values())
    
    print("\n" + "=" * 60)
    if all_ok:
        print("🎉 TOUS LES COMPOSANTS SONT CONFIGURÉS CORRECTEMENT")
        print("\n💡 Pour tester la communication complète:")
        print("   1. Démarrer le backend: cd backend && python3 app.py")
        print("   2. Lancer les tests: python3 tests/test_communication_complete.py")
    else:
        print("⚠️  CERTAINS COMPOSANTS NÉCESSITENT UNE ATTENTION")
    print("=" * 60)

if __name__ == "__main__":
    main()


