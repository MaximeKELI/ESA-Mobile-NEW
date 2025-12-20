# 🔧 Correction de l'Erreur d'Inscription

**Date:** 2025-12-19

---

## 🔴 Problème Identifié

**Erreur:**
```
AttributeError: 'sqlite3.Row' object has no attribute 'get'
```

**Localisation:** `backend/blueprints/auth.py`, ligne 242

**Cause:** `sqlite3.Row` n'a pas de méthode `.get()`. Il faut utiliser l'accès direct ou convertir en dictionnaire.

---

## ✅ Solution Appliquée

### Avant (Erreur)
```python
user_dict = {
    'id': user['id'],
    'username': user['username'],
    ...
    'telephone': user.get('telephone'),  # ❌ Erreur: sqlite3.Row n'a pas .get()
    'adresse': user.get('adresse'),
    ...
}
```

### Après (Corrigé)
```python
# Convertir sqlite3.Row en dictionnaire pour faciliter l'accès
user_dict_row = dict(user)

user_dict = {
    'id': user_dict_row['id'],
    'username': user_dict_row['username'],
    ...
    'telephone': user_dict_row.get('telephone'),  # ✅ Fonctionne avec dict
    'adresse': user_dict_row.get('adresse'),
    ...
}
```

---

## 📝 Explication

`sqlite3.Row` est un objet spécial qui permet l'accès par index ou par clé avec `[]`, mais ne supporte pas la méthode `.get()`. 

**Solutions possibles:**
1. ✅ **Convertir en dictionnaire** (choisi) : `dict(user)` - Plus simple et lisible
2. Utiliser l'accès direct : `user['telephone']` avec try/except
3. Vérifier l'existence : `user['telephone'] if 'telephone' in user.keys() else None`

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
    "username": "test_user",
    "email": "test@example.com",
    "password": "password123",
    "nom": "Test",
    "prenom": "User",
    "role": "etudiant"
  }'
```

**Résultat attendu:** Status 201 avec l'utilisateur créé

---

## ✅ Correction Appliquée

- ✅ Conversion de `sqlite3.Row` en dictionnaire
- ✅ Utilisation de `.get()` sur le dictionnaire
- ✅ Gestion des valeurs optionnelles (telephone, adresse, etc.)

---

**🔧 Erreur corrigée ! Redémarrer le serveur et tester.**


