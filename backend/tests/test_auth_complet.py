"""
Tests complets d'authentification (connexion et inscription)
Tous les scénarios possibles
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

def print_test(title):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}  {title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}")

def print_result(test_name, success, details=""):
    icon = f"{Colors.GREEN}✅{Colors.RESET}" if success else f"{Colors.RED}❌{Colors.RESET}"
    print(f"{icon} {test_name}")
    if details:
        print(f"   {details}")

def test_login_success():
    """Tests de connexion réussie"""
    print_test("TESTS DE CONNEXION RÉUSSIE")
    
    test_cases = [
        {
            "name": "Login admin avec username",
            "data": {"username": "admin", "password": "password123"},
            "expected_status": 200
        },
        {
            "name": "Login admin avec email",
            "data": {"username": "admin@esa.tg", "password": "password123"},
            "expected_status": 200
        },
        {
            "name": "Login comptable",
            "data": {"username": "comptable", "password": "password123"},
            "expected_status": 200
        },
        {
            "name": "Login enseignant",
            "data": {"username": "enseignant1", "password": "password123"},
            "expected_status": 200
        },
        {
            "name": "Login étudiant",
            "data": {"username": "etudiant1", "password": "password123"},
            "expected_status": 200
        },
        {
            "name": "Login parent",
            "data": {"username": "parent1", "password": "password123"},
            "expected_status": 200
        },
    ]
    
    tokens = {}
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == test_case["expected_status"]
            
            if success:
                data = response.json()
                if "access_token" in data:
                    tokens[test_case["data"]["username"]] = data["access_token"]
                    print_result(
                        test_case["name"],
                        True,
                        f"Token obtenu: {data['access_token'][:30]}..."
                    )
                else:
                    print_result(test_case["name"], False, "Token manquant dans la réponse")
            else:
                print_result(
                    test_case["name"],
                    False,
                    f"Status {response.status_code} au lieu de {test_case['expected_status']}"
                )
        except Exception as e:
            print_result(test_case["name"], False, f"Erreur: {e}")
    
    return tokens

def test_login_failures():
    """Tests de connexion échouée"""
    print_test("TESTS DE CONNEXION ÉCHOUÉE")
    
    test_cases = [
        {
            "name": "Mauvais mot de passe",
            "data": {"username": "admin", "password": "wrongpassword"},
            "expected_status": 401
        },
        {
            "name": "Utilisateur inexistant",
            "data": {"username": "inexistant", "password": "password123"},
            "expected_status": 401
        },
        {
            "name": "Username vide",
            "data": {"username": "", "password": "password123"},
            "expected_status": 400
        },
        {
            "name": "Mot de passe vide",
            "data": {"username": "admin", "password": ""},
            "expected_status": 400
        },
        {
            "name": "Champs manquants",
            "data": {"username": "admin"},
            "expected_status": 400
        },
        {
            "name": "Données invalides (null)",
            "data": None,
            "expected_status": 400
        },
    ]
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json=test_case["data"] if test_case["data"] else {},
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == test_case["expected_status"]
            error_msg = response.json().get("error", "") if response.status_code < 500 else ""
            
            print_result(
                test_case["name"],
                success,
                f"Status {response.status_code}" + (f" - {error_msg}" if error_msg else "")
            )
        except Exception as e:
            print_result(test_case["name"], False, f"Erreur: {e}")

def test_register_success():
    """Tests d'inscription réussie"""
    print_test("TESTS D'INSCRIPTION RÉUSSIE")
    
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
            "expected_status": 201
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
            "expected_status": 201
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
            "expected_status": 201
        },
        {
            "name": "Inscription avec téléphone et adresse",
            "data": {
                "username": f"complet_test_{timestamp}",
                "email": f"complet_test_{timestamp}@test.com",
                "password": "password123",
                "nom": "Test",
                "prenom": "Complet",
                "role": "parent",
                "telephone": "+22890123456",
                "adresse": "Lomé, Togo"
            },
            "expected_status": 201
        },
    ]
    
    created_users = []
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == test_case["expected_status"]
            
            if success:
                data = response.json()
                created_users.append(test_case["data"]["username"])
                print_result(
                    test_case["name"],
                    True,
                    f"Utilisateur créé: {data.get('user', {}).get('username', 'N/A')}"
                )
            else:
                error = response.json().get("error", "Erreur inconnue")
                print_result(
                    test_case["name"],
                    False,
                    f"Status {response.status_code} - {error}"
                )
        except Exception as e:
            print_result(test_case["name"], False, f"Erreur: {e}")
    
    return created_users

