# 🧪 Guide de Test de l'API

## ✅ Serveur Démarré

Votre serveur Flask est maintenant actif sur :
- **Local** : http://127.0.0.1:5000
- **Réseau** : http://192.168.1.74:5000

## 🔍 Tests Rapides

### 1. Test de Santé (Health Check)
```bash
curl http://localhost:5000/api/health
```

**Résultat attendu** :
```json
{"status": "ok", "message": "ESA API is running"}
```

### 2. Test d'Authentification (Login)
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 3. Test avec Token JWT
```bash
# D'abord, obtenez un token avec le login ci-dessus
TOKEN="votre_token_ici"

# Ensuite, testez un endpoint protégé
curl http://localhost:5000/api/admin/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

## 📋 Endpoints Disponibles

### Authentification
- `POST /api/auth/login` - Connexion
- `POST /api/auth/register` - Inscription
- `POST /api/auth/logout` - Déconnexion
- `POST /api/auth/reset-password` - Réinitialisation mot de passe

### Administration
- `GET /api/admin/dashboard` - Tableau de bord admin
- `GET /api/admin/users` - Liste des utilisateurs
- `GET /api/admin/etudiants` - Liste des étudiants

### Étudiants
- `GET /api/etudiant/notes` - Notes de l'étudiant
- `GET /api/etudiant/bulletin` - Bulletin scolaire
- `GET /api/etudiant/emploi-temps` - Emploi du temps

### Nouvelles Fonctionnalités
- `GET /api/ai/prediction/reussite?etudiant_id=1` - Prédiction ML
- `GET /api/gamification/points` - Points de gamification
- `GET /api/elearning/cours` - Cours en ligne
- `GET /api/chat/conversations` - Conversations chat
- `GET /api/portfolio/mon-portfolio` - Portfolio numérique

## 🛠️ Outils Recommandés

### Postman
Importez la collection d'API (à créer) pour tester facilement tous les endpoints.

### cURL
Utilisez cURL depuis le terminal pour des tests rapides.

### Python Requests
```python
import requests

# Test health
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# Test login
response = requests.post('http://localhost:5000/api/auth/login', 
                        json={'username': 'admin', 'password': 'admin123'})
token = response.json()['access_token']
print(f"Token: {token}")
```

## ⚠️ Notes Importantes

1. **Base de Données** : Assurez-vous que la base de données est initialisée
2. **Utilisateurs** : Créez des utilisateurs de test via `/api/auth/register` ou le script d'initialisation
3. **CORS** : L'API accepte les requêtes depuis toutes les origines (configuré pour développement)
4. **JWT** : Les tokens expirent après 24h par défaut

## 🐛 Dépannage

### Erreur 404
- Vérifiez que le serveur est bien démarré
- Vérifiez l'URL (doit commencer par `/api/`)

### Erreur 401 (Unauthorized)
- Vérifiez que vous avez un token JWT valide
- Vérifiez le format : `Authorization: Bearer <token>`

### Erreur 500 (Server Error)
- Vérifiez les logs du serveur
- Vérifiez que la base de données existe et est accessible

## 📝 Prochaines Étapes

1. **Tester l'authentification** complète
2. **Créer des utilisateurs de test** pour chaque rôle
3. **Tester les endpoints** de chaque module
4. **Intégrer avec le frontend Flutter**

