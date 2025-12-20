# Backend ESA - Application de Gestion Scolaire

Backend Flask pour l'application de gestion scolaire de l'École Supérieure des Affaires (ESA Togo).

## Installation

1. Créer un environnement virtuel Python :
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Initialiser la base de données :
```bash
cd database
python init_db.py
```

4. Configurer les variables d'environnement :
```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

5. Lancer l'application :
```bash
python app.py
```

L'API sera accessible sur `http://localhost:5000`

## Structure du projet

```
backend/
├── app.py                 # Application Flask principale
├── requirements.txt       # Dépendances Python
├── database/
│   ├── schema.sql        # Schéma de base de données
│   ├── init_db.py        # Script d'initialisation
│   └── esa.db            # Base de données SQLite (générée)
├── blueprints/
│   ├── auth.py           # Authentification
│   ├── admin.py          # Administration
│   ├── comptabilite.py   # Comptabilité
│   ├── enseignant.py     # Enseignants
│   ├── etudiant.py       # Étudiants
│   ├── parent.py         # Parents
│   └── commun.py         # Fonctionnalités communes
├── utils/
│   ├── auth.py           # Utilitaires d'authentification
│   ├── validators.py     # Validateurs de données
│   ├── pdf_generator.py  # Génération de PDF
│   └── qr_code.py        # Génération de QR codes
└── uploads/              # Dossier pour les fichiers uploadés
```

## API Endpoints

### Authentification
- `POST /api/auth/login` - Connexion
- `POST /api/auth/logout` - Déconnexion
- `POST /api/auth/refresh` - Rafraîchir le token
- `POST /api/auth/change-password` - Changer le mot de passe
- `GET /api/auth/me` - Informations utilisateur actuel

### Administration
- `GET /api/admin/users` - Liste des utilisateurs
- `POST /api/admin/users` - Créer un utilisateur
- `GET /api/admin/dashboard/stats` - Statistiques du tableau de bord

### Comptabilité
- `GET /api/comptabilite/paiements` - Liste des paiements
- `POST /api/comptabilite/paiements` - Enregistrer un paiement
- `POST /api/comptabilite/paiements/{id}/validate` - Valider un paiement

### Étudiant
- `GET /api/etudiant/profile` - Profil étudiant
- `GET /api/etudiant/notes` - Notes de l'étudiant
- `GET /api/etudiant/moyennes` - Moyennes de l'étudiant
- `GET /api/etudiant/bulletin` - Bulletin scolaire (PDF)

## Utilisateur par défaut

- Username: `admin`
- Password: `admin123`

**⚠️ IMPORTANT : Changez le mot de passe par défaut en production !**

## Sécurité

- Les mots de passe sont hashés avec SHA-256 (en production, utiliser bcrypt)
- Authentification JWT avec tokens d'accès et de rafraîchissement
- Contrôle d'accès par rôles
- Journalisation des connexions et actions sensibles
- Validation stricte des données

## Tests

```bash
# Tests à venir
pytest tests/
```

## Déploiement

Pour la production :
1. Utiliser un serveur WSGI (Gunicorn, uWSGI)
2. Configurer un reverse proxy (Nginx)
3. Utiliser HTTPS
4. Changer tous les secrets par défaut
5. Utiliser bcrypt pour le hashage des mots de passe
6. Configurer la sauvegarde automatique de la base de données


