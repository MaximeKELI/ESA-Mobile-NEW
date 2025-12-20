"""
Tests finaux avec génération de rapport en tableau
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def wait_for_server(max_attempts=5, delay=2):
    """Attend que le serveur soit accessible"""
    for i in range(max_attempts):
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "test", "password": "test"},
                headers={"Content-Type": "application/json"},
                timeout=3
            )
            return True
        except:
            if i < max_attempts - 1:
                time.sleep(delay)
            else:
                return False
    return False

def test_connection():
    """Tests de connexion"""
    results = []
    
    test_cases = [
        {"name": "Login admin (username)", "data": {"username": "admin", "password": "password123"}, "expected": 200},
        {"name": "Login admin (email)", "data": {"username": "admin@esa.tg", "password": "password123"}, "expected": 200},
        {"name": "Login comptable", "data": {"username": "comptable", "password": "password123"}, "expected": 200},
        {"name": "Login enseignant", "data": {"username": "enseignant1", "password": "password123"}, "expected": 200},
        {"name": "Login étudiant", "data": {"username": "etudiant1", "password": "password123"}, "expected": 200},
        {"name": "Login parent", "data": {"username": "parent1", "password": "password123"}, "expected": 200},
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
            
            if success and response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    details = "Token obtenu"
                else:
                    details = "Token manquant"
            elif response.status_code < 500:
                try:
                    error = response.json().get("error", "")
                    details = error if error else f"Status {response.status_code}"
                except:
                    details = f"Status {response.status_code}"
            else:
                details = f"Erreur serveur {response.status_code}"
            
            results.append({
                "category": "CONNEXION",
                "test": test_case["name"],
                "success": success,
                "status": response.status_code,
                "details": details
            })
        except Exception as e:
            results.append({
                "category": "CONNEXION",
                "test": test_case["name"],
                "success": False,
                "status": None,
                "details": f"Exception: {str(e)[:50]}"
            })
    
    return results

def test_inscription():
    """Tests d'inscription"""
    results = []
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
            },
            "expected": 201
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
            },
            "expected": 201
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
            },
            "expected": 201
        },
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
            
            if success and response.status_code == 201:
                try:
                    data = response.json()
                    user_data = data.get('user', {})
                    details = f"Role: {user_data.get('role')}, Active: {user_data.get('is_active')}"
                except:
                    details = "Utilisateur créé"
            elif response.status_code < 500:
                try:
                    error = response.json().get("error", "")
                    error_details = response.json().get("details", [])
                    details = f"{error}" + (f" - {error_details}" if error_details else "")
                except:
                    details = f"Status {response.status_code}"
            else:
                details = f"Erreur serveur {response.status_code}"
            
            results.append({
                "category": "INSCRIPTION",
                "test": test_case["name"],
                "success": success,
                "status": response.status_code,
                "details": details
            })
            
            timestamp += 1
        except Exception as e:
            results.append({
                "category": "INSCRIPTION",
                "test": test_case["name"],
                "success": False,
                "status": None,
                "details": f"Exception: {str(e)[:50]}"
            })
    
    return results

def generate_table_report(all_results):
    """Génère un rapport en format tableau"""
    total = len(all_results)
    passed = sum(1 for r in all_results if r["success"])
    failed = total - passed
    success_rate = (passed / total * 100) if total > 0 else 0
    
    # Par catégorie
    categories = {}
    for result in all_results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0, "failed": 0}
        categories[cat]["total"] += 1
        if result["success"]:
            categories[cat]["passed"] += 1
        else:
            categories[cat]["failed"] += 1
    
    report = []
    report.append("=" * 120)
    report.append("BILAN DES TESTS D'AUTHENTIFICATION")
    report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 120)
    report.append("")
    
    # Statistiques générales
    report.append("📊 STATISTIQUES GÉNÉRALES")
    report.append("-" * 120)
    report.append(f"Total des tests        : {total}")
    report.append(f"✅ Réussis             : {passed}")
    report.append(f"❌ Échoués             : {failed}")
    report.append(f"📈 Taux de réussite    : {success_rate:.1f}%")
    report.append("")
    
    # Statistiques par catégorie
    report.append("📊 STATISTIQUES PAR CATÉGORIE")
    report.append("-" * 120)
    report.append(f"{'Catégorie':<20} | {'Total':<8} | {'Réussis':<8} | {'Échoués':<8} | {'Taux':<10}")
    report.append("-" * 120)
    for cat, stats in categories.items():
        rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        report.append(f"{cat:<20} | {stats['total']:<8} | {stats['passed']:<8} | {stats['failed']:<8} | {rate:>6.1f}%")
    report.append("")
    
    # Tableau détaillé
    report.append("📋 TABLEAU DÉTAILLÉ DES TESTS")
    report.append("-" * 120)
    report.append(f"{'Catégorie':<15} | {'Test':<45} | {'Résultat':<10} | {'Code':<6} | {'Détails'}")
    report.append("-" * 120)
    
    for result in all_results:
        status_icon = "✅ PASS" if result["success"] else "❌ FAIL"
        status_code = str(result["status"]) if result["status"] else "N/A"
        details_short = result["details"][:30] if result["details"] else ""
        report.append(f"{result['category']:<15} | {result['test']:<45} | {status_icon:<10} | {status_code:<6} | {details_short}")
    
    report.append("")
    report.append("=" * 120)
    
    return "\n".join(report)

def main():
    print("🔍 Vérification du serveur...")
    if not wait_for_server():
        print("❌ Serveur non accessible après plusieurs tentatives.")
        print("💡 Assurez-vous que le serveur tourne: python3 app.py")
        return
    
    print("✅ Serveur accessible\n")
    print("🧪 Exécution des tests...\n")
    
    # Exécuter les tests
    connection_results = test_connection()
    inscription_results = test_inscription()
    
    all_results = connection_results + inscription_results
    
    # Générer le rapport
    report = generate_table_report(all_results)
    print(report)
    
    # Sauvegarder
    import os
    report_dir = os.path.dirname(os.path.abspath(__file__))
    report_file = os.path.join(report_dir, f"BILAN_TESTS_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n📄 Rapport sauvegardé: {report_file}")

if __name__ == "__main__":
    main()


