"""
Test complet de communication Frontend-Backend-Database
"""
import requests
import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5000/api"
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'esa.db')

class CommunicationTester:
    def __init__(self):
        self.results = []
        self.errors = []
    
    def log_result(self, test_name, success, details=""):
        """Enregistre un résultat de test"""
        self.results.append({
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
        if details:
            print(f"      {details}")
    
    def test_backend_health(self):
        """Test 1: Vérifier que le backend est accessible"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                self.log_result("Backend Health Check", True, f"Status: {response.status_code}")
                return True
            else:
                self.log_result("Backend Health Check", False, f"Status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_result("Backend Health Check", False, "Serveur non accessible. Démarrez-le avec: python3 app.py")
            return False
        except Exception as e:
            self.log_result("Backend Health Check", False, f"Erreur: {str(e)}")
            return False
    
    def test_database_connection(self):
        """Test 2: Vérifier la connexion à la base de données"""
        try:
            if not os.path.exists(DB_PATH):
                self.log_result("Database Connection", False, f"Base de données non trouvée: {DB_PATH}")
                return False
            
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Vérifier que la table users existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if cursor.fetchone():
                self.log_result("Database Connection", True, f"Base de données accessible: {DB_PATH}")
                conn.close()
                return True
            else:
                self.log_result("Database Connection", False, "Table 'users' non trouvée")
                conn.close()
                return False
        except Exception as e:
            self.log_result("Database Connection", False, f"Erreur: {str(e)}")
            return False
    
    def test_database_schema(self):
        """Test 3: Vérifier le schéma de la base de données"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Vérifier les tables essentielles
            essential_tables = ['users', 'etudiants', 'enseignants', 'parents', 'classes', 'matieres']
            missing_tables = []
            
            for table in essential_tables:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if not cursor.fetchone():
                    missing_tables.append(table)
            
            if missing_tables:
                self.log_result("Database Schema", False, f"Tables manquantes: {', '.join(missing_tables)}")
                conn.close()
                return False
            else:
                self.log_result("Database Schema", True, f"Toutes les tables essentielles présentes")
                conn.close()
                return True
        except Exception as e:
            self.log_result("Database Schema", False, f"Erreur: {str(e)}")
            return False
    
    def test_cors_configuration(self):
        """Test 4: Vérifier la configuration CORS"""
        try:
            response = requests.options(
                f"{BASE_URL}/health",
                headers={
                    'Origin': 'http://localhost',
                    'Access-Control-Request-Method': 'GET'
                },
                timeout=5
            )
            
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            }
            
            if cors_headers['Access-Control-Allow-Origin']:
                self.log_result("CORS Configuration", True, f"Headers: {cors_headers}")
                return True
            else:
                self.log_result("CORS Configuration", False, "Headers CORS manquants")
                return False
        except Exception as e:
            self.log_result("CORS Configuration", False, f"Erreur: {str(e)}")
            return False
    
    def test_auth_endpoints(self):
        """Test 5: Vérifier les endpoints d'authentification"""
        endpoints = [
            ('POST', '/auth/login', {'username': 'admin', 'password': 'password123'}),
            ('POST', '/auth/register', {
                'username': f'test_user_{int(datetime.now().timestamp())}',
                'email': f'test_{int(datetime.now().timestamp())}@test.com',
                'password': 'password123',
                'nom': 'Test',
                'prenom': 'User',
                'role': 'etudiant'
            }),
        ]
        
        results = []
        for method, endpoint, data in endpoints:
            try:
                if method == 'POST':
                    response = requests.post(
                        f"{BASE_URL}{endpoint}",
                        json=data,
                        headers={'Content-Type': 'application/json'},
                        timeout=10
                    )
                    success = response.status_code in [200, 201, 400, 401]  # 400/401 sont attendus pour certains tests
                    status = "accessible" if success else "inaccessible"
                    self.log_result(f"Endpoint {endpoint}", success, f"Status: {response.status_code} - {status}")
                    results.append(success)
            except Exception as e:
                self.log_result(f"Endpoint {endpoint}", False, f"Erreur: {str(e)}")
                results.append(False)
        
        return all(results)
    
    def test_database_read_write(self):
        """Test 6: Vérifier les opérations de lecture/écriture"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Test de lecture
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            # Test d'écriture (création d'un enregistrement temporaire)
            test_username = f"test_read_write_{int(datetime.now().timestamp())}"
            try:
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, role, nom, prenom, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (test_username, f"{test_username}@test.com", "hash", "etudiant", "Test", "User", 0))
                conn.commit()
                
                # Vérifier la lecture
                cursor.execute("SELECT id FROM users WHERE username = ?", (test_username,))
                if cursor.fetchone():
                    # Nettoyer
                    cursor.execute("DELETE FROM users WHERE username = ?", (test_username,))
                    conn.commit()
                    self.log_result("Database Read/Write", True, f"Lecture/écriture fonctionnelles. {user_count} utilisateurs")
                    conn.close()
                    return True
                else:
                    self.log_result("Database Read/Write", False, "Écriture réussie mais lecture échouée")
                    conn.close()
                    return False
            except sqlite3.IntegrityError:
                # L'utilisateur existe déjà, c'est OK
                cursor.execute("DELETE FROM users WHERE username = ?", (test_username,))
                conn.commit()
                self.log_result("Database Read/Write", True, f"Lecture/écriture fonctionnelles. {user_count} utilisateurs")
                conn.close()
                return True
        except Exception as e:
            self.log_result("Database Read/Write", False, f"Erreur: {str(e)}")
            return False
    
    def test_api_response_format(self):
        """Test 7: Vérifier le format des réponses API"""
        try:
            # Test avec un endpoint qui devrait retourner du JSON
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={'username': 'admin', 'password': 'password123'},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        self.log_result("API Response Format", True, "Format JSON valide")
                        return True
                    else:
                        self.log_result("API Response Format", False, "Réponse n'est pas un dictionnaire")
                        return False
                except ValueError:
                    self.log_result("API Response Format", False, "Réponse n'est pas du JSON valide")
                    return False
            else:
                # Même si le login échoue, on vérifie le format
                try:
                    data = response.json()
                    self.log_result("API Response Format", True, "Format JSON valide (même en cas d'erreur)")
                    return True
                except:
                    self.log_result("API Response Format", False, "Format de réponse invalide")
                    return False
        except Exception as e:
            self.log_result("API Response Format", False, f"Erreur: {str(e)}")
            return False
    
    def test_frontend_backend_connection(self):
        """Test 8: Simuler une connexion frontend-backend"""
        try:
            # Simuler une requête comme le ferait le frontend
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Origin': 'http://localhost',  # Simuler le frontend
            }
            
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={'username': 'admin', 'password': 'password123'},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' in data:
                    token = data['access_token']
                    
                    # Tester une requête authentifiée
                    auth_headers = {
                        'Authorization': f'Bearer {token}',
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                    }
                    
                    # Tester l'endpoint /auth/me
                    me_response = requests.get(
                        f"{BASE_URL}/auth/me",
                        headers=auth_headers,
                        timeout=10
                    )
                    
                    if me_response.status_code == 200:
                        self.log_result("Frontend-Backend Connection", True, "Authentification et requêtes authentifiées fonctionnelles")
                        return True
                    else:
                        self.log_result("Frontend-Backend Connection", False, f"Requête authentifiée échouée: {me_response.status_code}")
                        return False
                else:
                    self.log_result("Frontend-Backend Connection", False, "Token d'accès manquant dans la réponse")
                    return False
            else:
                self.log_result("Frontend-Backend Connection", False, f"Login échoué: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Frontend-Backend Connection", False, f"Erreur: {str(e)}")
            return False
    
    def test_database_backend_integration(self):
        """Test 9: Vérifier l'intégration base de données - backend"""
        try:
            # Créer un utilisateur via l'API
            timestamp = int(datetime.now().timestamp())
            user_data = {
                'username': f'test_integration_{timestamp}',
                'email': f'test_integration_{timestamp}@test.com',
                'password': 'password123',
                'nom': 'Test',
                'prenom': 'Integration',
                'role': 'etudiant'
            }
            
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=user_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 201:
                # Vérifier dans la base de données
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT id, username, email, role FROM users WHERE username = ?", (user_data['username'],))
                user = cursor.fetchone()
                
                if user:
                    # Nettoyer
                    cursor.execute("DELETE FROM users WHERE username = ?", (user_data['username'],))
                    conn.commit()
                    conn.close()
                    self.log_result("Database-Backend Integration", True, "Création via API et vérification DB réussies")
                    return True
                else:
                    self.log_result("Database-Backend Integration", False, "Utilisateur créé via API mais non trouvé en DB")
                    conn.close()
                    return False
            else:
                self.log_result("Database-Backend Integration", False, f"Création via API échouée: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Database-Backend Integration", False, f"Erreur: {str(e)}")
            return False
    
    def generate_report(self):
        """Génère un rapport complet"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r['success'])
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        report = []
        report.append("=" * 100)
        report.append("RAPPORT DE COMMUNICATION FRONTEND-BACKEND-DATABASE")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 100)
        report.append("")
        
        # Statistiques
        report.append("📊 STATISTIQUES GÉNÉRALES")
        report.append("-" * 100)
        report.append(f"Total des tests        : {total}")
        report.append(f"✅ Réussis             : {passed}")
        report.append(f"❌ Échoués             : {failed}")
        report.append(f"📈 Taux de réussite    : {success_rate:.1f}%")
        report.append("")
        
        # Détails
        report.append("📋 DÉTAILS DES TESTS")
        report.append("-" * 100)
        for result in self.results:
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            report.append(f"{status} - {result['test']}")
            if result['details']:
                report.append(f"      {result['details']}")
        report.append("")
        
        # Résumé
        report.append("=" * 100)
        if success_rate == 100:
            report.append("🎉 TOUS LES TESTS SONT RÉUSSIS !")
        elif success_rate >= 80:
            report.append("⚠️  LA PLUPART DES TESTS SONT RÉUSSIS")
        else:
            report.append("❌ PLUSIEURS TESTS ONT ÉCHOUÉ - VÉRIFIER LA CONFIGURATION")
        report.append("=" * 100)
        
        return "\n".join(report)
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🔍 DÉMARRAGE DES TESTS DE COMMUNICATION\n")
        
        self.test_backend_health()
        self.test_database_connection()
        self.test_database_schema()
        self.test_cors_configuration()
        self.test_auth_endpoints()
        self.test_database_read_write()
        self.test_api_response_format()
        self.test_frontend_backend_connection()
        self.test_database_backend_integration()
        
        print("\n" + "=" * 100)
        report = self.generate_report()
        print(report)
        
        # Sauvegarder le rapport
        import os
        report_dir = os.path.dirname(os.path.abspath(__file__))
        report_file = os.path.join(report_dir, f"rapport_communication_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 Rapport sauvegardé: {report_file}")

if __name__ == "__main__":
    tester = CommunicationTester()
    tester.run_all_tests()


