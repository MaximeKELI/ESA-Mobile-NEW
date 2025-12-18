# Application de Gestion Scolaire - ESA Togo

Application mobile complète de gestion scolaire pour l'École Supérieure des Affaires (ESA - Togo), développée avec Flutter (frontend) et Flask (backend).

## 🎯 Fonctionnalités principales

### Gestion des utilisateurs
- **Administration** : Gestion complète de tous les utilisateurs, années académiques, filières, niveaux, classes, matières
- **Comptabilité** : Gestion des paiements, validation, génération de reçus PDF
- **Enseignants** : Saisie et validation des notes, gestion des absences
- **Étudiants** : Consultation des notes, bulletins, emplois du temps, absences
- **Parents** : Suivi de la scolarité de leurs enfants

### Modules principaux

#### Module académique
- Gestion des années académiques, filières, niveaux, classes
- Gestion des matières et coefficients
- Saisie et validation des notes (devoirs, contrôles, examens)
- Calcul automatique des moyennes et classements
- Génération de bulletins PDF
- Gestion des absences et retards
- Délibérations et décisions académiques

#### Module financier
- Définition des frais scolaires (inscription, scolarité, tranches)
- Enregistrement des paiements (espèces, mobile money, virement)
- Suivi automatique des soldes et arriérés
- Génération de reçus et factures PDF
- Alertes de retard de paiement
- Verrouillage automatique en cas d'impayés

#### Autres fonctionnalités
- Emplois du temps
- Cartes étudiantes numériques (QR code)
- Annonces officielles
- Notifications push
- Messagerie interne sécurisée
- Tableau de bord avec statistiques
- Mode hors ligne avec synchronisation
- Export des données (PDF/CSV)

## 🏗️ Architecture

### Backend (Flask)
- **Framework** : Flask avec Blueprints modulaires
- **Base de données** : SQLite avec schéma relationnel normalisé
- **Authentification** : JWT avec refresh tokens
- **Sécurité** : Contrôle d'accès par rôles, validation stricte, journalisation

### Frontend (Flutter)
- **Framework** : Flutter (Android prioritaire)
- **State Management** : Provider/Riverpod
- **Architecture** : Structure modulaire par rôle
- **UI** : Material Design 3, responsive, accessible

## 📁 Structure du projet

```
Application_ESA/
├── backend/              # Backend Flask
│   ├── app.py
│   ├── blueprints/
│   ├── database/
│   ├── utils/
│   └── requirements.txt
├── esa/                  # Frontend Flutter
│   ├── lib/
│   │   ├── core/         # Constantes, thème, services
│   │   ├── models/       # Modèles de données
│   │   ├── providers/    # State management
│   │   └── screens/      # Écrans par rôle
│   └── pubspec.yaml
└── README.md
```

## 🚀 Installation et démarrage

### Backend

1. Aller dans le dossier backend :
```bash
cd backend
```

2. Créer un environnement virtuel :
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Initialiser la base de données :
```bash
cd database
python init_db.py
cd ..
```

5. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

6. Lancer le serveur :
```bash
python app.py
```

Le serveur sera accessible sur `http://localhost:5000`

### Frontend

1. Aller dans le dossier esa :
```bash
cd esa
```

2. Installer les dépendances :
```bash
flutter pub get
```

3. Configurer l'URL de l'API dans `lib/core/constants/api_constants.dart` :
```dart
static const String baseUrl = 'http://VOTRE_IP:5000/api';
```

4. Lancer l'application :
```bash
flutter run
```

## 🔐 Comptes par défaut

- **Admin** :
  - Username: `admin`
  - Password: `admin123`

**⚠️ IMPORTANT : Changez le mot de passe par défaut en production !**

## 📱 Rôles utilisateurs

1. **Administration** : Gestion complète de l'école
2. **Comptabilité** : Gestion des paiements et finances
3. **Enseignant** : Saisie des notes et gestion des absences
4. **Étudiant** : Consultation des notes et informations
5. **Parent** : Suivi de la scolarité des enfants

## 🔒 Sécurité

- Authentification JWT sécurisée
- Hashage des mots de passe
- Contrôle d'accès par rôles
- Validation stricte des données
- Journalisation des actions sensibles
- Protection contre les injections SQL
- Gestion des erreurs

## 📊 Base de données

La base de données SQLite contient toutes les tables nécessaires :
- Utilisateurs et profils
- Années académiques, filières, niveaux, classes
- Matières et notes
- Paiements et frais
- Absences et emplois du temps
- Messages et notifications
- Logs de connexion et actions

## 🧪 Tests

Les tests sont à implémenter pour :
- Backend : pytest
- Frontend : flutter_test

## 📝 Documentation API

Voir `backend/README.md` pour la documentation complète de l'API.

## 🚢 Déploiement

### Backend
- Utiliser Gunicorn ou uWSGI
- Configurer Nginx comme reverse proxy
- Utiliser HTTPS
- Configurer la sauvegarde automatique de la base de données

### Frontend
- Build Android : `flutter build apk --release`
- Build iOS : `flutter build ios --release`
- Publier sur Google Play Store / App Store

## 📄 Licence

Ce projet est développé pour l'École Supérieure des Affaires (ESA Togo).

## 👥 Contribution

Pour contribuer au projet, veuillez suivre les bonnes pratiques de développement et créer des pull requests.

## 📞 Support

Pour toute question ou problème, contactez l'équipe de développement.

---

**Développé avec ❤️ pour l'ESA Togo**
