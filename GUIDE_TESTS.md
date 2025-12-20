# 📋 Guide des Tests Unitaires - ESA Application

## 🎯 Vue d'Ensemble

Ce guide explique comment exécuter les tests unitaires pour le frontend (Flutter) et le backend (Python/Flask).

---

## 🔧 BACKEND - Tests Python

### Installation des Dépendances

```bash
cd backend
pip install -r requirements_test.txt
```

### Structure des Tests

```
backend/
├── tests/
│   ├── test_backend_complete.py  # Tests complets du backend
│   ├── test_communication_complete.py
│   └── test_quick_check.py
└── pytest.ini  # Configuration pytest
```

### Exécuter les Tests

**Tous les tests:**
```bash
cd backend
pytest tests/test_backend_complete.py -v
```

**Tests spécifiques:**
```bash
# Tests d'authentification uniquement
pytest tests/test_backend_complete.py::TestAuthBlueprint -v

# Tests de sécurité uniquement
pytest tests/test_backend_complete.py::TestSecurity -v

# Tests avec couverture de code
pytest tests/test_backend_complete.py --cov=. --cov-report=html
```

**Tests par catégorie:**
```bash
# Tests unitaires uniquement
pytest -m unit

# Tests d'intégration uniquement
pytest -m integration

# Tests de sécurité uniquement
pytest -m security
```

### Catégories de Tests Backend

1. **Tests Utils.Auth**
   - Hashage de mot de passe
   - Vérification de mot de passe
   - Journalisation des connexions
   - Journalisation des actions

2. **Tests Utils.Validators**
   - Validation d'email
   - Validation des champs requis

3. **Tests Utils.Security**
   - Validation de la force du mot de passe
   - Sanitization des entrées
   - Détection d'injection SQL

4. **Tests Blueprints.Auth**
   - Connexion réussie/échouée
   - Inscription réussie/échouée
   - Gestion des erreurs

5. **Tests Database**
   - Connexion à la base de données
   - Création d'utilisateurs
   - Requêtes de données

6. **Tests Intégration**
   - Flux d'authentification complet
   - Cohérence du hashage

7. **Tests Performance**
   - Vitesse de hashage
   - Performance des requêtes DB

8. **Tests Sécurité**
   - Prévention d'injection SQL
   - Prévention XSS

---

## 📱 FRONTEND - Tests Flutter

### Installation des Dépendances

```bash
cd esa
flutter pub get
```

### Générer les Mocks

```bash
cd esa
flutter pub run build_runner build --delete-conflicting-outputs
```

### Structure des Tests

```
esa/
├── test/
│   └── test_frontend_complete.dart  # Tests complets du frontend
└── pubspec.yaml  # Dépendances de test
```

### Exécuter les Tests

**Tous les tests:**
```bash
cd esa
flutter test test/test_frontend_complete.dart
```

**Tests spécifiques:**
```bash
# Tests de modèles uniquement
flutter test test/test_frontend_complete.dart --name "UserModel"

# Tests d'authentification uniquement
flutter test test/test_frontend_complete.dart --name "AuthService"

# Tests avec couverture
flutter test --coverage
```

### Catégories de Tests Frontend

1. **Tests Models**
   - Création depuis JSON
   - Sérialisation en JSON
   - Gestion des booléens

2. **Tests ApiService**
   - Singleton
   - Configuration de base URL

3. **Tests AuthService**
   - Authentification
   - Gestion des utilisateurs
   - Stockage local

4. **Tests AuthProvider**
   - État initial
   - Mise à jour de l'utilisateur
   - Déconnexion

5. **Tests Constants**
   - URLs et endpoints
   - Timeouts

6. **Tests Validation**
   - Validation d'email
   - Validation de mot de passe

7. **Tests Navigation**
   - Routes définies

8. **Tests Rôles**
   - Gestion des rôles
   - Validation des rôles

9. **Tests Sécurité**
   - Stockage sécurisé
   - Protection des données sensibles

10. **Tests Performance**
    - Vitesse de sérialisation
    - Performance des opérations

11. **Tests Intégration**
    - Flux d'authentification complet

12. **Tests Erreurs**
    - Gestion des erreurs réseau
    - Gestion des erreurs de parsing

---

## 📊 Rapports de Couverture

### Backend

```bash
cd backend
pytest tests/test_backend_complete.py --cov=. --cov-report=html
# Ouvrir htmlcov/index.html dans le navigateur
```

### Frontend

```bash
cd esa
flutter test --coverage
# Le rapport est généré dans coverage/lcov.info
```

---

## 🧪 Exécution Automatique

### Script de Test Complet

```bash
#!/bin/bash
# test_all.sh

echo "🧪 Tests Backend..."
cd backend
pytest tests/test_backend_complete.py -v

echo "🧪 Tests Frontend..."
cd ../esa
flutter test test/test_frontend_complete.dart

echo "✅ Tous les tests terminés!"
```

---

## 📝 Notes Importantes

### Backend
- Les tests utilisent une base de données en mémoire (`:memory:`) pour l'isolation
- Les mocks sont utilisés pour simuler les dépendances externes
- Les fixtures pytest gèrent le cycle de vie des ressources

### Frontend
- Les tests utilisent `Mockito` pour créer des mocks
- `SharedPreferences` est mocké pour les tests
- Les tests sont isolés et ne nécessitent pas de connexion réseau réelle

---

## 🔍 Débogage

### Backend
```bash
# Mode verbose avec sortie détaillée
pytest tests/test_backend_complete.py -v -s

# Arrêter au premier échec
pytest tests/test_backend_complete.py -x

# Afficher les print statements
pytest tests/test_backend_complete.py -s
```

### Frontend
```bash
# Mode verbose
flutter test test/test_frontend_complete.dart --verbose

# Arrêter au premier échec
flutter test test/test_frontend_complete.dart --stop-on-first-failure
```

---

## ✅ Checklist de Tests

### Backend
- [x] Tests d'authentification
- [x] Tests de validation
- [x] Tests de sécurité
- [x] Tests de base de données
- [x] Tests d'intégration
- [x] Tests de performance

### Frontend
- [x] Tests de modèles
- [x] Tests de services
- [x] Tests de providers
- [x] Tests de validation
- [x] Tests de sécurité
- [x] Tests de performance
- [x] Tests d'intégration

---

## 🎉 Résultat Attendu

Après l'exécution des tests, vous devriez voir:

**Backend:**
```
tests/test_backend_complete.py::TestAuthUtils::test_hash_password PASSED
tests/test_backend_complete.py::TestAuthUtils::test_verify_password PASSED
...
========== 50+ tests passed in X.XXs ==========
```

**Frontend:**
```
00:01 +50: All tests passed!
```

---

**📚 Pour plus d'informations, consultez les fichiers de test directement.**


