# 🧪 Tests d'Authentification Flutter

## Scénarios de Test à Vérifier Manuellement

### 1. Tests de Connexion

#### ✅ Connexion Réussie
- [ ] Connexion avec username `admin` / `password123`
- [ ] Connexion avec email `admin@esa.tg` / `password123`
- [ ] Connexion avec différents rôles (comptable, enseignant, étudiant, parent)
- [ ] Vérifier que la navigation vers le dashboard fonctionne
- [ ] Vérifier que le token est sauvegardé

#### ❌ Connexion Échouée
- [ ] Mauvais mot de passe → Message d'erreur affiché
- [ ] Utilisateur inexistant → Message d'erreur affiché
- [ ] Champs vides → Validation affichée
- [ ] Connexion avec compte désactivé → Message approprié

### 2. Tests d'Inscription

#### ✅ Inscription Réussie
- [ ] Inscription étudiant → Compte créé mais inactif
- [ ] Inscription parent → Compte créé et actif
- [ ] Inscription enseignant → Compte créé et actif
- [ ] Inscription avec tous les champs remplis
- [ ] Navigation automatique après inscription réussie

#### ❌ Inscription Échouée
- [ ] Username déjà utilisé → Message d'erreur
- [ ] Email déjà utilisé → Message d'erreur
- [ ] Email invalide → Validation affichée
- [ ] Mot de passe trop court → Validation affichée
- [ ] Mots de passe ne correspondent pas → Message d'erreur
- [ ] Champs obligatoires manquants → Validation affichée

### 3. Tests de Navigation

- [ ] Après connexion réussie → Redirection vers dashboard
- [ ] Après inscription réussie → Redirection vers dashboard (si actif) ou message
- [ ] Après déconnexion → Retour à la page de connexion
- [ ] Navigation entre login et register → Fonctionne dans les deux sens

### 4. Tests de Persistance

- [ ] Fermer et rouvrir l'app → Reste connecté
- [ ] Token expiré → Redirection vers login
- [ ] Refresh token → Fonctionne automatiquement

## Checklist de Test Complète

```
□ Connexion admin réussie
□ Connexion avec email réussie
□ Connexion avec mauvais mot de passe échoue
□ Inscription étudiant réussie
□ Inscription parent réussie
□ Inscription avec username existant échoue
□ Navigation après connexion fonctionne
□ Navigation après inscription fonctionne
□ Persistance de session fonctionne
```

