# ✅ Résolution de l'Erreur sqlite3.Row

**Date:** 2025-12-19

---

## 🔴 Problème

**Erreur lors de l'inscription:**
```
AttributeError: 'sqlite3.Row' object has no attribute 'get'
```

**Fichier:** `backend/blueprints/auth.py`, ligne 242

---

## 🔍 Cause

`sqlite3.Row` est un objet spécial qui:
- ✅ Supporte l'accès par index: `row[0]`
- ✅ Supporte l'accès par clé: `row['column_name']`
- ❌ **Ne supporte PAS** la méthode `.get()`

Le code utilisait `user.get('telephone')` sur un objet `sqlite3.Row`, ce qui causait l'erreur.

---

## ✅ Solution Appliquée

### Correction

**Avant:**
```python
user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
# user est un sqlite3.Row

user_dict = {
    'telephone': user.get('telephone'),  # ❌ Erreur
    'adresse': user.get('adresse'),      # ❌ Erreur
    ...
}
```

**Après:**
```python
user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
# Convertir sqlite3.Row en dictionnaire
user_dict_row = dict(user)

user_dict = {
    'telephone': user_dict_row.get('telephone'),  # ✅ Fonctionne
    'adresse': user_dict_row.get('adresse'),      # ✅ Fonctionne
    ...
}
```

---

## 📝 Explication Technique

### sqlite3.Row

`sqlite3.Row` est un objet spécial qui permet:
- Accès par index: `row[0]`, `row[1]`
- Accès par nom de colonne: `row['username']`
- Itération: `for key in row.keys()`

Mais **ne supporte pas**:
- ❌ `.get(key)` - Méthode de dictionnaire
- ❌ `.get(key, default)` - Méthode de dictionnaire avec valeur par défaut

### Conversion en Dictionnaire

La solution est de convertir le `Row` en dictionnaire:
```python
user_dict = dict(user)  # Convertit sqlite3.Row en dict
```

Ensuite, on peut utiliser toutes les méthodes de dictionnaire:
- ✅ `.get(key)`
- ✅ `.get(key, default)`
- ✅ `.keys()`
- ✅ `.values()`
- ✅ `.items()`

---

## 🧪 Test

**Redémarrer le serveur:**
```bash
cd backend
python3 app.py
```

**Tester l'inscription:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user_123",
    "email": "test_user_123@example.com",
    "password": "password123",
    "nom": "Test",
    "prenom": "User",
    "role": "etudiant"
  }'
```

**Résultat attendu:**
```json
{
  "message": "Inscription réussie",
  "user": {
    "id": 15,
    "username": "test_user_123",
    "email": "test_user_123@example.com",
    "role": "etudiant",
    "nom": "Test",
    "prenom": "User",
    "telephone": null,
    "adresse": null,
    "photo_path": null,
    "is_active": false,
    "last_login": null
  }
}
```

---

## ✅ Fichier Corrigé

**Fichier:** `backend/blueprints/auth.py`
**Lignes:** 227-248

**Changements:**
- ✅ Ajout de `user_dict_row = dict(user)` pour convertir le Row en dictionnaire
- ✅ Remplacement de `user.get()` par `user_dict_row.get()`
- ✅ Conservation de la logique existante

---

## 📚 Notes

### Autres Solutions Possibles

1. **Accès direct avec try/except:**
```python
try:
    telephone = user['telephone']
except KeyError:
    telephone = None
```

2. **Vérification de l'existence:**
```python
telephone = user['telephone'] if 'telephone' in user.keys() else None
```

3. **Conversion en dictionnaire (choisie):**
```python
user_dict = dict(user)
telephone = user_dict.get('telephone')
```

**La solution 3 est la plus propre et lisible.**

---

## 🎯 Résultat

✅ **Erreur corrigée !**

L'inscription devrait maintenant fonctionner correctement pour tous les rôles (étudiant, parent, enseignant).

---

**🔧 Redémarrer le serveur et tester l'inscription !**


