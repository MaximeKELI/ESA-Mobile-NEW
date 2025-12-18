# Guide de Démarrage Rapide - Application ESA

## 🚀 Démarrage rapide

### 1. Backend (Flask)

```bash
cd backend

# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
cd database
python init_db.py
cd ..

# Lancer le serveur
python app.py
```

Le serveur sera accessible sur `http://localhost:5000`

**Compte admin par défaut :**
- Username: `admin`
- Password: `admin123`

### 2. Frontend (Flutter)

```bash
cd esa

# Installer les dépendances
flutter pub get

# Configurer l'URL de l'API
# Éditer lib/core/constants/api_constants.dart
# Changer baseUrl selon votre configuration :
# - Émulateur Android : http://10.0.2.2:5000/api
# - Appareil physique : http://VOTRE_IP:5000/api
# - iOS Simulator : http://localhost:5000/api

# Lancer l'application
flutter run
```

## 📋 Fonctionnalités implémentées

### ✅ Backend (100%)
- ✅ Schéma de base de données SQLite complet
- ✅ Authentification JWT avec refresh tokens
- ✅ Contrôle d'accès par rôles (admin, comptabilite, enseignant, etudiant, parent)
- ✅ Gestion des utilisateurs
- ✅ Module académique (années, filières, niveaux, classes, matières, notes)
- ✅ Module financier (frais, paiements, validation, reçus PDF)
- ✅ Gestion des absences
- ✅ Calcul automatique des moyennes et classements
- ✅ Génération de PDF (bulletins, reçus)
- ✅ QR codes pour cartes étudiantes
- ✅ Messagerie interne
- ✅ Notifications
- ✅ Annonces
- ✅ Journalisation des actions
- ✅ Validation stricte des données

### ✅ Frontend (Structure de base)
- ✅ Architecture modulaire Flutter
- ✅ Authentification (login/logout)
- ✅ Navigation par rôle
- ✅ Thème Material Design 3
- ✅ Services API et authentification
- ✅ Tableau de bord admin (structure)
- ✅ Écrans de base pour tous les rôles

### ⏳ À compléter dans le frontend
- Écrans détaillés pour chaque module
- Gestion hors ligne et synchronisation
- Notifications push
- Affichage des données (notes, paiements, etc.)
- Formulaires de saisie complets
- Graphiques et statistiques

## 🔧 Configuration

### Backend
Modifier `backend/.env` pour :
- Changer les secrets (SECRET_KEY, JWT_SECRET_KEY)
- Configurer le chemin de la base de données
- Ajuster les paramètres du serveur

### Frontend
Modifier `esa/lib/core/constants/api_constants.dart` pour :
- Configurer l'URL de base de l'API selon votre environnement

## 📱 Test de l'application

1. **Démarrer le backend** : `python backend/app.py`
2. **Démarrer le frontend** : `flutter run` dans le dossier `esa`
3. **Se connecter** avec les identifiants admin par défaut
4. **Explorer** les différentes fonctionnalités selon le rôle

## 🐛 Résolution de problèmes

### Le backend ne démarre pas
- Vérifier que Python 3.8+ est installé
- Vérifier que toutes les dépendances sont installées
- Vérifier que le port 5000 n'est pas utilisé

### Le frontend ne se connecte pas à l'API
- Vérifier que le backend est démarré
- Vérifier l'URL dans `api_constants.dart`
- Pour Android : utiliser `10.0.2.2` au lieu de `localhost`
- Vérifier les permissions réseau dans AndroidManifest.xml

### Erreurs de base de données
- Supprimer `backend/database/esa.db` et réinitialiser avec `init_db.py`
- Vérifier les permissions d'écriture sur le dossier database

## 📚 Documentation

- Voir `README.md` pour la documentation complète
- Voir `backend/README.md` pour la documentation de l'API
- Les endpoints API sont documentés dans les blueprints

## 🔐 Sécurité en production

⚠️ **IMPORTANT avant le déploiement :**

1. Changer tous les secrets par défaut
2. Utiliser bcrypt au lieu de SHA-256 pour les mots de passe
3. Configurer HTTPS
4. Activer la validation CORS appropriée
5. Configurer la sauvegarde automatique de la base de données
6. Utiliser un serveur WSGI (Gunicorn) au lieu du serveur de développement Flask
7. Configurer un reverse proxy (Nginx)
8. Activer les logs et monitoring

## 📞 Support

Pour toute question ou problème, consultez la documentation ou contactez l'équipe de développement.

---

**Bon développement ! 🎉**

