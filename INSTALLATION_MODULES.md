# 📦 Installation des Nouveaux Modules

## 🚀 Étapes d'Installation

### 1. Mettre à jour la base de données

```bash
cd backend/database

# Appliquer le schéma étendu
sqlite3 esa.db < schema_extended.sql

# Ou utiliser Python
python -c "
import sqlite3
conn = sqlite3.connect('esa.db')
with open('schema_extended.sql', 'r') as f:
    conn.executescript(f.read())
conn.close()
print('Schéma étendu appliqué avec succès')
"
```

### 2. Vérifier les dépendances

Les nouveaux modules utilisent les mêmes dépendances que le projet principal. Vérifiez que `requirements.txt` est à jour :

```bash
cd backend
pip install -r requirements.txt
```

### 3. Redémarrer le serveur

```bash
python app.py
```

Les nouveaux endpoints seront automatiquement disponibles :
- `/api/inscriptions/*`
- `/api/bourses/*`
- `/api/bibliotheque/*`
- `/api/stages/*`
- `/api/infrastructure/*`

## ✅ Vérification

### Tester les nouveaux endpoints

```bash
# 1. Se connecter
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Récupérer le token de la réponse

# 2. Tester les candidatures
curl -X GET http://localhost:5000/api/inscriptions/candidatures \
  -H "Authorization: Bearer VOTRE_TOKEN"

# 3. Tester les bourses
curl -X GET http://localhost:5000/api/bourses/types \
  -H "Authorization: Bearer VOTRE_TOKEN"

# 4. Tester la bibliothèque
curl -X GET http://localhost:5000/api/bibliotheque/ouvrages \
  -H "Authorization: Bearer VOTRE_TOKEN"

# 5. Tester les stages
curl -X GET http://localhost:5000/api/stages/entreprises \
  -H "Authorization: Bearer VOTRE_TOKEN"

# 6. Tester l'infrastructure
curl -X GET http://localhost:5000/api/infrastructure/salles \
  -H "Authorization: Bearer VOTRE_TOKEN"
```

## 📋 Données de Test

### Créer des données de test (optionnel)

```python
# test_data.py
import sqlite3
from datetime import datetime

conn = sqlite3.connect('backend/database/esa.db')
cursor = conn.cursor()

# Type de bourse
cursor.execute("""
    INSERT INTO types_bourses (code, libelle, montant, duree_mois, is_active)
    VALUES ('BOU_MERITE', 'Bourse de mérite', 50000, 12, 1)
""")

# Entreprise
cursor.execute("""
    INSERT INTO entreprises (raison_sociale, secteur_activite, is_active)
    VALUES ('Entreprise Test', 'Technologie', 1)
""")

# Salle
cursor.execute("""
    INSERT INTO salles (code, libelle, type_salle, capacite, is_active)
    VALUES ('SALLE_001', 'Salle de cours 1', 'classe', 30, 1)
""")

conn.commit()
conn.close()
print('Données de test créées')
```

## 🔧 Configuration

Aucune configuration supplémentaire n'est nécessaire. Les modules utilisent la même configuration que l'application principale.

## 📝 Notes

- Tous les modules sont **sécurisés** avec JWT
- Tous les modules respectent le **contrôle d'accès par rôles**
- Tous les modules **journalisent** les actions importantes
- Les **index** sont créés automatiquement pour les performances

## 🐛 Résolution de problèmes

### Erreur : Table already exists
Si vous avez déjà certaines tables, le script SQL peut échouer. Utilisez `CREATE TABLE IF NOT EXISTS` (déjà inclus dans le schéma).

### Erreur : Foreign key constraint failed
Assurez-vous que les données de référence existent (ex: filières, niveaux) avant d'insérer des données liées.

### Erreur : Module not found
Vérifiez que tous les blueprints sont bien importés dans `app.py`.

---

**Les modules sont maintenant prêts à être utilisés ! 🎉**


