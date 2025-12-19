"""
Tests d'authentification avec génération de rapport détaillé
"""
import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple

BASE_URL = "http://localhost:5000/api"

class TestResult:
    def __init__(self, name: str, success: bool, status_code: int = None, details: str = ""):
        self.name = name
        self.success = success
        self.status_code = status_code
        self.details = details
        self.timestamp = datetime.now().strftime("%H:%M:%S")

class AuthTestRunner:
    def __init__(self):
        self.results: List[TestResult] = []
        self.tokens = {}
        self.created_users = []
    
    def add_result(self, name: str, success: bool, status_code: int = None, details: str = ""):
        self.results.append(TestResult(name, success, status_code, details))
    
    def test_server_health(self) -> bool:
        """Vérifie que le serveur est accessible"""
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_login_success(self):
        """Tests de connexion réussie"""
        test_cases = [
            {"name": "Login admin (username)", "data": {"username": "admin", "password": "password123"}},
            {"name": "Login admin (email)", "data": {"username": "admin@esa.tg", "password": "password123"}},
            {"name": "Login comptable", "data": {"username": "comptable", "password": "password123"}},
            {"name": "Login enseignant", "data": {"username": "enseignant1", "password": "password123"}},
            {"name": "Login étudiant", "data": {"username": "etudiant1", "password": "password123"}},
            {"name": "Login parent", "data": {"username": "parent1", "password": "password123"}},
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/login",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                success = response.status_code == 200
                details = ""
                
                if success:
                    data = response.json()
                    if "access_token" in data:
                        self.tokens[test_case["data"]["username"]] = data["access_token"]
                        details = f"Token obtenu"
                    else:
                        details = "Token manquant"
                else:
                    try:
                        error = response.json().get("error", "")
                        details = f"Erreur: {error}"
                    except:
                        details = f"Status {response.status_code}"
                
                self.add_result(test_case["name"], success, response.status_code, details)
            except Exception as e:
                self.add_result(test_case["name"], False, None, f"Exception: {str(e)[:50]}")
    
    def test_login_failures(self):
        """Tests de connexion échouée"""
        test_cases = [
            {"name": "Mauvais mot de passe", "data": {"username": "admin", "password": "wrong"}, "expected": 401},
            {"name": "Utilisateur inexistant", "data": {"username": "inexistant", "password": "password123"}, "expected": 401},
            {"name": "Username vide", "data": {"username": "", "password": "password123"}, "expected": 400},
            {"name": "Mot de passe vide", "data": {"username": "admin", "password": ""}, "expected": 400},
            {"name": "Champs manquants", "data": {"username": "admin"}, "expected": 400},
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/login",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                success = response.status_code == test_case["expected"]
                details = ""
                
                if response.status_code < 500:
                    try:
                        error = response.json().get("error", "")
                        details = error if error else f"Status {response.status_code}"
                    except:
                        details = f"Status {response.status_code}"
                else:
                    details = f"Erreur serveur {response.status_code}"
                
                self.add_result(test_case["name"], success, response.status_code, details)
            except Exception as e:
                self.add_result(test_case["name"], False, None, f"Exception: {str(e)[:50]}")
    
    def test_register_success(self):
        """Tests d'inscription réussie"""
        timestamp = int(datetime.now().timestamp())
        
        test_cases = [
            {
                "name": "Inscription étudiant",
                "data": {
                    "username": f"etudiant_test_{timestamp}",
                    "email": f"etudiant_test_{timestamp}@test.com",
                    "password": "password123",
                    "nom": "Test",
                    "prenom": "Étudiant",
                    "role": "etudiant"
                }
            },
            {
                "name": "Inscription parent",
                "data": {
                    "username": f"parent_test_{timestamp}",
                    "email": f"parent_test_{timestamp}@test.com",
                    "password": "password123",
                    "nom": "Test",
                    "prenom": "Parent",
                    "role": "parent"
                }
            },
            {
                "name": "Inscription enseignant",
                "data": {
                    "username": f"enseignant_test_{timestamp}",
                    "email": f"enseignant_test_{timestamp}@test.com",
                    "password": "password123",
                    "nom": "Test",
                    "prenom": "Enseignant",
                    "role": "enseignant"
                }
            },
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/register",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                success = response.status_code == 201
                details = ""
                
                if success:
                    try:
                        data = response.json()
                        self.created_users.append(test_case["data"]["username"])
                        details = f"Utilisateur créé: {test_case['data']['username']}"
                    except:
                        details = "Utilisateur créé"
                else:
                    try:
                        error = response.json().get("error", "")
                        error_details = response.json().get("details", [])
                        details = f"{error}" + (f" - {error_details}" if error_details else "")
                    except:
                        details = f"Status {response.status_code}"
                
                self.add_result(test_case["name"], success, response.status_code, details)
            except Exception as e:
                self.add_result(test_case["name"], False, None, f"Exception: {str(e)[:50]}")
    
    def test_register_failures(self):
        """Tests d'inscription échouée"""
        timestamp = int(datetime.now().timestamp())
        
        test_cases = [
            {
                "name": "Username déjà utilisé",
                "data": {
                    "username": "admin",
                    "email": f"new_{timestamp}@test.com",
                    "password": "password123",
                    "nom": "Test",
                    "prenom": "User",
                    "role": "etudiant"
                },
                "expected": 400
            },
            {
                "name": "Email déjà utilisé",
                "data": {
                    "username": f"new_{timestamp}",
                    "email": "admin@esa.tg",
                    "password": "password123",
                    "nom": "Test",
                    "prenom": "User",
                    "role": "etudiant"
                },
                "expected": 400
            },
            {
                "name": "Email invalide",
                "data": {
                    "username": f"invalid_email_{timestamp}",
                    "email": "email-invalide",
                    "password": "password123",
                    "nom": "Test",
                    "prenom": "User",
                    "role": "etudiant"
                },
                "expected": 400
            },
            {
                "name": "Mot de passe trop court",
                "data": {
                    "username": f"short_pwd_{timestamp}",
                    "email": f"short_pwd_{timestamp}@test.com",
                    "password": "12345",
                    "nom": "Test",
                    "prenom": "User",
                    "role": "etudiant"
                },
                "expected": 400
            },
            {
                "name": "Champs obligatoires manquants",
                "data": {
                    "username": f"missing_{timestamp}",
                    "email": f"missing_{timestamp}@test.com",
                    "password": "password123",
                    "role": "etudiant"
                },
                "expected": 400
            },
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/register",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                success = response.status_code == test_case["expected"]
                details = ""
                
                if response.status_code < 500:
                    try:
                        error = response.json().get("error", "")
                        details = error if error else f"Status {response.status_code}"
                    except:
                        details = f"Status {response.status_code}"
                else:
                    details = f"Erreur serveur {response.status_code}"
                
                self.add_result(test_case["name"], success, response.status_code, details)
            except Exception as e:
                self.add_result(test_case["name"], False, None, f"Exception: {str(e)[:50]}")
    
    def test_password_validation(self):
        """Tests de validation des mots de passe"""
        timestamp = int(datetime.now().timestamp())
        
        passwords = [
            {"name": "password123 (dev)", "password": "password123", "should_accept": True},
            {"name": "Mot de passe fort", "password": "StrongP@ss123", "should_accept": True},
            {"name": "Trop court", "password": "12345", "should_accept": False},
            {"name": "Sans majuscule", "password": "password123!", "should_accept": False},
            {"name": "Sans chiffre", "password": "Password!", "should_accept": False},
            {"name": "Sans caractère spécial", "password": "Password123", "should_accept": False},
        ]
        
        for pwd_test in passwords:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/register",
                    json={
                        "username": f"pwd_test_{timestamp}_{pwd_test['name'].replace(' ', '_').replace('(', '').replace(')', '')}",
                        "email": f"pwd_test_{timestamp}_{pwd_test['name'].replace(' ', '_').replace('(', '').replace(')', '')}@test.com",
                        "password": pwd_test["password"],
                        "nom": "Test",
                        "prenom": "Password",
                        "role": "etudiant"
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                success = (response.status_code == 201) == pwd_test["should_accept"]
                details = ""
                
                if response.status_code == 400:
                    try:
                        error = response.json().get("error", "")
                        error_details = response.json().get("details", [])
                        details = f"{error}" + (f" - {error_details[:1]}" if error_details else "")
                    except:
                        details = f"Status {response.status_code}"
                elif response.status_code == 201:
                    details = "Accepté"
                else:
                    details = f"Status {response.status_code}"
                
                self.add_result(pwd_test["name"], success, response.status_code, details)
                timestamp += 1
            except Exception as e:
                self.add_result(pwd_test["name"], False, None, f"Exception: {str(e)[:50]}")
    
    def test_token_validation(self):
        """Tests de validation des tokens"""
        if not self.tokens:
            self.add_result("Validation token (pas de token)", False, None, "Aucun token disponible")
            return
        
        token = list(self.tokens.values())[0]
        
        # Test avec token valide
        try:
            response = requests.get(
                f"{BASE_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            self.add_result("Accès avec token valide", response.status_code == 200, response.status_code, 
                          "OK" if response.status_code == 200 else "Échec")
        except Exception as e:
            self.add_result("Accès avec token valide", False, None, f"Exception: {str(e)[:50]}")
        
        # Test avec token invalide
        try:
            response = requests.get(
                f"{BASE_URL}/auth/me",
                headers={"Authorization": "Bearer token_invalide"},
                timeout=10
            )
            self.add_result("Accès avec token invalide", response.status_code == 401, response.status_code,
                          "Rejeté correctement" if response.status_code == 401 else "Non rejeté")
        except Exception as e:
            self.add_result("Accès avec token invalide", False, None, f"Exception: {str(e)[:50]}")
    
    def generate_report(self) -> str:
        """Génère un rapport détaillé en format tableau"""
        report = []
        report.append("=" * 100)
        report.append("RAPPORT DES TESTS D'AUTHENTIFICATION")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 100)
        report.append("")
        
        # Statistiques
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        report.append(f"📊 STATISTIQUES GÉNÉRALES")
        report.append(f"   Total des tests: {total}")
        report.append(f"   ✅ Réussis: {passed}")
        report.append(f"   ❌ Échoués: {failed}")
        report.append(f"   📈 Taux de réussite: {success_rate:.1f}%")
        report.append("")
        
        # Tableau détaillé
        report.append("=" * 100)
        report.append("TABLEAU DÉTAILLÉ DES TESTS")
        report.append("=" * 100)
        report.append("")
        
        # En-tête du tableau
        header = f"{'Test':<50} | {'Status':<8} | {'Code':<6} | {'Détails'}"
        report.append(header)
        report.append("-" * 100)
        
        # Groupes de tests
        groups = {
            "CONNEXION - Réussie": [],
            "CONNEXION - Échouée": [],
            "INSCRIPTION - Réussie": [],
            "INSCRIPTION - Échouée": [],
            "VALIDATION MOT DE PASSE": [],
            "VALIDATION TOKEN": []
        }
        
        current_group = None
        for result in self.results:
            # Déterminer le groupe
            if "Login" in result.name and result.success:
                current_group = "CONNEXION - Réussie"
            elif "Login" in result.name and not result.success:
                current_group = "CONNEXION - Échouée"
            elif "Inscription" in result.name and result.success:
                current_group = "INSCRIPTION - Réussie"
            elif "Inscription" in result.name and not result.success:
                current_group = "INSCRIPTION - Échouée"
            elif "password" in result.name.lower() or "Mot de passe" in result.name:
                current_group = "VALIDATION MOT DE PASSE"
            elif "token" in result.name.lower() or "Token" in result.name:
                current_group = "VALIDATION TOKEN"
            
            if current_group:
                groups[current_group].append(result)
        
        # Afficher chaque groupe
        for group_name, results in groups.items():
            if results:
                report.append("")
                report.append(f"📋 {group_name}")
                report.append("-" * 100)
                for result in results:
                    status_icon = "✅ PASS" if result.success else "❌ FAIL"
                    status_code_str = str(result.status_code) if result.status_code else "N/A"
                    details_short = result.details[:40] if result.details else ""
                    row = f"{result.name:<50} | {status_icon:<8} | {status_code_str:<6} | {details_short}"
                    report.append(row)
        
        report.append("")
        report.append("=" * 100)
        report.append("RÉSUMÉ PAR CATÉGORIE")
        report.append("=" * 100)
        report.append("")
        
        for group_name, results in groups.items():
            if results:
                group_total = len(results)
                group_passed = sum(1 for r in results if r.success)
                group_rate = (group_passed / group_total * 100) if group_total > 0 else 0
                report.append(f"{group_name:<40} : {group_passed}/{group_total} ({group_rate:.1f}%)")
        
        report.append("")
        report.append("=" * 100)
        
        return "\n".join(report)
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🔍 Vérification du serveur...")
        if not self.test_server_health():
            print("❌ Serveur non accessible. Démarrez-le avec: python3 app.py")
            return False
        
        print("✅ Serveur accessible\n")
        
        print("🧪 Exécution des tests...")
        print("   - Tests de connexion réussie...")
        self.test_login_success()
        
        print("   - Tests de connexion échouée...")
        self.test_login_failures()
        
        print("   - Tests d'inscription réussie...")
        self.test_register_success()
        
        print("   - Tests d'inscription échouée...")
        self.test_register_failures()
        
        print("   - Tests de validation des mots de passe...")
        self.test_password_validation()
        
        print("   - Tests de validation des tokens...")
        self.test_token_validation()
        
        print("\n✅ Tous les tests sont terminés\n")
        return True

def main():
    runner = AuthTestRunner()
    
    if runner.run_all_tests():
        report = runner.generate_report()
        print(report)
        
        # Sauvegarder le rapport
        import os
        report_dir = os.path.dirname(os.path.abspath(__file__))
        report_file = os.path.join(report_dir, f"rapport_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 Rapport sauvegardé dans: {report_file}")
    else:
        print("❌ Impossible d'exécuter les tests")

if __name__ == "__main__":
    main()

