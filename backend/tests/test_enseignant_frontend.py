"""
Test d'inscription et connexion enseignant depuis le frontend
Simule les requêtes Flutter vers le backend
"""
import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def print_section(title):
    """Affiche une section"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(success, message, details=""):
    """Affiche un résultat"""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")
    if details:
        print(f"   {details}")

def test_inscription_enseignant():
    """Test d'inscription en tant qu'enseignant"""
    print_section("TEST 1: INSCRIPTION ENSEIGNANT")
    
    timestamp = int(datetime.now().timestamp())
    user_data = {
        'username': f'enseignant_test_{timestamp}',
        'email': f'enseignant_test_{timestamp}@esa.tg',
        'password': 'password123',
        'nom': 'Test',
        'prenom': 'Enseignant',
        'role': 'enseignant'
    }
    
    print(f"\n📝 Données d'inscription:")
    print(json.dumps(user_data, indent=2, ensure_ascii=False))
    
    try:
        print(f"\n🌐 Envoi de la requête POST à {BASE_URL}/auth/register...")
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Origin': 'http://localhost'  # Simuler le frontend
            },
            timeout=10
        )
        
        print(f"\n📊 Réponse reçue:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"   Body: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"   Body (raw): {response.text[:500]}")
        
        if response.status_code == 201:
            print_result(True, "Inscription réussie", f"Status: {response.status_code}")
            
            if 'user' in response_data:
                user = response_data['user']
                print(f"\n👤 Utilisateur créé:")
                print(f"   ID: {user.get('id')}")
                print(f"   Username: {user.get('username')}")
                print(f"   Email: {user.get('email')}")
                print(f"   Role: {user.get('role')}")
                print(f"   Is Active: {user.get('is_active')}")
                print(f"   Nom: {user.get('nom')}")
                print(f"   Prénom: {user.get('prenom')}")
                
                # Vérifications
                checks = []
                if user.get('role') == 'enseignant':
                    checks.append(("✅", "Rôle correct"))
                else:
                    checks.append(("❌", f"Rôle incorrect: {user.get('role')}"))
                
                if user.get('is_active') == True:
                    checks.append(("✅", "Compte activé"))
                else:
                    checks.append(("❌", f"Compte non activé: {user.get('is_active')}"))
                
                if user.get('id'):
                    checks.append(("✅", f"ID généré: {user.get('id')}"))
                else:
                    checks.append(("❌", "ID manquant"))
                
                print(f"\n🔍 Vérifications:")
                for icon, check in checks:
                    print(f"   {icon} {check}")
                
                return {
                    'success': True,
                    'user': user,
                    'username': user_data['username'],
                    'password': user_data['password']
                }
            else:
                print_result(False, "Réponse invalide", "Clé 'user' manquante dans la réponse")
                return {'success': False, 'error': 'user key missing'}
        else:
            print_result(False, f"Inscription échouée", f"Status: {response.status_code}")
            if response.status_code < 500:
                try:
                    error_data = response.json()
                    print(f"\n❌ Erreur détectée:")
                    print(f"   Message: {error_data.get('error', 'Erreur inconnue')}")
                    if 'details' in error_data:
                        print(f"   Détails: {error_data.get('details')}")
                except:
                    print(f"   Réponse: {response.text[:200]}")
            return {'success': False, 'error': f'status_{response.status_code}'}
            
    except requests.exceptions.ConnectionError:
        print_result(False, "Connexion impossible", "Le serveur backend n'est pas accessible")
        print("   💡 Démarrez le serveur avec: cd backend && python3 app.py")
        return {'success': False, 'error': 'connection_error'}
    except Exception as e:
        print_result(False, "Exception", str(e))
        import traceback
        print(f"\n📋 Traceback:")
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def test_connexion_enseignant(username, password):
    """Test de connexion en tant qu'enseignant"""
    print_section("TEST 2: CONNEXION ENSEIGNANT")
    
    login_data = {
        'username': username,
        'password': password
    }
    
    print(f"\n📝 Données de connexion:")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    
    try:
        print(f"\n🌐 Envoi de la requête POST à {BASE_URL}/auth/login...")
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Origin': 'http://localhost'  # Simuler le frontend
            },
            timeout=10
        )
        
        print(f"\n📊 Réponse reçue:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"   Body: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        except:
            print(f"   Body (raw): {response.text[:500]}")
        
        if response.status_code == 200:
            print_result(True, "Connexion réussie", f"Status: {response.status_code}")
            
            if 'access_token' in response_data:
                print(f"\n🔑 Token d'accès obtenu:")
                token = response_data['access_token']
                print(f"   Token (premiers 50 caractères): {token[:50]}...")
                
                if 'user' in response_data:
                    user = response_data['user']
                    print(f"\n👤 Utilisateur connecté:")
                    print(f"   ID: {user.get('id')}")
                    print(f"   Username: {user.get('username')}")
                    print(f"   Email: {user.get('email')}")
                    print(f"   Role: {user.get('role')}")
                    print(f"   Nom: {user.get('nom')}")
                    print(f"   Prénom: {user.get('prenom')}")
                    
                    # Vérifications
                    checks = []
                    if user.get('role') == 'enseignant':
                        checks.append(("✅", "Rôle correct"))
                    else:
                        checks.append(("❌", f"Rôle incorrect: {user.get('role')}"))
                    
                    if user.get('id'):
                        checks.append(("✅", f"ID présent: {user.get('id')}"))
                    else:
                        checks.append(("❌", "ID manquant"))
                    
                    print(f"\n🔍 Vérifications:")
                    for icon, check in checks:
                        print(f"   {icon} {check}")
                
                return {
                    'success': True,
                    'token': token,
                    'user': response_data.get('user')
                }
            else:
                print_result(False, "Token manquant", "Clé 'access_token' absente de la réponse")
                return {'success': False, 'error': 'token_missing'}
        else:
            print_result(False, f"Connexion échouée", f"Status: {response.status_code}")
            if response.status_code < 500:
                try:
                    error_data = response.json()
                    print(f"\n❌ Erreur détectée:")
                    print(f"   Message: {error_data.get('error', 'Erreur inconnue')}")
                    if 'details' in error_data:
                        print(f"   Détails: {error_data.get('details')}")
                except:
                    print(f"   Réponse: {response.text[:200]}")
            return {'success': False, 'error': f'status_{response.status_code}'}
            
    except requests.exceptions.ConnectionError:
        print_result(False, "Connexion impossible", "Le serveur backend n'est pas accessible")
        return {'success': False, 'error': 'connection_error'}
    except Exception as e:
        print_result(False, "Exception", str(e))
        import traceback
        print(f"\n📋 Traceback:")
        traceback.print_exc()
        return {'success': False, 'error': str(e)}

def test_endpoint_me(token):
    """Test de l'endpoint /auth/me avec le token"""
    print_section("TEST 3: ENDPOINT /auth/me")
    
    try:
        print(f"\n🌐 Envoi de la requête GET à {BASE_URL}/auth/me...")
        response = requests.get(
            f"{BASE_URL}/auth/me",
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=10
        )
        
        print(f"\n📊 Réponse reçue:")
        print(f"   Status Code: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"   Body: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            
            if response.status_code == 200:
                print_result(True, "Endpoint /auth/me accessible", f"Status: {response.status_code}")
                return {'success': True, 'data': response_data}
            else:
                print_result(False, "Endpoint /auth/me échoué", f"Status: {response.status_code}")
                return {'success': False, 'error': f'status_{response.status_code}'}
        except:
            print(f"   Body (raw): {response.text[:200]}")
            return {'success': False, 'error': 'invalid_json'}
            
    except Exception as e:
        print_result(False, "Exception", str(e))
        return {'success': False, 'error': str(e)}

def main():
    """Fonction principale"""
    print("\n" + "=" * 80)
    print("  TEST COMPLET: INSCRIPTION ET CONNEXION ENSEIGNANT")
    print("  Simule les requêtes du frontend Flutter")
    print("=" * 80)
    
    # Test 1: Inscription
    inscription_result = test_inscription_enseignant()
    
    if not inscription_result.get('success'):
        print("\n" + "=" * 80)
        print("  ❌ TEST ARRÊTÉ: L'inscription a échoué")
        print("=" * 80)
        return
    
    username = inscription_result.get('username')
    password = inscription_result.get('password')
    
    # Test 2: Connexion
    connexion_result = test_connexion_enseignant(username, password)
    
    if connexion_result.get('success'):
        token = connexion_result.get('token')
        
        # Test 3: Endpoint /auth/me
        test_endpoint_me(token)
    
    # Résumé final
    print_section("RÉSUMÉ FINAL")
    
    results = {
        'Inscription': '✅ RÉUSSI' if inscription_result.get('success') else '❌ ÉCHOUÉ',
        'Connexion': '✅ RÉUSSI' if connexion_result.get('success') else '❌ ÉCHOUÉ',
    }
    
    for test_name, result in results.items():
        print(f"   {test_name}: {result}")
    
    print("\n" + "=" * 80)
    if all(r.get('success', False) for r in [inscription_result, connexion_result]):
        print("  🎉 TOUS LES TESTS SONT RÉUSSIS !")
    else:
        print("  ⚠️  CERTAINS TESTS ONT ÉCHOUÉ - VÉRIFIER LES ERREURS CI-DESSUS")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()

