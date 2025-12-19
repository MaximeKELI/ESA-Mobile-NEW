"""
Tests spécifiques de connexion et inscription
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(title):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}  {title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")

def print_result(test_name, success, details=""):
    icon = f"{Colors.GREEN}✅{Colors.RESET}" if success else f"{Colors.RED}❌{Colors.RESET}"
    print(f"{icon} {test_name}")
    if details:
        print(f"   {details}")

def test_connection():
    """Tests de connexion"""
    print_header("TESTS DE CONNEXION")
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    # Test 1: Login admin avec username
    results["total"] += 1
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "password123"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        success = response.status_code == 200
        if success:
            data = response.json()
            has_token = "access_token" in data
            details = f"Status {response.status_code}" + (f" - Token obtenu" if has_token else " - Pas de token")
            results["passed"] += 1
        else:
            error = response.json().get("error", "") if response.status_code < 500 else "Erreur serveur"
            details = f"Status {response.status_code} - {error}"
            results["failed"] += 1
        print_result("Login admin (username)", success, details)
        results["details"].append({"test": "Login admin (username)", "success": success, "status": response.status_code, "details": details})
    except Exception as e:
        results["failed"] += 1
        print_result("Login admin (username)", False, f"Exception: {str(e)[:50]}")
        results["details"].append({"test": "Login admin (username)", "success": False, "status": None, "details": f"Exception: {str(e)[:50]}"})
    
    # Test 2: Login admin avec email
    results["total"] += 1
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin@esa.tg", "password": "password123"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        success = response.status_code == 200
        if success:
            data = response.json()
            has_token = "access_token" in data
            details = f"Status {response.status_code}" + (f" - Token obtenu" if has_token else " - Pas de token")
            results["passed"] += 1
        else:
            error = response.json().get("error", "") if response.status_code < 500 else "Erreur serveur"
            details = f"Status {response.status_code} - {error}"
            results["failed"] += 1
        print_result("Login admin (email)", success, details)
        results["details"].append({"test": "Login admin (email)", "success": success, "status": response.status_code, "details": details})
    except Exception as e:
        results["failed"] += 1
        print_result("Login admin (email)", False, f"Exception: {str(e)[:50]}")
        results["details"].append({"test": "Login admin (email)", "success": False, "status": None, "details": f"Exception: {str(e)[:50]}"})
    
    # Test 3: Mauvais mot de passe
    results["total"] += 1
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "wrongpassword"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        success = response.status_code == 401
        error = response.json().get("error", "") if response.status_code < 500 else "Erreur serveur"
        details = f"Status {response.status_code}" + (f" - {error}" if error else "")
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print_result("Mauvais mot de passe", success, details)
        results["details"].append({"test": "Mauvais mot de passe", "success": success, "status": response.status_code, "details": details})
    except Exception as e:
        results["failed"] += 1
        print_result("Mauvais mot de passe", False, f"Exception: {str(e)[:50]}")
        results["details"].append({"test": "Mauvais mot de passe", "success": False, "status": None, "details": f"Exception: {str(e)[:50]}"})
    
    # Test 4: Utilisateur inexistant
    results["total"] += 1
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "inexistant", "password": "password123"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        success = response.status_code == 401
        error = response.json().get("error", "") if response.status_code < 500 else "Erreur serveur"
        details = f"Status {response.status_code}" + (f" - {error}" if error else "")
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print_result("Utilisateur inexistant", success, details)
        results["details"].append({"test": "Utilisateur inexistant", "success": success, "status": response.status_code, "details": details})
    except Exception as e:
        results["failed"] += 1
        print_result("Utilisateur inexistant", False, f"Exception: {str(e)[:50]}")
        results["details"].append({"test": "Utilisateur inexistant", "success": False, "status": None, "details": f"Exception: {str(e)[:50]}"})
    
    # Test 5: Champs manquants
    results["total"] += 1
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        success = response.status_code == 400
        error = response.json().get("error", "") if response.status_code < 500 else "Erreur serveur"
        details = f"Status {response.status_code}" + (f" - {error}" if error else "")
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print_result("Champs manquants", success, details)
        results["details"].append({"test": "Champs manquants", "success": success, "status": response.status_code, "details": details})
    except Exception as e:
        results["failed"] += 1
        print_result("Champs manquants", False, f"Exception: {str(e)[:50]}")
        results["details"].append({"test": "Champs manquants", "success": False, "status": None, "details": f"Exception: {str(e)[:50]}"})
    
    return results

def test_inscription():
    """Tests d'inscription"""
    print_header("TESTS D'INSCRIPTION")
    
    results = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "details": []
    }
    
    timestamp = int(datetime.now().timestamp())
    
    # Test 1: Inscription étudiant
    results["total"] += 1
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": f"etudiant_test_{timestamp}",
                "email": f"etudiant_test_{timestamp}@test.com",
                "password": "password123",
                "nom": "Test",
                "prenom": "Étudiant",
                "role": "etudiant"
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        success = response.status_code == 201
        if success:
            data = response.json()
            details = f"Status {response.status_code} - Utilisateur créé"
            results["passed"] += 1
        else:
            error = response.json().get("error", "") if response.status_code < 500 else "Erreur serveur"
            error_details = response.json().get("details", [])
            details = f"Status {response.status_code} - {error}" + (f" - {error_details}" if error_details else "")
            results["failed"] += 1
        print_result("Inscription étudiant", success, details)
        results["details"].append({"test": "Inscription étudiant", "success": success, "status": response.status_code, "details": details})
    except Exception as e:
        results["failed"] += 1
        print_result("Inscription étudiant", False, f"Exception: {str(e)[:50]}")
        results["details"].append({"test": "Inscription étudiant", "success": False, "status": None, "details": f"Exception: {str(e)[:50]}"})
    
    # Test 2: Inscription parent
    results["total"] += 1
    timestamp += 1
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": f"parent_test_{timestamp}",
                "email": f"parent_test_{timestamp}@test.com",
                "password": "password123",
                "nom": "Test",
                "prenom": "Parent",
                "role": "parent"
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        success = response.status_code == 201
        if success:
            data = response.json()
            details = f"Status {response.status_code} - Utilisateur créé"
            results["passed"] += 1
        else:
            error = response.json().get("error", "") if response.status_code < 500 else "Erreur serveur"
            error_details = response.json().get("details", [])
            details = f"Status {response.status_code} - {error}" + (f" - {error_details}" if error_details else "")
            results["failed"] += 1
        print_result("Inscription parent", success, details)
        results["details"].append({"test": "Inscription parent", "success": success, "status": response.status_code, "details": details})
    except Exception as e:
        results["failed"] += 1
        print_result("Inscription parent", False, f"Exception: {str(e)[:50]}")
        results["details"].append({"test": "Inscription parent", "success": False, "status": None, "details": f"Exception: {str(e)[:50]}"})
    
    # Test 3: Username déjà utilisé
    results["total"] += 1
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": "admin",  # Déjà existant
                "email": f"new_{timestamp}@test.com",
                "password": "password123",
                "nom": "Test",
                "prenom": "User",
                "role": "etudiant"
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        success = response.status_code == 400
        error = response.json().get("error", "") if response.status_code < 500 else "Erreur serveur"
        details = f"Status {response.status_code}" + (f" - {error}" if error else "")
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print_result("Username déjà utilisé", success, details)
        results["details"].append({"test": "Username déjà utilisé", "success": success, "status": response.status_code, "details": details})
    except Exception as e:
        results["failed"] += 1
        print_result("Username déjà utilisé", False, f"Exception: {str(e)[:50]}")
        results["details"].append({"test": "Username déjà utilisé", "success": False, "status": None, "details": f"Exception: {str(e)[:50]}"})
    
    # Test 4: Email invalide
    results["total"] += 1
    timestamp += 1
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": f"invalid_email_{timestamp}",
                "email": "email-invalide",
                "password": "password123",
                "nom": "Test",
                "prenom": "User",
                "role": "etudiant"
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        success = response.status_code == 400
        error = response.json().get("error", "") if response.status_code < 500 else "Erreur serveur"
        details = f"Status {response.status_code}" + (f" - {error}" if error else "")
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print_result("Email invalide", success, details)
        results["details"].append({"test": "Email invalide", "success": success, "status": response.status_code, "details": details})
    except Exception as e:
        results["failed"] += 1
        print_result("Email invalide", False, f"Exception: {str(e)[:50]}")
        results["details"].append({"test": "Email invalide", "success": False, "status": None, "details": f"Exception: {str(e)[:50]}"})
    
    # Test 5: Champs obligatoires manquants
    results["total"] += 1
    timestamp += 1
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": f"missing_{timestamp}",
                "email": f"missing_{timestamp}@test.com",
                "password": "password123",
                "role": "etudiant"
                # nom et prenom manquants
            },
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        success = response.status_code == 400
        error = response.json().get("error", "") if response.status_code < 500 else "Erreur serveur"
        details = f"Status {response.status_code}" + (f" - {error}" if error else "")
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
        print_result("Champs obligatoires manquants", success, details)
        results["details"].append({"test": "Champs obligatoires manquants", "success": success, "status": response.status_code, "details": details})
    except Exception as e:
        results["failed"] += 1
        print_result("Champs obligatoires manquants", False, f"Exception: {str(e)[:50]}")
        results["details"].append({"test": "Champs obligatoires manquants", "success": False, "status": None, "details": f"Exception: {str(e)[:50]}"})
    
    return results

