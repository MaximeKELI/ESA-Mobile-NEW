# 🚀 Guide de Démarrage du Serveur Backend

## Installation des Dépendances

```bash
cd backend
pip3 install -r requirements.txt
pip3 install -r requirements_security.txt  # Si le fichier existe
```

## Démarrage du Serveur

### Méthode 1 : Script automatique
```bash
./start_server.sh
```

### Méthode 2 : Commande directe
```bash
python3 app.py
```

### Méthode 3 : Avec Flask CLI (recommandé pour développement)
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

## Vérification

Une fois le serveur démarré, testez avec :
```bash
curl http://localhost:5000/api/health
```

Vous devriez recevoir :
```json
{"status": "ok", "message": "ESA API is running"}
```

## Configuration

### Variables d'Environnement (optionnel)

Créez un fichier `.env` dans le dossier `backend/` :

```env
SECRET_KEY=votre-secret-key-production
JWT_SECRET_KEY=votre-jwt-secret-key-production
DATABASE=./database/esa.db
```

## Initialisation de la Base de Données

Si c'est la première fois :

```bash
# Créer le schéma de base
sqlite3 database/esa.db < database/schema.sql

# Ou utiliser le script Python
python3 database/init_db.py
```

## Ports et Accès

- **API** : http://localhost:5000/api
- **Health Check** : http://localhost:5000/api/health
- **Documentation** : À venir (Swagger/OpenAPI)

## Dépannage

### Erreur "ModuleNotFoundError"
```bash
pip3 install -r requirements.txt
```

### Erreur "Database not found"
```bash
mkdir -p database
touch database/esa.db
python3 database/init_db.py
```

### Erreur "Port already in use"
```bash
# Trouver le processus
lsof -i :5000

# Tuer le processus
kill -9 <PID>
```

## Logs

Les logs s'affichent dans la console. Pour la production, configurez un gestionnaire de logs.