def test_register_failures():
    """Tests d'inscription échouée"""
    print_test("TESTS D'INSCRIPTION ÉCHOUÉE")
    
    timestamp = int(datetime.now().timestamp())
    
    test_cases = [
        {
            "name": "Username déjà utilisé",
            "data": {
                "username": "admin",  # Déjà existant
                "email": f"new_{timestamp}@test.com",
                "password": "password123",
                "nom": "Test",
                "prenom": "User",
                "role": "etudiant"
            },
            "expected_status": 400
        },
        {
            "name": "Email déjà utilisé",
            "data": {
                "username": f"new_{timestamp}",
                "email": "admin@esa.tg",  # Déjà existant
                "password": "password123",
                "nom": "Test",
                "prenom": "User",
                "role": "etudiant"
            },
            "expected_status": 400
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
            "expected_status": 400
        },
        {
            "name": "Mot de passe trop court",
            "data": {
                "username": f"short_pwd_{timestamp}",
                "email": f"short_pwd_{timestamp}@test.com",
                "password": "12345",  # Trop court
                "nom": "Test",
                "prenom": "User",
                "role": "etudiant"
            },
            "expected_status": 400
        },
        {
            "name": "Champs obligatoires manquants",
            "data": {
                "username": f"missing_{timestamp}",
                "email": f"missing_{timestamp}@test.com",
                "password": "password123",
                # Nom et prénom manquants
                "role": "etudiant"
            },
            "expected_status": 400
        },
        {
            "name": "Rôle invalide",
            "data": {
                "username": f"invalid_role_{timestamp}",
                "email": f"invalid_role_{timestamp}@test.com",
                "password": "password123",
                "nom": "Test",
                "prenom": "User",
                "role": "role_inexistant"
            },
            "expected_status": 400
        },
        {
            "name": "Username trop court",
            "data": {
                "username": "ab",  # Trop court
                "email": f"short_user_{timestamp}@test.com",
                "password": "password123",
                "nom": "Test",
                "prenom": "User",
                "role": "etudiant"
            },
            "expected_status": 400
        },
    ]
    
    for test_case in test_cases:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=test_case["data"],
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == test_case["expected_status"]
            error_msg = response.json().get("error", "") if response.status_code < 500 else ""
            
            print_result(
                test_case["name"],
                success,
                f"Status {response.status_code}" + (f" - {error_msg}" if error_msg else "")
            )
        except Exception as e:
            print_result(test_case["name"], False, f"Erreur: {e}")

def test_password_validation():
    """Tests de validation des mots de passe"""
    print_test("TESTS DE VALIDATION DES MOTS DE PASSE")
    
    timestamp = int(datetime.now().timestamp())
    
    passwords = [
        {
            "name": "password123 (dev)",
            "password": "password123",
            "should_accept": True
        },
        {
            "name": "Mot de passe fort",
            "password": "StrongP@ss123",
            "should_accept": True
        },
        {
            "name": "Trop court",
            "password": "12345",
            "should_accept": False
        },
        {
            "name": "Sans majuscule",
            "password": "password123!",
            "should_accept": False
        },
        {
            "name": "Sans chiffre",
            "password": "Password!",
            "should_accept": False
        },
        {
            "name": "Sans caractère spécial",
            "password": "Password123",
            "should_accept": False
        },
    ]
    
    for pwd_test in passwords:
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json={
                    "username": f"pwd_test_{timestamp}_{pwd_test['name'].replace(' ', '_')}",
                    "email": f"pwd_test_{timestamp}_{pwd_test['name'].replace(' ', '_')}@test.com",
                    "password": pwd_test["password"],
                    "nom": "Test",
                    "prenom": "Password",
                    "role": "etudiant"
                },
                headers={"Content-Type": "application/json"}
            )
            
            success = (response.status_code == 201) == pwd_test["should_accept"]
            
            if response.status_code == 400:
                error = response.json().get("error", "")
                details = response.json().get("details", [])
                error_msg = f"{error}" + (f" - {details}" if details else "")
            else:
                error_msg = ""
            
            print_result(
                pwd_test["name"],
                success,
                f"Status {response.status_code}" + (f" - {error_msg}" if error_msg else "")
            )
            
            timestamp += 1  # Pour éviter les conflits
        except Exception as e:
            print_result(pwd_test["name"], False, f"Erreur: {e}")

