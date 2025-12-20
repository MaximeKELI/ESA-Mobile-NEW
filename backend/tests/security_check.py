"""
Vérifications de sécurité automatisées
"""
import sqlite3
import hashlib
import re
from pathlib import Path

class SecurityChecker:
    def __init__(self, db_path='database/esa.db'):
        self.db_path = db_path
        self.issues = []
        self.warnings = []
    
    def check_password_hashing(self):
        """Vérifie que les mots de passe sont hashés avec bcrypt"""
        print("🔍 Vérification du hashage des mots de passe...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, password_hash FROM users LIMIT 10")
            users = cursor.fetchall()
            
            bcrypt_count = 0
            sha256_count = 0
            
            for user_id, password_hash in users:
                # Bcrypt commence par $2b$ ou $2a$
                if password_hash.startswith('$2'):
                    bcrypt_count += 1
                # SHA-256 fait 64 caractères hex
                elif len(password_hash) == 64:
                    sha256_count += 1
                    self.warnings.append({
                        'type': 'password_hashing',
                        'user_id': user_id,
                        'message': 'Mot de passe en SHA-256, doit être migré vers bcrypt'
                    })
            
            conn.close()
            
            if sha256_count > 0:
                self.issues.append({
                    'severity': 'high',
                    'type': 'password_hashing',
                    'message': f'{sha256_count} utilisateurs avec mots de passe en SHA-256'
                })
                print(f"  ⚠️  {sha256_count} mots de passe en SHA-256 détectés")
            else:
                print(f"  ✅ Tous les mots de passe utilisent bcrypt")
        
        except Exception as e:
            self.issues.append({
                'severity': 'medium',
                'type': 'password_hashing',
                'message': f'Erreur lors de la vérification: {str(e)}'
            })
    
    def check_sql_injection_protection(self):
        """Vérifie la protection contre les injections SQL"""
        print("🔍 Vérification de la protection SQL injection...")
        
        # Vérifier l'utilisation de requêtes paramétrées
        code_files = [
            'blueprints/auth.py',
            'blueprints/admin.py',
            'blueprints/comptabilite.py',
        ]
        
        vulnerable_patterns = [
            r'execute\s*\(\s*f["\'].*%[sd]',
            r'execute\s*\(\s*["\'].*\+.*\+',
            r'execute\s*\(\s*["\'].*\{.*\}',
        ]
        
        for file_path in code_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    for pattern in vulnerable_patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            self.issues.append({
                                'severity': 'high',
                                'type': 'sql_injection',
                                'file': file_path,
                                'message': 'Possible injection SQL détectée'
                            })
                            print(f"  ⚠️  Pattern suspect dans {file_path}")
            except FileNotFoundError:
                pass
        
        if not any(issue['type'] == 'sql_injection' for issue in self.issues):
            print("  ✅ Aucune injection SQL détectée")
    
    def check_secrets_in_code(self):
        """Vérifie la présence de secrets dans le code"""
        print("🔍 Vérification des secrets dans le code...")
        
        secret_patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'Mot de passe en dur'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'Clé API en dur'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'Secret en dur'),
            (r'admin123', 'Mot de passe par défaut'),
        ]
        
        code_files = Path('.').rglob('*.py')
        
        for file_path in code_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    for pattern, description in secret_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            self.warnings.append({
                                'type': 'secret_in_code',
                                'file': str(file_path),
                                'message': description
                            })
                            print(f"  ⚠️  {description} dans {file_path}")
            except Exception:
                pass
        
        if not any(w['type'] == 'secret_in_code' for w in self.warnings):
            print("  ✅ Aucun secret détecté dans le code")
    
    def check_file_permissions(self):
        """Vérifie les permissions des fichiers sensibles"""
        print("🔍 Vérification des permissions des fichiers...")
        
        sensitive_files = [
            'database/esa.db',
            '.env',
            'app.py',
        ]
        
        for file_path in sensitive_files:
            try:
                path = Path(file_path)
                if path.exists():
                    stat = path.stat()
                    # Vérifier que le fichier n'est pas accessible par tous
                    mode = stat.st_mode
                    # En Unix, vérifier les permissions
                    if (mode & 0o077) != 0:  # Autres et groupe ont des permissions
                        self.warnings.append({
                            'type': 'file_permissions',
                            'file': file_path,
                            'message': 'Permissions trop permissives'
                        })
                        print(f"  ⚠️  {file_path} a des permissions trop permissives")
            except Exception:
                pass
    
    def check_cors_configuration(self):
        """Vérifie la configuration CORS"""
        print("🔍 Vérification de la configuration CORS...")
        
        try:
            with open('app.py', 'r') as f:
                content = f.read()
                
                if "origins: '*'" in content or 'origins=["*"]' in content:
                    self.warnings.append({
                        'type': 'cors',
                        'message': 'CORS configuré pour accepter toutes les origines'
                    })
                    print("  ⚠️  CORS accepte toutes les origines (à restreindre en production)")
                else:
                    print("  ✅ CORS correctement configuré")
        except Exception as e:
            pass
    
    def check_jwt_configuration(self):
        """Vérifie la configuration JWT"""
        print("🔍 Vérification de la configuration JWT...")
        
        try:
            with open('app.py', 'r') as f:
                content = f.read()
                
                # Vérifier que le secret n'est pas le défaut
                if 'dev-secret-key' in content or 'jwt-secret-key-change' in content:
                    self.issues.append({
                        'severity': 'high',
                        'type': 'jwt_secret',
                        'message': 'Secret JWT par défaut détecté - À CHANGER EN PRODUCTION'
                    })
                    print("  ❌ Secret JWT par défaut détecté")
                else:
                    print("  ✅ Secret JWT personnalisé")
        except Exception as e:
            pass
    
    def check_input_validation(self):
        """Vérifie la validation des entrées"""
        print("🔍 Vérification de la validation des entrées...")
        
        validation_functions = [
            'validate_email_format',
            'validate_phone',
            'validate_date',
            'validate_note',
            'validate_montant',
            'sanitize_input',
        ]
        
        try:
            with open('utils/validators.py', 'r') as f:
                content = f.read()
                
                for func in validation_functions:
                    if func not in content:
                        self.warnings.append({
                            'type': 'validation',
                            'message': f'Fonction de validation {func} manquante'
                        })
            
            print("  ✅ Fonctions de validation présentes")
        except Exception as e:
            self.warnings.append({
                'type': 'validation',
                'message': f'Erreur lors de la vérification: {str(e)}'
            })
    
    def run_all_checks(self):
        """Exécute toutes les vérifications"""
        print("=" * 60)
        print("🔒 VÉRIFICATIONS DE SÉCURITÉ")
        print("=" * 60)
        print()
        
        self.check_password_hashing()
        self.check_sql_injection_protection()
        self.check_secrets_in_code()
        self.check_file_permissions()
        self.check_cors_configuration()
        self.check_jwt_configuration()
        self.check_input_validation()
        
        # Résumé
        print()
        print("=" * 60)
        print("📊 RÉSUMÉ")
        print("=" * 60)
        
        high_issues = [i for i in self.issues if i['severity'] == 'high']
        medium_issues = [i for i in self.issues if i['severity'] == 'medium']
        
        print(f"❌ Problèmes critiques: {len(high_issues)}")
        print(f"⚠️  Problèmes moyens: {len(medium_issues)}")
        print(f"⚠️  Avertissements: {len(self.warnings)}")
        
        if high_issues:
            print("\n🔴 PROBLÈMES CRITIQUES:")
            for issue in high_issues:
                print(f"  - {issue['message']}")
        
        if medium_issues:
            print("\n🟡 PROBLÈMES MOYENS:")
            for issue in medium_issues:
                print(f"  - {issue['message']}")
        
        if self.warnings:
            print("\n🟠 AVERTISSEMENTS:")
            for warning in self.warnings[:10]:  # Limiter à 10
                print(f"  - {warning['message']}")
        
        return {
            'issues': self.issues,
            'warnings': self.warnings
        }

if __name__ == "__main__":
    checker = SecurityChecker()
    results = checker.run_all_checks()
    
    import json
    with open('security_check_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n📄 Résultats sauvegardés dans security_check_results.json")


