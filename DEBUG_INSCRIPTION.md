# 🔍 Debug Inscription - Problème Parent et Enseignant

## 🔴 Problème Identifié

Seulement la partie étudiant s'affiche après inscription. Les parties enseignant et parent ne fonctionnent pas.

## 🔍 Causes Possibles

### 1. Erreurs 400 sur l'inscription
Les logs montrent des erreurs 400, ce qui signifie que l'inscription échoue pour parent et enseignant.

### 2. Réponse Backend Incomplète
Le backend retourne seulement certains champs dans la réponse d'inscription :
- ✅ id, username, email, role, nom, prenom
- ❌ is_active, telephone, adresse, photo_path, last_login

Le `UserModel.fromJson()` essaie de lire `is_active` mais il n'est pas dans la réponse.

### 3. Logique d'Activation
```python
# Backend ligne 171
data.get('is_active', True) if data['role'] != 'etudiant' else False
```
- Étudiants : `is_active = False` (doivent être activés par admin)
- Parents/Enseignants : `is_active = True` (activés automatiquement)

## ✅ Corrections Appliquées

### 1. Réponse Backend Complète
**Fichier :** `backend/blueprints/auth.py`

**Avant :**
```python
return jsonify({
    'message': 'Inscription réussie',
    'user': {
        'id': user['id'],
        'username': user['username'],
        'email': user['email'],
        'role': user['role'],
        'nom': user['nom'],
        'prenom': user['prenom']
    }
}), 201
```

**Après :**
```python
user_dict = {
    'id': user['id'],
    'username': user['username'],
    'email': user['email'],
    'role': user['role'],
    'nom': user['nom'],
    'prenom': user['prenom'],
    'telephone': user.get('telephone'),
    'adresse': user.get('adresse'),
    'photo_path': user.get('photo_path'),
    'is_active': bool(user['is_active']),
    'last_login': user.get('last_login'),
}

return jsonify({
    'message': 'Inscription réussie',
    'user': user_dict
}), 201
```

## 🧪 Tests à Effectuer

### Test 1 : Inscription Parent
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testparent",
    "email": "testparent@test.com",
    "password": "password123",
    "nom": "Test",
    "prenom": "Parent",
    "role": "parent"
  }'
```

**Résultat attendu :** Status 201 avec `is_active: true`

### Test 2 : Inscription Enseignant
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testenseignant",
    "email": "testenseignant@test.com",
    "password": "password123",
    "nom": "Test",
    "prenom": "Enseignant",
    "role": "enseignant"
  }'
```

**Résultat attendu :** Status 201 avec `is_active: true`

## 🔧 Vérifications Frontend

### 1. UserModel.fromJson()
Vérifier que `is_active` est correctement parsé :
```dart
isActive: json['is_active'] == 1 || json['is_active'] == true,
```

### 2. HomeScreen
Vérifier que le switch case reconnaît bien les rôles :
```dart
case AppConstants.roleEnseignant:
  return const EnseignantDashboardScreen();
case AppConstants.roleParent:
  return const ParentDashboardScreen();
```

### 3. AuthWrapper
Vérifier que la navigation se fait correctement après inscription :
```dart
if (authProvider.isAuthenticated && authProvider.user != null) {
  return const HomeScreen();
}
```

## 📝 Checklist de Debug

- [ ] Backend retourne tous les champs nécessaires
- [ ] `is_active` est correctement retourné pour parent/enseignant
- [ ] UserModel.fromJson() parse correctement `is_active`
- [ ] AuthProvider met à jour `_user` après inscription
- [ ] HomeScreen reconnaît les rôles parent et enseignant
- [ ] Navigation vers le bon dashboard fonctionne

## 🎯 Prochaines Étapes

1. Redémarrer le serveur backend
2. Tester l'inscription parent depuis Flutter
3. Vérifier les logs backend pour voir l'erreur exacte
4. Vérifier que le dashboard parent s'affiche correctement

---

**🔧 Correction appliquée : Réponse backend complète avec tous les champs nécessaires**