def test_rate_limiting():
    """Tests de rate limiting"""
    print_test("TESTS DE RATE LIMITING")
    
    print("Tentative de 10 connexions avec mauvais mot de passe...")
    
    for i in range(10):
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "admin", "password": "wrongpassword"},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 429:
                print_result(
                    f"Tentative {i+1} - Rate limit activé",
                    True,
                    f"Status 429 après {i+1} tentatives"
                )
                break
            elif i == 9:
                print_result(
                    "Rate limiting",
                    False,
                    "Rate limit non activé après 10 tentatives"
                )
        except Exception as e:
            print_result(f"Tentative {i+1}", False, f"Erreur: {e}")

def test_token_validation():
    """Tests de validation des tokens"""
    print_test("TESTS DE VALIDATION DES TOKENS")
    
    # Obtenir un token valide
    try:
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "password123"},
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            token = login_response.json()["access_token"]
            
            # Test avec token valide
            test_response = requests.get(
                f"{BASE_URL}/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            print_result(
                "Accès avec token valide",
                test_response.status_code == 200,
                f"Status {test_response.status_code}"
            )
            
            # Test avec token invalide
            test_response = requests.get(
                f"{BASE_URL}/auth/me",
                headers={"Authorization": "Bearer token_invalide"}
            )
            print_result(
                "Accès avec token invalide",
                test_response.status_code == 401,
                f"Status {test_response.status_code}"
            )
            
            # Test sans token
            test_response = requests.get(f"{BASE_URL}/auth/me")
            print_result(
                "Accès sans token",
                test_response.status_code == 401,
                f"Status {test_response.status_code}"
            )
        else:
            print_result("Obtention du token", False, "Impossible d'obtenir un token pour les tests")
    except Exception as e:
        print_result("Tests de tokens", False, f"Erreur: {e}")

def test_register_then_login():
    """Test d'inscription puis connexion"""
    print_test("TEST INSCRIPTION PUIS CONNEXION")
    
    timestamp = int(datetime.now().timestamp())
    username = f"test_flow_{timestamp}"
    email = f"test_flow_{timestamp}@test.com"
    
    try:
        # Inscription
        register_response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                "username": username,
                "email": email,
                "password": "password123",
                "nom": "Flow",
                "prenom": "Test",
                "role": "parent"
            },
            headers={"Content-Type": "application/json"}
        )
        
        if register_response.status_code == 201:
            print_result("Inscription", True, f"Utilisateur {username} créé")
            
            # Connexion avec username
            login_response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": username, "password": "password123"},
                headers={"Content-Type": "application/json"}
            )
            print_result(
                "Connexion avec username",
                login_response.status_code == 200,
                f"Status {login_response.status_code}"
            )
            
            # Connexion avec email
            login_response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": email, "password": "password123"},
                headers={"Content-Type": "application/json"}
            )
            print_result(
                "Connexion avec email",
                login_response.status_code == 200,
                f"Status {login_response.status_code}"
            )
        else:
            error = register_response.json().get("error", "")
            print_result("Inscription", False, f"Status {register_response.status_code} - {error}")
    except Exception as e:
        print_result("Test flow complet", False, f"Erreur: {e}")

def main():
    """Exécute tous les tests"""
    print(f"\n{Colors.YELLOW}{'='*70}{Colors.RESET}")
    print(f"{Colors.YELLOW}  TESTS COMPLETS D'AUTHENTIFICATION{Colors.RESET}")
    print(f"{Colors.YELLOW}  Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(f"{Colors.YELLOW}{'='*70}{Colors.RESET}")
    
    # Vérifier que le serveur est accessible
    try:
        health = requests.get(f"{BASE_URL}/health", timeout=5)
        if health.status_code != 200:
            print(f"{Colors.RED}❌ Serveur non accessible ou erreur{Colors.RESET}")
            return
    except:
        print(f"{Colors.RED}❌ Serveur non accessible. Démarrez-le avec: python3 app.py{Colors.RESET}")
        return
    
    print(f"{Colors.GREEN}✅ Serveur accessible{Colors.RESET}\n")
    
    # Exécuter tous les tests
    tokens = test_login_success()
    test_login_failures()
    created_users = test_register_success()
    test_register_failures()
    test_password_validation()
    test_rate_limiting()
    test_token_validation()
    test_register_then_login()
    
    # Résumé
    print_test("RÉSUMÉ")
    print(f"{Colors.GREEN}✅ Tests de connexion réussie: {len(tokens)}/{6}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Utilisateurs créés: {len(created_users)}{Colors.RESET}")
    print(f"\n{Colors.BLUE}Tests terminés !{Colors.RESET}\n")

if __name__ == "__main__":
    main()