def generate_report(connection_results, inscription_results):
    """Génère un rapport détaillé"""
    print_header("RAPPORT DÉTAILLÉ")
    
    total_tests = connection_results["total"] + inscription_results["total"]
    total_passed = connection_results["passed"] + inscription_results["passed"]
    total_failed = connection_results["failed"] + inscription_results["failed"]
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 STATISTIQUES GÉNÉRALES")
    print(f"   Total des tests: {total_tests}")
    print(f"   ✅ Réussis: {total_passed}")
    print(f"   ❌ Échoués: {total_failed}")
    print(f"   📈 Taux de réussite: {success_rate:.1f}%")
    
    print(f"\n📋 CONNEXION")
    print(f"   Total: {connection_results['total']}")
    print(f"   ✅ Réussis: {connection_results['passed']}")
    print(f"   ❌ Échoués: {connection_results['failed']}")
    print(f"   Taux: {(connection_results['passed']/connection_results['total']*100) if connection_results['total'] > 0 else 0:.1f}%")
    
    print(f"\n📋 INSCRIPTION")
    print(f"   Total: {inscription_results['total']}")
    print(f"   ✅ Réussis: {inscription_results['passed']}")
    print(f"   ❌ Échoués: {inscription_results['failed']}")
    print(f"   Taux: {(inscription_results['passed']/inscription_results['total']*100) if inscription_results['total'] > 0 else 0:.1f}%")
    
    print(f"\n📋 TABLEAU DÉTAILLÉ")
    print(f"{'Test':<40} | {'Status':<8} | {'Code':<6} | {'Détails'}")
    print("-" * 80)
    
    for detail in connection_results["details"]:
        status_icon = "✅ PASS" if detail["success"] else "❌ FAIL"
        status_code = str(detail["status"]) if detail["status"] else "N/A"
        print(f"{detail['test']:<40} | {status_icon:<8} | {status_code:<6} | {detail['details'][:40]}")
    
    for detail in inscription_results["details"]:
        status_icon = "✅ PASS" if detail["success"] else "❌ FAIL"
        status_code = str(detail["status"]) if detail["status"] else "N/A"
        print(f"{detail['test']:<40} | {status_icon:<8} | {status_code:<6} | {detail['details'][:40]}")
    
    return {
        "total": total_tests,
        "passed": total_passed,
        "failed": total_failed,
        "success_rate": success_rate,
        "connection": connection_results,
        "inscription": inscription_results
    }

def main():
    print(f"\n{Colors.YELLOW}{'='*70}{Colors.RESET}")
    print(f"{Colors.YELLOW}  TESTS DE CONNEXION ET INSCRIPTION{Colors.RESET}")
    print(f"{Colors.YELLOW}  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(f"{Colors.YELLOW}{'='*70}{Colors.RESET}")
    
    # Vérifier que le serveur est accessible en testant directement le login
    try:
        test_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "test", "password": "test"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        # Si on obtient une réponse (même 401), le serveur est accessible
        print(f"{Colors.GREEN}✅ Serveur accessible{Colors.RESET}\n")
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ Serveur non accessible. Démarrez-le avec: python3 app.py{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Assurez-vous que le serveur tourne sur http://localhost:5000{Colors.RESET}")
        return
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Erreur lors de la vérification: {e}{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 Continuons les tests quand même...{Colors.RESET}\n")
    
    # Exécuter les tests
    connection_results = test_connection()
    inscription_results = test_inscription()
    
    # Générer le rapport
    report = generate_report(connection_results, inscription_results)
    
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}  Tests terminés !{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

if __name__ == "__main__":
    main()

