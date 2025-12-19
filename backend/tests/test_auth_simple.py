"""
Tests simples d'authentification - Version simplifiée
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_login():
    """Test de connexion simple"""
    print("\n=== TEST DE CONNEXION ===")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "password123"},
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    return response.status_code == 200

def test_register():
    """Test d'inscription simple"""
    print("\n=== TEST D'INSCRIPTION ===")
    import time
    timestamp = int(time.time())
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "username": f"test_{timestamp}",
            "email": f"test_{timestamp}@test.com",
            "password": "password123",
            "nom": "Test",
            "prenom": "User",
            "role": "parent"
        },
        headers={"Content-Type": "application/json"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    return response.status_code == 201

if __name__ == "__main__":
    print("Tests simples d'authentification")
    print("=" * 50)
    
    login_ok = test_login()
    register_ok = test_register()
    
    print("\n=== RÉSULTATS ===")
    print(f"Login: {'✅ OK' if login_ok else '❌ ÉCHEC'}")
    print(f"Register: {'✅ OK' if register_ok else '❌ ÉCHEC'}")

