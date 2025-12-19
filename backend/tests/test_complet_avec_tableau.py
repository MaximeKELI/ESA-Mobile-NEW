"""
Tests complets avec génération de rapport en tableau
"""
import requests
import json
from datetime import datetime
from typing import Dict, List

BASE_URL = "http://localhost:5000/api"

class TestResult:
    def __init__(self, category: str, test_name: str, success: bool, status_code: int = None, details: str = ""):
        self.category = category
        self.test_name = test_name
        self.success = success
        self.status_code = status_code
        self.details = details

class TestRunner:
    def __init__(self):
        self.results: List[TestResult] = []
        self.tokens = {}
        self.created_users = []
    
    def test_connection(self):
        """Tests de connexion"""
        test_cases = [
            {"name": "Login admin (username)", "data": {"username": "admin", "password": "password123"}, "expected": 200},
            {"name": "Login admin (email)", "data": {"username": "admin@esa.tg", "password": "password123"}, "expected": 200},
            {"name": "Login comptable", "data": {"username": "comptable", "password": "password123"}, "expected": 200},
            {"name": "Login enseignant", "data": {"username": "enseignant1", "password": "password123"}, "expected": 200},
            {"name": "Login étudiant", "data": {"username": "etudiant1", "password": "password123"}, "expected": 200},
            {"name": "Login parent", "data": {"username": "parent1", "password": "password123"}, "expected": 200},
            {"name": "Mauvais mot de passe", "data": {"username": "admin", "password": "wrong"}, "expected": 401},
            {"name": "Utilisateur inexistant", "data": {"username": "inexistant", "password": "password123"}, "expected": 401},
            {"name": "Username vide", "data": {"username": "", "password": "password123"}, "expected": 400},
            {"name": "Mot de passe vide", "data": {"username": "admin", "password": ""}, "expected": 400},
            {"name": "Champs manquants", "data": {"username": "admin"}, "expected": 400},
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/login",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                success = response.status_code == test_case["expected"]
                details = ""
                
                if success and response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.tokens[test_case["data"]["username"]] = data["access_token"]
                        details = "Token obtenu"
                    else:
                        details = "Token manquant"
                elif response.status_code < 500:
                    try:
                        error = response.json().get("error", "")
                        details = error if error else f"Status {response.status_code}"
                    except:
                        details = f"Status {response.status_code}"
                else:
                    details = f"Erreur serveur {response.status_code}"
                
                self.results.append(TestResult(
                    "CONNEXION",
                    test_case["name"],
                    success,
                    response.status_code,
                    details
                ))
            except Exception as e:
                self.results.append(TestResult(
                    "CONNEXION",
                    test_case["name"],
                    False,
                    None,
                    f"Exception: {str(e)[:50]}"
                ))
    
    def test_inscription(self):
        """Tests d'inscription"""
        timestamp = int(datetime.now().timestamp())
        
        test_cases = [
            {
                "name": "Inscription étudiant",
                "data": {
                    "username": f"etudiant_test_{timestamp}",
                    "email": f"etudiant_test_{timestamp}@test.com",
                    "password": "password123",
                    "nom": "Test",
                    "prenom": "Étudiant",
                    "role": "etudiant"
                },
                "expected": 201
            },
            {
                "name": "Inscription parent",
                "data": {
                    "username": f"parent_test_{timestamp}",
                    "email": f"parent_test_{timestamp}@test.com",
                    "password": "password123",
                    "nom": "Test",
                    "prenom": "Parent",
                    "role": "parent"
                },
                "expected": 201
            },
            {
                "name": "Inscription enseignant",
                "data": {
                    "username": f"enseignant_test_{timestamp}",
                    "email": f"enseignant_test_{timestamp}@test.com",
                    "password": "password123",
                    "nom": "Test",
                    "prenom": "Enseignant",
                    "role": "enseignant"
                },
                "expected": 201
            },
            {
                "name": "Username déjà utilisé",
                "data": {
                    "username": "admin",
                    "email": f"new_{timestamp}@test.com",
                    "password": "password123",
                    "nom": "Test",
                    "prenom": "User",
                    "role": "etudiant"
                },
                "expected": 400
            },
            {
                "name": "Email invalide",
                "data": {
                    "username": f"invalid_email_{timestamp}",
                    "email": "email-invalide",
                    "password": "password123",
                    "nom": "Test",
                    "prenom": "User",
                    "role": "etudiant"
                },
                "expected": 400
            },
            {
                "name": "Champs obligatoires manquants",
                "data": {
                    "username": f"missing_{timestamp}",
                    "email": f"missing_{timestamp}@test.com",
                    "password": "password123",
                    "role": "etudiant"
                },
                "expected": 400
            },
        ]
        
        for test_case in test_cases:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/register",
                    json=test_case["data"],
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                
                success = response.status_code == test_case["expected"]
                details = ""
                
                if success and response.status_code == 201:
                    try:
                        data = response.json()
                        self.created_users.append(test_case["data"]["username"])
                        user_data = data.get('user', {})
                        details = f"Utilisateur créé - Role: {user_data.get('role')}, Active: {user_data.get('is_active')}"
                    except:
                        details = "Utilisateur créé"
                elif response.status_code < 500:
                    try:
                        error = response.json().get("error", "")
                        error_details = response.json().get("details", [])
                        details = f"{error}" + (f" - {error_details}" if error_details else "")
                    except:
                        details = f"Status {response.status_code}"
                else:
                    details = f"Erreur serveur {response.status_code}"
                
                self.results.append(TestResult(
                    "INSCRIPTION",
                    test_case["name"],
                    success,
                    response.status_code,
                    details
                ))
                
                timestamp += 1  # Pour éviter les conflits
            except Exception as e:
                self.results.append(TestResult(
                    "INSCRIPTION",
                    test_case["name"],
                    False,
                    None,
                    f"Exception: {str(e)[:50]}"
                ))
    
    def generate_table_report(self) -> str:
        """Génère un rapport en format tableau"""
        report = []
        report.append("=" * 120)
        report.append("RAPPORT DES TESTS D'AUTHENTIFICATION")
        report.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 120)
        report.append("")
        
        # Statistiques générales
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        report.append("📊 STATISTIQUES GÉNÉRALES")
        report.append("-" * 120)
        report.append(f"Total des tests        : {total}")
        report.append(f"✅ Réussis             : {passed}")
        report.append(f"❌ Échoués             : {failed}")
        report.append(f"📈 Taux de réussite    : {success_rate:.1f}%")
        report.append("")
        
        # Statistiques par catégorie
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {"total": 0, "passed": 0, "failed": 0}
            categories[result.category]["total"] += 1
            if result.success:
                categories[result.category]["passed"] += 1
            else:
                categories[result.category]["failed"] += 1
        
        report.append("📊 STATISTIQUES PAR CATÉGORIE")
        report.append("-" * 120)
        report.append(f"{'Catégorie':<20} | {'Total':<8} | {'Réussis':<8} | {'Échoués':<8} | {'Taux':<10}")
        report.append("-" * 120)
        for cat, stats in categories.items():
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            report.append(f"{cat:<20} | {stats['total']:<8} | {stats['passed']:<8} | {stats['failed']:<8} | {rate:>6.1f}%")
        report.append("")
        
        # Tableau détaillé
        report.append("📋 TABLEAU DÉTAILLÉ DES TESTS")
        report.append("-" * 120)
        report.append(f"{'Catégorie':<15} | {'Test':<45} | {'Résultat':<10} | {'Code':<6} | {'Détails'}")
        report.append("-" * 120)
        
        for result in self.results:
            status_icon = "✅ PASS" if result.success else "❌ FAIL"
            status_code = str(result.status_code) if result.status_code else "N/A"
            details_short = result.details[:30] if result.details else ""
            
            report.append(f"{result.category:<15} | {result.test_name:<45} | {status_icon:<10} | {status_code:<6} | {details_short}")
        
        report.append("")
        report.append("=" * 120)
        
        return "\n".join(report)
    
    def generate_html_table(self) -> str:
        """Génère un rapport HTML avec tableau"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.success)
        failed = total - passed
        success_rate = (passed / total * 100) if total > 0 else 0
        
        # Statistiques par catégorie
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {"total": 0, "passed": 0, "failed": 0}
            categories[result.category]["total"] += 1
            if result.success:
                categories[result.category]["passed"] += 1
            else:
                categories[result.category]["failed"] += 1
        
        html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rapport des Tests - ESA</title>
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
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Rapport des Tests d'Authentification</h1>
        <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
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
                <h3>{success_rate:.1f}%</h3>
                <p>Taux de Réussite</p>
            </div>
        </div>
        
        <h2>📊 Statistiques par Catégorie</h2>
        <table>
            <thead>
                <tr>
                    <th>Catégorie</th>
                    <th>Total</th>
                    <th>Réussis</th>
                    <th>Échoués</th>
                    <th>Taux de Réussite</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for cat, stats in categories.items():
            rate = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
            html += f"""
                <tr>
                    <td><strong>{cat}</strong></td>
                    <td>{stats['total']}</td>
                    <td class="pass">{stats['passed']}</td>
                    <td class="fail">{stats['failed']}</td>
                    <td>{rate:.1f}%</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
        
        <h2>📋 Tableau Détaillé des Tests</h2>
        <table>
            <thead>
                <tr>
                    <th>Catégorie</th>
                    <th>Test</th>
                    <th>Résultat</th>
                    <th>Status Code</th>
                    <th>Détails</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for result in self.results:
            status_class = "pass" if result.success else "fail"
            status_text = "✅ PASS" if result.success else "❌ FAIL"
            status_code = str(result.status_code) if result.status_code else "N/A"
            
            html += f"""
                <tr>
                    <td>{result.category}</td>
                    <td>{result.test_name}</td>
                    <td class="{status_class}">{status_text}</td>
                    <td>{status_code}</td>
                    <td>{result.details[:50] if result.details else ''}</td>
                </tr>
"""
        
        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        
        return html
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("🔍 Vérification du serveur...")
        try:
            test_response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": "test", "password": "test"},
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            print("✅ Serveur accessible\n")
        except:
            print("❌ Serveur non accessible. Démarrez-le avec: python3 app.py\n")
            return False
        
        print("🧪 Exécution des tests...")
        print("   - Tests de connexion...")
        self.test_connection()
        
        print("   - Tests d'inscription...")
        self.test_inscription()
        
        print("\n✅ Tous les tests sont terminés\n")
        return True

def main():
    runner = TestRunner()
    
    if runner.run_all_tests():
        # Générer rapport texte
        report = runner.generate_table_report()
        print(report)
        
        # Sauvegarder rapport texte
        import os
        report_dir = os.path.dirname(os.path.abspath(__file__))
        txt_file = os.path.join(report_dir, f"rapport_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 Rapport texte sauvegardé: {txt_file}")
        
        # Générer et sauvegarder rapport HTML
        html_report = runner.generate_html_table()
        html_file = os.path.join(report_dir, f"rapport_tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        print(f"📄 Rapport HTML sauvegardé: {html_file}")

if __name__ == "__main__":
    main()

