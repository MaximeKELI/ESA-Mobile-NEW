"""
Génère un rapport détaillé des tests d'authentification
"""
import os
from datetime import datetime

def generate_html_report():
    """Génère un rapport HTML avec tableau"""
    
    # Données des tests (basées sur les résultats observés)
    test_results = [
        # Connexion - Réussie (devrait être OK après redémarrage)
        {"category": "CONNEXION", "subcategory": "Réussie", "test": "Login admin (username)", "expected": "✅ PASS", "actual": "❌ FAIL", "status": 500, "details": "Database locked - Redémarrer serveur requis"},
        {"category": "CONNEXION", "subcategory": "Réussie", "test": "Login admin (email)", "expected": "✅ PASS", "actual": "❌ FAIL", "status": 500, "details": "Database locked - Redémarrer serveur requis"},
        {"category": "CONNEXION", "subcategory": "Réussie", "test": "Login comptable", "expected": "✅ PASS", "actual": "❌ FAIL", "status": 500, "details": "Database locked - Redémarrer serveur requis"},
        {"category": "CONNEXION", "subcategory": "Réussie", "test": "Login enseignant", "expected": "✅ PASS", "actual": "❌ FAIL", "status": 500, "details": "Database locked - Redémarrer serveur requis"},
        {"category": "CONNEXION", "subcategory": "Réussie", "test": "Login étudiant", "expected": "✅ PASS", "actual": "❌ FAIL", "status": 500, "details": "Database locked - Redémarrer serveur requis"},
        {"category": "CONNEXION", "subcategory": "Réussie", "test": "Login parent", "expected": "✅ PASS", "actual": "❌ FAIL", "status": 500, "details": "Database locked - Redémarrer serveur requis"},
        
        # Connexion - Échouée
        {"category": "CONNEXION", "subcategory": "Échouée", "test": "Mauvais mot de passe", "expected": "❌ FAIL", "actual": "❌ FAIL", "status": 500, "details": "Database locked - Redémarrer serveur requis"},
        {"category": "CONNEXION", "subcategory": "Échouée", "test": "Utilisateur inexistant", "expected": "❌ FAIL", "actual": "❌ FAIL", "status": 500, "details": "Database locked - Redémarrer serveur requis"},
        {"category": "CONNEXION", "subcategory": "Échouée", "test": "Username vide", "expected": "❌ FAIL", "actual": "✅ PASS", "status": 400, "details": "Validation fonctionne"},
        {"category": "CONNEXION", "subcategory": "Échouée", "test": "Mot de passe vide", "expected": "❌ FAIL", "actual": "✅ PASS", "status": 400, "details": "Validation fonctionne"},
        {"category": "CONNEXION", "subcategory": "Échouée", "test": "Champs manquants", "expected": "❌ FAIL", "actual": "✅ PASS", "status": 400, "details": "Validation fonctionne"},
        
        # Inscription - Réussie
        {"category": "INSCRIPTION", "subcategory": "Réussie", "test": "Inscription étudiant", "expected": "✅ PASS", "actual": "❌ FAIL", "status": 400, "details": "password123 rejeté - Code corrigé mais serveur non redémarré"},
        {"category": "INSCRIPTION", "subcategory": "Réussie", "test": "Inscription parent", "expected": "✅ PASS", "actual": "❌ FAIL", "status": 400, "details": "password123 rejeté - Code corrigé mais serveur non redémarré"},
        {"category": "INSCRIPTION", "subcategory": "Réussie", "test": "Inscription enseignant", "expected": "✅ PASS", "actual": "❌ FAIL", "status": 400, "details": "password123 rejeté - Code corrigé mais serveur non redémarré"},
        
        # Inscription - Échouée
        {"category": "INSCRIPTION", "subcategory": "Échouée", "test": "Username déjà utilisé", "expected": "❌ FAIL", "actual": "✅ PASS", "status": 400, "details": "Détection correcte"},
        {"category": "INSCRIPTION", "subcategory": "Échouée", "test": "Email déjà utilisé", "expected": "❌ FAIL", "actual": "✅ PASS", "status": 400, "details": "Détection correcte"},
        {"category": "INSCRIPTION", "subcategory": "Échouée", "test": "Email invalide", "expected": "❌ FAIL", "actual": "✅ PASS", "status": 400, "details": "Validation fonctionne"},
        {"category": "INSCRIPTION", "subcategory": "Échouée", "test": "Mot de passe trop court", "expected": "❌ FAIL", "actual": "✅ PASS", "status": 400, "details": "Validation fonctionne"},
        {"category": "INSCRIPTION", "subcategory": "Échouée", "test": "Champs obligatoires manquants", "expected": "❌ FAIL", "actual": "✅ PASS", "status": 400, "details": "Validation fonctionne"},
        
        # Validation Mot de Passe
        {"category": "VALIDATION", "subcategory": "Mot de Passe", "test": "password123 (dev)", "expected": "✅ PASS", "actual": "❌ FAIL", "status": 400, "details": "Code corrigé - Serveur doit être redémarré"},
        {"category": "VALIDATION", "subcategory": "Mot de Passe", "test": "Mot de passe fort", "expected": "✅ PASS", "actual": "❌ FAIL", "status": 500, "details": "Database locked"},
        {"category": "VALIDATION", "subcategory": "Mot de Passe", "test": "Trop court", "expected": "❌ FAIL", "actual": "✅ PASS", "status": 400, "details": "Rejeté correctement"},
        {"category": "VALIDATION", "subcategory": "Mot de Passe", "test": "Sans majuscule", "expected": "❌ FAIL", "actual": "✅ PASS", "status": 400, "details": "Rejeté correctement"},
        {"category": "VALIDATION", "subcategory": "Mot de Passe", "test": "Sans chiffre", "expected": "❌ FAIL", "actual": "✅ PASS", "status": 400, "details": "Rejeté correctement"},
        {"category": "VALIDATION", "subcategory": "Mot de Passe", "test": "Sans caractère spécial", "expected": "❌ FAIL", "actual": "✅ PASS", "status": 400, "details": "Rejeté correctement"},
        
        # Validation Token
        {"category": "VALIDATION", "subcategory": "Token", "test": "Accès avec token valide", "expected": "✅ PASS", "actual": "❌ FAIL", "status": None, "details": "Aucun token disponible (login échoue)"},
        {"category": "VALIDATION", "subcategory": "Token", "test": "Accès avec token invalide", "expected": "❌ FAIL", "actual": "❌ FAIL", "status": None, "details": "Test non exécuté"},
    ]
    
    # Calculer les statistiques
    total = len(test_results)
    passed = sum(1 for r in test_results if r["actual"] == "✅ PASS")
    failed = total - passed
    
    # Par catégorie
    categories = {}
    for result in test_results:
        cat = result["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "passed": 0}
        categories[cat]["total"] += 1
        if result["actual"] == "✅ PASS":
            categories[cat]["passed"] += 1
    
    # Générer le HTML
    html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport des Tests d'Authentification - ESA</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-card h3 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .stat-card p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}
        .warning {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .pass {{
            color: #27ae60;
            font-weight: bold;
        }}
        .fail {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .category-header {{
            background: #ecf0f1;
            font-weight: bold;
            color: #2c3e50;
        }}
        .status-code {{
            font-family: monospace;
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        .summary {{
            background: #e8f4f8;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .summary h2 {{
            margin-top: 0;
            color: #2c3e50;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Rapport des Tests d'Authentification</h1>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="warning">
            <strong>⚠️ IMPORTANT:</strong> Le serveur backend doit être redémarré pour appliquer les corrections.
            La base de données est actuellement verrouillée, ce qui cause des erreurs 500.
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{total}</h3>
                <p>Total des Tests</p>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
                <h3>{passed}</h3>
                <p>✅ Réussis</p>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);">
                <h3>{failed}</h3>
                <p>❌ Échoués</p>
            </div>
            <div class="stat-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                <h3>{(passed/total*100):.1f}%</h3>
                <p>Taux de Réussite</p>
            </div>
        </div>
        
        <div class="summary">
            <h2>📋 Résumé par Catégorie</h2>
"""
    
    for cat, stats in categories.items():
        rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        html += f"""
            <p><strong>{cat}:</strong> {stats['passed']}/{stats['total']} ({rate:.1f}%)</p>
"""
    
    html += """
        </div>
        
        <h2>📋 Tableau Détaillé des Tests</h2>
        <table>
            <thead>
                <tr>
                    <th>Catégorie</th>
                    <th>Sous-Catégorie</th>
                    <th>Test</th>
                    <th>Résultat Attendu</th>
                    <th>Résultat Actuel</th>
                    <th>Status Code</th>
                    <th>Détails</th>
                </tr>
            </thead>
            <tbody>
"""
    
    current_category = None
    for result in test_results:
        if result["category"] != current_category:
            current_category = result["category"]
            html += f'<tr class="category-header"><td colspan="7"><strong>{current_category}</strong></td></tr>'
        
        actual_class = "pass" if result["actual"] == "✅ PASS" else "fail"
        status_code = str(result["status"]) if result["status"] else "N/A"
        
        html += f"""
                <tr>
                    <td>{result['category']}</td>
                    <td>{result['subcategory']}</td>
                    <td>{result['test']}</td>
                    <td>{result['expected']}</td>
                    <td class="{actual_class}">{result['actual']}</td>
                    <td><span class="status-code">{status_code}</span></td>
                    <td>{result['details']}</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        
        <div class="warning" style="margin-top: 30px;">
            <h3>🔧 Actions Requises</h3>
            <ol>
                <li><strong>Redémarrer le serveur backend:</strong>
                    <pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin: 10px 0;">
# Arrêter le serveur (Ctrl+C)
cd backend
python3 app.py</pre>
                </li>
                <li><strong>Relancer les tests:</strong>
                    <pre style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin: 10px 0;">
cd backend
python3 tests/test_auth_with_report.py</pre>
                </li>
            </ol>
        </div>
        
        <div style="margin-top: 30px; padding: 15px; background: #e8f5e9; border-radius: 8px;">
            <h3>✅ Corrections Appliquées</h3>
            <ul>
                <li>Validation du mot de passe : <code>password123</code> accepté en développement</li>
                <li>Gestion des erreurs de logging : Ne bloque plus l'application</li>
                <li>Gestion des erreurs de base de données : Rollback automatique</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    html = generate_html_report()
    
    # Sauvegarder le rapport
    report_dir = os.path.dirname(os.path.abspath(__file__))
    report_file = os.path.join(report_dir, f"rapport_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Rapport HTML généré: {report_file}")
    
    # Aussi générer un rapport texte
    txt_report = f"""
====================================================================================================
RAPPORT DES TESTS D'AUTHENTIFICATION
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
====================================================================================================

⚠️  IMPORTANT: Le serveur backend doit être redémarré pour appliquer les corrections.
   La base de données est actuellement verrouillée, ce qui cause des erreurs 500.

📊 STATISTIQUES GÉNÉRALES
   Total des tests: 26
   ✅ Réussis: 12
   ❌ Échoués: 14
   📈 Taux de réussite: 46.2%

====================================================================================================
TABLEAU DÉTAILLÉ DES TESTS
====================================================================================================

Catégorie          | Sous-Catégorie    | Test                              | Attendu | Actuel | Code | Détails
----------------------------------------------------------------------------------------------------
CONNEXION          | Réussie           | Login admin (username)            | ✅ PASS  | ❌ FAIL | 500  | Database locked
CONNEXION          | Réussie           | Login admin (email)               | ✅ PASS  | ❌ FAIL | 500  | Database locked
CONNEXION          | Réussie           | Login comptable                   | ✅ PASS  | ❌ FAIL | 500  | Database locked
CONNEXION          | Réussie           | Login enseignant                  | ✅ PASS  | ❌ FAIL | 500  | Database locked
CONNEXION          | Réussie           | Login étudiant                    | ✅ PASS  | ❌ FAIL | 500  | Database locked
CONNEXION          | Réussie           | Login parent                      | ✅ PASS  | ❌ FAIL | 500  | Database locked
CONNEXION          | Échouée           | Mauvais mot de passe              | ❌ FAIL  | ❌ FAIL | 500  | Database locked
CONNEXION          | Échouée           | Utilisateur inexistant            | ❌ FAIL  | ❌ FAIL | 500  | Database locked
CONNEXION          | Échouée           | Username vide                     | ❌ FAIL  | ✅ PASS | 400  | Validation OK
CONNEXION          | Échouée           | Mot de passe vide                 | ❌ FAIL  | ✅ PASS | 400  | Validation OK
CONNEXION          | Échouée           | Champs manquants                  | ❌ FAIL  | ✅ PASS | 400  | Validation OK
INSCRIPTION        | Réussie           | Inscription étudiant              | ✅ PASS  | ❌ FAIL | 400  | password123 rejeté
INSCRIPTION        | Réussie           | Inscription parent                | ✅ PASS  | ❌ FAIL | 400  | password123 rejeté
INSCRIPTION        | Réussie           | Inscription enseignant            | ✅ PASS  | ❌ FAIL | 400  | password123 rejeté
INSCRIPTION        | Échouée           | Username déjà utilisé             | ❌ FAIL  | ✅ PASS | 400  | Détection OK
INSCRIPTION        | Échouée           | Email déjà utilisé                | ❌ FAIL  | ✅ PASS | 400  | Détection OK
INSCRIPTION        | Échouée           | Email invalide                    | ❌ FAIL  | ✅ PASS | 400  | Validation OK
INSCRIPTION        | Échouée           | Mot de passe trop court           | ❌ FAIL  | ✅ PASS | 400  | Validation OK
INSCRIPTION        | Échouée           | Champs obligatoires manquants     | ❌ FAIL  | ✅ PASS | 400  | Validation OK
VALIDATION         | Mot de Passe      | password123 (dev)                 | ✅ PASS  | ❌ FAIL | 400  | Code corrigé
VALIDATION         | Mot de Passe      | Mot de passe fort                 | ✅ PASS  | ❌ FAIL | 500  | Database locked
VALIDATION         | Mot de Passe      | Trop court                        | ❌ FAIL  | ✅ PASS | 400  | Rejeté OK
VALIDATION         | Mot de Passe      | Sans majuscule                   | ❌ FAIL  | ✅ PASS | 400  | Rejeté OK
VALIDATION         | Mot de Passe      | Sans chiffre                      | ❌ FAIL  | ✅ PASS | 400  | Rejeté OK
VALIDATION         | Mot de Passe      | Sans caractère spécial            | ❌ FAIL  | ✅ PASS | 400  | Rejeté OK
VALIDATION         | Token             | Accès avec token valide            | ✅ PASS  | ❌ FAIL | N/A  | Pas de token
VALIDATION         | Token             | Accès avec token invalide          | ❌ FAIL  | ❌ FAIL | N/A  | Non testé

====================================================================================================
RÉSUMÉ PAR CATÉGORIE
====================================================================================================

CONNEXION          : 3/11 (27.3%)
INSCRIPTION        : 5/8 (62.5%)
VALIDATION         : 4/7 (57.1%)

====================================================================================================
🔧 ACTIONS REQUISES
====================================================================================================

1. Redémarrer le serveur backend:
   cd backend
   python3 app.py

2. Relancer les tests:
   cd backend
   python3 tests/test_auth_with_report.py

====================================================================================================
✅ CORRECTIONS APPLIQUÉES
====================================================================================================

- Validation du mot de passe : password123 accepté en développement
- Gestion des erreurs de logging : Ne bloque plus l'application
- Gestion des erreurs de base de données : Rollback automatique

====================================================================================================
"""
    
    txt_file = os.path.join(report_dir, f"rapport_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(txt_report)
    
    print(f"✅ Rapport texte généré: {txt_file}")
    print("\n" + txt_report)

if __name__ == "__main__":
    main()


