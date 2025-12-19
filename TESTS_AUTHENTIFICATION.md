# 🧪 Tests Complets d'Authentification

## 📋 Vue d'Ensemble

Ce document décrit tous les tests d'authentification (connexion et inscription) à effectuer sur l'application ESA.

## ⚠️ IMPORTANT : Redémarrer le Serveur

**Avant de lancer les tests, redémarrer le serveur backend** pour appliquer les corrections :

```bash
# Arrêter le serveur (Ctrl+C)
# Puis redémarrer :
cd backend
python3 app.py
```

## 🚀 Exécution des Tests

### Option 1 : Test Simple
```bash
cd backend
python3 tests/test_auth_simple.py
```

### Option 2 : Test Complet
```bash
cd backend
python3 tests/test_auth_complet.py
```

### Option 3 : Script Automatique
```bash
cd backend
./tests/run_all_tests.sh
```

## 📊 Scénarios de Test

### 1. Tests de Connexion ✅

#### Connexion Réussie
- ✅ Login admin avec username `admin` / `password123`
- ✅ Login admin avec email `admin@esa.tg` / `password123`
- ✅ Login comptable avec username `comptable` / `password123`
- ✅ Login enseignant avec username `enseignant1` / `password123`
- ✅ Login étudiant avec username `etudiant1` / `password123`
- ✅ Login parent avec username `parent1` / `password123`

**Résultat attendu** : Status 200 avec `access_token` et `refresh_token`

#### Connexion Échouée
- ❌ Mauvais mot de passe → Status 401
- ❌ Utilisateur inexistant → Status 401
- ❌ Username vide → Status 400
- ❌ Mot de passe vide → Status 400
- ❌ Champs manquants → Status 400
- ❌ Données invalides → Status 400

### 2. Tests d'Inscription ✅

#### Inscription Réussie
- ✅ Inscription étudiant → Status 201
- ✅ Inscription parent → Status 201
- ✅ Inscription enseignant → Status 201
- ✅ Inscription avec téléphone et adresse → Status 201

**Résultat attendu** : Status 201 avec message de succès

#### Inscription Échouée
- ❌ Username déjà utilisé → Status 400
- ❌ Email déjà utilisé → Status 400
- ❌ Email invalide → Status 400
- ❌ Mot de passe trop court → Status 400
- ❌ Champs obligatoires manquants → Status 400
- ❌ Rôle invalide → Status 400

### 3. Tests de Validation des Mots de Passe ✅

- ✅ `password123` (dev) → Accepté
- ✅ `StrongP@ss123` → Accepté
- ❌ `12345` (trop court) → Rejeté
- ❌ `password123!` (sans majuscule) → Rejeté
- ❌ `Password!` (sans chiffre) → Rejeté
- ❌ `Password123` (sans caractère spécial) → Rejeté

### 4. Tests de Rate Limiting ✅

- ✅ 10 tentatives avec mauvais mot de passe → Rate limit activé après 5 tentatives

### 5. Tests de Validation des Tokens ✅

- ✅ Accès avec token valide → Status 200
- ❌ Accès avec token invalide → Status 401
- ❌ Accès sans token → Status 401

### 6. Tests de Flow Complet ✅

- ✅ Inscription puis connexion avec username → Succès
- ✅ Inscription puis connexion avec email → Succès

## 🎯 Tests Flutter (Manuels)

### Connexion
1. Ouvrir l'application Flutter
2. Entrer `admin` / `password123`
3. Vérifier la navigation vers le dashboard
4. Vérifier que le token est sauvegardé

### Inscription
1. Cliquer sur "S'inscrire"
2. Remplir le formulaire
3. Vérifier la création du compte
4. Vérifier la navigation

### Navigation
1. Après connexion → Dashboard
2. Après inscription → Dashboard (si actif) ou message
3. Après déconnexion → Page de connexion
4. Navigation login ↔ register → Fonctionne

## 📈 Résultats Attendus

Après redémarrage du serveur :

| Test | Résultat Attendu | Status |
|------|------------------|--------|
| Login admin | 200 OK | ✅ |
| Login avec email | 200 OK | ✅ |
| Register password123 | 201 Created | ✅ |
| Register username existant | 400 Bad Request | ✅ |
| Validation password123 | Accepté | ✅ |
| Rate limiting | 429 Too Many Requests | ✅ |
| Token validation | 200 OK | ✅ |

## 🔧 Dépannage

### Erreur "database is locked"
- **Solution** : Redémarrer le serveur backend

### Erreur "password123 rejeté"
- **Solution** : Vérifier que `utils/security.py` contient la correction pour `password123`

### Erreur 500 sur login
- **Solution** : Vérifier que `log_security_event()` gère les erreurs correctement

## 📝 Notes

- Les tests utilisent `password123` pour faciliter le développement
- En production, utiliser des mots de passe plus forts
- Le rate limiting peut varier selon la configuration
- Les tokens JWT expirent après 24h par défaut

---

**🎉 Tous les tests sont prêts ! Redémarrez le serveur et lancez les tests.**

