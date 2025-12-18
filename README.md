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

#### Module inscriptions en ligne
- Candidatures en ligne (publique)
- Suivi des candidatures
- Traitement des candidatures (accepter/refuser)
- Création automatique de compte étudiant
- Gestion des concours d'entrée
- Résultats de concours

#### Module bourses et aides
- Gestion des types de bourses
- Attribution de bourses aux étudiants
- Suivi des paiements de bourses
- Gestion des statuts (active, suspendue, terminée)

#### Module bibliothèque
- Catalogue des ouvrages
- Gestion des exemplaires
- Emprunts et retours de livres
- Réservations d'ouvrages
- Amendes automatiques pour retards
- Recherche d'ouvrages

#### Module stages et alternances
- Gestion des entreprises partenaires
- Offres de stage
- Conventions de stage
- Signature électronique des conventions
- Évaluations de stage
- Suivi des stages

#### Module infrastructure
- Gestion des salles et amphithéâtres
- Réservations de salles avec vérification de disponibilité
- Gestion des équipements
- Maintenance des équipements
- Inventaire

#### Module ressources humaines
- Gestion du personnel (enseignants, administratif, technique)
- Gestion des contrats (CDI, CDD, vacataires)
- Gestion des congés
- Évaluations du personnel

#### Module vie étudiante
- Gestion des clubs et associations
- Gestion des événements et activités
- Gestion des compétitions
- Gestion des sorties pédagogiques

#### Module diplômes et certifications
- Gestion des diplômes délivrés
- Gestion des certifications
- Gestion des attestations
- Gestion des équivalences internationales

#### Module alumni
- Base de données des anciens étudiants
- Réseau des anciens
- Gestion des dons des alumni
- Événements alumni

#### Module recherche
- Gestion des projets de recherche
- Gestion des publications
- Gestion des laboratoires
- Gestion des financements recherche

#### Module logistique
- Gestion des transports scolaires
- Gestion de la restauration
- Gestion de l'internat
- Gestion des uniformes

#### Module santé
- Gestion des dossiers médicaux
- Gestion des visites médicales
- Gestion des vaccinations
- Gestion des urgences médicales

#### Module discipline
- Gestion des sanctions
- Gestion des avertissements
- Gestion des commissions disciplinaires
- Gestion des récompenses

#### Autres fonctionnalités
- Emplois du temps
- Cartes étudiantes numériques (QR code)
- Annonces officielles
- Notifications push
- Messagerie interne sécurisée
- Tableau de bord avec statistiques
- Mode hors ligne avec synchronisation
- Export des données (PDF/CSV)
- Gestion des prérequis et équivalences
- Gestion des transferts étudiants
- Gestion des rattrapages

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

La base de données SQLite contient **60+ tables** pour une gestion complète :
- Utilisateurs et profils
- Années académiques, filières, niveaux, classes
- Matières et notes
- Paiements et frais
- Bourses et aides financières
- Candidatures et concours
- Bibliothèque (ouvrages, emprunts, réservations)
- Stages et entreprises
- Infrastructure (salles, équipements, maintenances)
- Ressources humaines (contrats, congés, évaluations)
- Événements et clubs
- Diplômes et certifications
- Alumni
- Recherche et publications
- Transports, restauration, internat
- Santé et discipline
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
