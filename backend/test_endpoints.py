"""
Script de test des endpoints de l'API ESA
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_endpoint(method, endpoint, data=None, token=None, description=""):
    """Test un endpoint et affiche le résultat"""
    url = f"{BASE_URL}{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        status_icon = "✅" if response.status_code < 400 else "❌"
        print(f"{status_icon} {method} {endpoint} - {response.status_code}")
        
        if description:
            print(f"   {description}")
        
        if response.status_code < 400:
            try:
                result = response.json()
                if isinstance(result, dict) and len(result) < 5:
                    print(f"   Réponse: {json.dumps(result, indent=2, ensure_ascii=False)}")
            except:
                pass
        
        return response
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Connexion refusée (serveur non démarré?)")
        return None
    except Exception as e:
        print(f"❌ {method} {endpoint} - Erreur: {e}")
        return None

def main():
    print("🧪 Tests des Endpoints de l'API ESA")
    print(f"URL de base: {BASE_URL}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Health Check
    print_section("1. Health Check")
    test_endpoint("GET", "/health", description="Vérification que le serveur fonctionne")
    
    # Test 2: Login
    print_section("2. Authentification")
    login_response = test_endpoint("POST", "/auth/login", 
        data={"username": "admin", "password": "password123"},
        description="Login avec admin/password123")
    
    token = None
    if login_response and login_response.status_code == 200:
        try:
            token = login_response.json().get("access_token")
            if token:
                print(f"   ✅ Token obtenu: {token[:30]}...")
        except:
            pass
    
    if not token:
        print("   ⚠️  Impossible d'obtenir un token. Les tests suivants seront limités.")
        return
    
    # Test 3: Endpoints Admin
    print_section("3. Endpoints Administration")
    test_endpoint("GET", "/admin/dashboard", token=token, description="Tableau de bord admin")
    test_endpoint("GET", "/admin/users", token=token, description="Liste des utilisateurs")
    
    # Test 4: Endpoints Étudiant
    print_section("4. Endpoints Étudiant")
    test_endpoint("GET", "/etudiant/notes", token=token, description="Notes de l'étudiant")
    test_endpoint("GET", "/etudiant/emploi-temps", token=token, description="Emploi du temps")
    
    # Test 5: Nouvelles Fonctionnalités
    print_section("5. Nouvelles Fonctionnalités")
    
    # AI Analytics
    test_endpoint("GET", "/ai/analytics/dashboard", token=token, description="Dashboard analytics")
    
    # Gamification
    test_endpoint("GET", "/gamification/points", token=token, description="Points de gamification")
    test_endpoint("GET", "/gamification/classement?type=points", token=token, description="Classement")
    
    # E-Learning
    test_endpoint("GET", "/elearning/cours", token=token, description="Liste des cours")
    
    # Chat
    test_endpoint("GET", "/chat/conversations", token=token, description="Conversations")
    
    # Portfolio
    test_endpoint("GET", "/portfolio/mon-portfolio", token=token, description="Mon portfolio")
    test_endpoint("GET", "/portfolio/competences", token=token, description="Compétences disponibles")
    
    # Dashboards
    test_endpoint("GET", "/dashboards/widgets", token=token, description="Widgets disponibles")
    test_endpoint("GET", "/dashboards/tableaux-bord", token=token, description="Tableaux de bord")
    
    # Exports
    test_endpoint("GET", "/exports/templates", token=token, description="Templates d'export")
    
    print_section("Résumé")
    print("✅ Tests terminés!")
    print("\n💡 Pour tester avec d'autres utilisateurs:")
    print("   - Comptable: comptable / password123")
    print("   - Enseignant: enseignant1 / password123")
    print("   - Étudiant: etudiant1 / password123")
    print("   - Parent: parent1 / password123")

if __name__ == "__main__":
    main()


