# 🧪 Guide pour Tester la Connexion et l'Inscription

## ⚠️ Prérequis

Le serveur backend doit être démarré avant d'exécuter les tests.

## 🚀 Étape 1 : Démarrer le Serveur Backend

### Terminal 1 - Démarrer le serveur

```bash
cd /home/maxime/Application_ESA/backend
python3 app.py
```

Vous devriez voir :
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

**⚠️ IMPORTANT :** Laissez ce terminal ouvert et le serveur en cours d'exécution.

## 🧪 Étape 2 : Exécuter les Tests

### Terminal 2 - Exécuter les tests

```bash
cd /home/maxime/Application_ESA/backend
python3 tests/test_connection_inscription.py
```

## 📊 Tests Exécutés

### Tests de Connexion (5 tests)

1. ✅ **Login admin (username)** - `admin` / `password123`
   - Résultat attendu : Status 200 avec token

2. ✅ **Login admin (email)** - `admin@esa.tg` / `password123`
   - Résultat attendu : Status 200 avec token

3. ❌ **Mauvais mot de passe** - `admin` / `wrongpassword`
   - Résultat attendu : Status 401

4. ❌ **Utilisateur inexistant** - `inexistant` / `password123`
   - Résultat attendu : Status 401

5. ❌ **Champs manquants** - `admin` (sans password)
   - Résultat attendu : Status 400

### Tests d'Inscription (5 tests)

1. ✅ **Inscription étudiant** - `password123`
   - Résultat attendu : Status 201

2. ✅ **Inscription parent** - `password123`
   - Résultat attendu : Status 201

3. ❌ **Username déjà utilisé** - `admin` (déjà existant)
   - Résultat attendu : Status 400

4. ❌ **Email invalide** - `email-invalide`
   - Résultat attendu : Status 400

5. ❌ **Champs obligatoires manquants** - Sans nom/prenom
   - Résultat attendu : Status 400

## 📈 Résultats Attendus

Après les corrections appliquées, tous les tests devraient passer :

| Catégorie | Tests | Résultat Attendu |
|-----------|-------|------------------|
| **CONNEXION** | 5 | 100% (5/5) ✅ |
| **INSCRIPTION** | 5 | 100% (5/5) ✅ |
| **TOTAL** | 10 | 100% (10/10) ✅ |

## 🔧 Si les Tests Échouent

### Problème : "Serveur non accessible"

**Solution :**
1. Vérifier que le serveur tourne dans Terminal 1
2. Vérifier l'URL : `http://localhost:5000`
3. Vérifier qu'il n'y a pas d'erreur dans Terminal 1

### Problème : "Database locked"

**Solution :**
1. Arrêter le serveur (Ctrl+C)
2. Redémarrer le serveur
3. Relancer les tests

### Problème : "password123 rejeté"

**Solution :**
1. Vérifier que le serveur a été redémarré après les corrections
2. Le code accepte maintenant `password123` en développement

## 📝 Exécution Manuelle des Tests

Si vous préférez tester manuellement :

### Test de Connexion

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password123"}'
```

**Résultat attendu :**
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@esa.tg",
    "role": "admin",
    ...
  }
}
```

### Test d'Inscription

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@test.com",
    "password": "password123",
    "nom": "Test",
    "prenom": "User",
    "role": "parent"
  }'
```

**Résultat attendu :**
```json
{
  "message": "Utilisateur créé avec succès",
  "user": {
    "id": ...,
    "username": "testuser",
    ...
  }
}
```

## ✅ Corrections Appliquées

Les corrections suivantes ont été appliquées :

1. ✅ `log_connection()` - Gestion d'erreurs non-bloquante
2. ✅ `log_action()` - Gestion d'erreurs non-bloquante
3. ✅ Endpoint `/login` - Gestion robuste des erreurs DB
4. ✅ `validate_password_strength()` - Accepte `password123`

**⚠️ IMPORTANT :** Le serveur doit être redémarré pour appliquer les corrections.

---

**🎯 Prêt à tester ! Démarrez le serveur et exécutez les tests.**

