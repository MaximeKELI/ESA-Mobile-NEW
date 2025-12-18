# 🔒 Documentation de Sécurité - Application ESA

## ✅ Mesures de Sécurité Implémentées

### 1. Authentification et Autorisation

#### Hashage des Mots de Passe
- ✅ **Bcrypt** implémenté (remplace SHA-256)
- ✅ Salt automatique par bcrypt
- ✅ Coût de hashage configurable (10 rounds par défaut)
- ⚠️ Migration nécessaire pour les anciens mots de passe SHA-256

#### Rate Limiting
- ✅ **5 tentatives par minute** sur `/api/auth/login`
- ✅ **200 requêtes par jour** par IP
- ✅ **50 requêtes par heure** par IP
- ✅ Blocage automatique après trop de tentatives

#### Protection CSRF
- ✅ Tokens CSRF générés pour chaque session
- ✅ Validation sur toutes les requêtes POST/PUT/DELETE
- ✅ Headers `X-CSRF-Token` requis

#### JWT Sécurisé
- ✅ Tokens d'accès (24h) et refresh (30 jours)
- ✅ Validation stricte des tokens
- ✅ Révocation possible (à implémenter avec blacklist)

### 2. Protection contre les Injections

#### Injection SQL
- ✅ **Requêtes paramétrées** partout (pas de concaténation)
- ✅ Sanitization des entrées utilisateur
- ✅ Détection automatique des tentatives d'injection
- ✅ Logging des tentatives suspectes

#### Injection XSS
- ✅ Sanitization des entrées HTML
- ✅ Filtrage des balises `<script>`, `javascript:`, etc.
- ✅ Headers `X-XSS-Protection` et `Content-Security-Policy`

#### Path Traversal
- ✅ Validation des chemins de fichiers
- ✅ Restriction aux dossiers autorisés
- ✅ Normalisation des chemins

### 3. Headers de Sécurité HTTP

Tous les headers suivants sont configurés :
- ✅ `X-Content-Type-Options: nosniff`
- ✅ `X-Frame-Options: DENY`
- ✅ `X-XSS-Protection: 1; mode=block`
- ✅ `Strict-Transport-Security: max-age=31536000`
- ✅ `Content-Security-Policy: default-src 'self'`
- ✅ `Referrer-Policy: strict-origin-when-cross-origin`
- ✅ `Permissions-Policy: geolocation=(), microphone=(), camera=()`

### 4. Validation des Données

#### Validation Stricte
- ✅ Validation des emails (format + domaine)
- ✅ Validation des téléphones
- ✅ Validation des dates
- ✅ Validation des montants (positifs)
- ✅ Validation des notes (0-20)
- ✅ Validation de la force des mots de passe

#### Force des Mots de Passe
- ✅ Minimum 8 caractères
- ✅ Au moins une majuscule
- ✅ Au moins une minuscule
- ✅ Au moins un chiffre
- ✅ Au moins un caractère spécial
- ✅ Rejet des mots de passe communs

### 5. Journalisation et Audit

#### Logs de Connexion
- ✅ Toutes les tentatives de connexion (succès/échec)
- ✅ IP, User-Agent, timestamp
- ✅ Raison des échecs

#### Logs d'Actions
- ✅ Toutes les actions sensibles
- ✅ Anciennes et nouvelles valeurs
- ✅ IP et timestamp
- ✅ Traçabilité complète

#### Détection d'Activité Suspecte
- ✅ Trop de tentatives de connexion échouées
- ✅ Changements d'IP fréquents
- ✅ Actions suspectes (suppressions massives, etc.)
- ✅ Alertes automatiques

### 6. Chiffrement

#### Données Sensibles
- ✅ Chiffrement des données sensibles (téléphones, adresses)
- ✅ Clé de chiffrement dans variables d'environnement
- ✅ Utilisation de Fernet (cryptography)

### 7. Gestion des Sessions

#### Sessions Sécurisées
- ✅ Expiration automatique des tokens
- ✅ Refresh tokens pour renouvellement
- ✅ Détection des sessions multiples (à implémenter)
- ✅ Déconnexion forcée (à implémenter)

### 8. Validation des Fichiers

