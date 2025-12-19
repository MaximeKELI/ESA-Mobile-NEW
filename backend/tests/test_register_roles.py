"""
Test d'inscription pour tous les rôles
"""
import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_register_role(role, username_prefix):
    """Test l'inscription pour un rôle spécifique"""
    timestamp = int(time.time())
    username = f"{username_prefix}_test_{timestamp}"
    email = f"{username_prefix}_test_{timestamp}@test.com"
    
    print(f"\n=== Test Inscription {role.upper()} ===")
    print(f"Username: {username}")
    print(f"Email: {email}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json={
                'username': username,
                'email': email,
                'password': 'password123',
                'nom': 'Test',
                'prenom': role.capitalize(),
                'role': role
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Succès!")
            print(f"User ID: {data.get('user', {}).get('id')}")
            print(f"Role: {data.get('user', {}).get('role')}")
            print(f"Is Active: {data.get('user', {}).get('is_active')}")
            return True
        else:
            error_data = response.json() if response.status_code < 500 else {}
            print(f"❌ Échec")
            print(f"Error: {error_data.get('error', 'Erreur inconnue')}")
            if 'details' in error_data:
                print(f"Details: {error_data['details']}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TESTS D'INSCRIPTION PAR RÔLE")
    print("=" * 60)
    
    results = {}
    
    # Test tous les rôles
    roles = ['etudiant', 'parent', 'enseignant']
    
    for role in roles:
        results[role] = test_register_role(role, role)
        time.sleep(1)  # Attendre entre les tests
    
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    for role, success in results.items():
        status = "✅ OK" if success else "❌ ÉCHEC"
        print(f"{role.capitalize():<15} : {status}")