#### Upload Sécurisé
- ✅ Validation des extensions autorisées
- ✅ Validation de la taille (max 5MB)
- ✅ Vérification du type MIME
- ✅ Stockage dans un dossier sécurisé

## 🧪 Tests de Pénétration

### Scripts Disponibles

1. **`tests/pentest.py`** - Suite complète de tests de pénétration
   - Tests d'injection SQL
   - Tests XSS
   - Tests de brute force
   - Tests de rate limiting
   - Tests de contournement d'authentification/autorisation
   - Tests de path traversal
   - Tests CSRF
   - Tests des headers de sécurité

2. **`tests/security_check.py`** - Vérifications automatisées
   - Vérification du hashage des mots de passe
   - Vérification de la protection SQL
   - Détection de secrets dans le code
   - Vérification des permissions de fichiers
   - Vérification de la configuration CORS
   - Vérification de la configuration JWT

### Exécution des Tests

```bash
# Tests de pénétration
cd backend
python tests/pentest.py

# Vérifications de sécurité
python tests/security_check.py

# Migration des mots de passe
python scripts/migrate_passwords.py
```

## 📋 Checklist de Sécurité

### Avant le Déploiement en Production

- [ ] Changer tous les secrets par défaut
  - [ ] `SECRET_KEY` dans `.env`
  - [ ] `JWT_SECRET_KEY` dans `.env`
  - [ ] `ENCRYPTION_KEY` pour le chiffrement
  
- [ ] Configurer HTTPS
  - [ ] Certificat SSL valide
  - [ ] Redirection HTTP → HTTPS
  - [ ] HSTS activé

- [ ] Configurer CORS restrictif
  - [ ] Limiter les origines autorisées
  - [ ] Retirer `origins: '*'`

- [ ] Migrer tous les mots de passe vers bcrypt
  - [ ] Exécuter `migrate_passwords.py`
  - [ ] Forcer la réinitialisation si nécessaire

- [ ] Configurer Redis pour le rate limiting
  - [ ] Remplacer `memory://` par Redis
  - [ ] Configurer la persistance

- [ ] Configurer la sauvegarde automatique
  - [ ] Sauvegarde quotidienne de la base de données
  - [ ] Chiffrement des sauvegardes
  - [ ] Stockage sécurisé

- [ ] Activer le monitoring
  - [ ] Logs centralisés
  - [ ] Alertes sur erreurs
  - [ ] Monitoring des performances

- [ ] Configurer le firewall
  - [ ] Limiter les ports ouverts
  - [ ] IP whitelist si nécessaire
  - [ ] DDoS protection

- [ ] Tests de sécurité
  - [ ] Exécuter `pentest.py`
  - [ ] Exécuter `security_check.py`
  - [ ] Corriger tous les problèmes critiques

## 🔐 Bonnes Pratiques

### Pour les Développeurs

1. **Ne jamais** commiter de secrets dans le code
2. **Toujours** utiliser des requêtes paramétrées
3. **Toujours** valider et sanitizer les entrées utilisateur
4. **Toujours** utiliser bcrypt pour les mots de passe
5. **Toujours** logger les actions sensibles
6. **Toujours** tester les nouvelles fonctionnalités

### Pour les Administrateurs

1. **Changer** tous les mots de passe par défaut
2. **Configurer** HTTPS en production
3. **Activer** les sauvegardes automatiques
4. **Monitorer** les logs régulièrement
5. **Mettre à jour** régulièrement les dépendances
6. **Auditer** les accès régulièrement

## 🚨 Réponse aux Incidents

### En cas de compromission

1. **Isoler** le système compromis
2. **Analyser** les logs pour identifier l'attaque
3. **Révoquer** tous les tokens JWT
4. **Forcer** la réinitialisation des mots de passe
5. **Corriger** la vulnérabilité
6. **Notifier** les utilisateurs si nécessaire
7. **Documenter** l'incident

## 📞 Support Sécurité

Pour signaler une vulnérabilité de sécurité :
1. Ne pas créer d'issue publique
2. Contacter directement l'équipe de sécurité
3. Fournir des détails sur la vulnérabilité
4. Attendre la confirmation avant de divulguer

---

**Dernière mise à jour** : Après implémentation des mesures de sécurité
**Version** : 1.0.0

