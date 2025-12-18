#!/bin/bash

# Script pour exécuter tous les tests de sécurité

echo "=========================================="
echo "🔒 TESTS DE SÉCURITÉ - Application ESA"
echo "=========================================="
echo ""

# Vérifier que le serveur est démarré
echo "📡 Vérification du serveur..."
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ Serveur accessible"
else
    echo "❌ Serveur non accessible. Démarrez-le avec: python app.py"
    exit 1
fi

echo ""
echo "🧪 Exécution des tests de pénétration..."
python tests/pentest.py

echo ""
echo "🔍 Exécution des vérifications de sécurité..."
python tests/security_check.py

echo ""
echo "=========================================="
echo "✅ Tests terminés"
echo "=========================================="
echo ""
echo "📄 Consultez les fichiers de résultats:"
echo "   - pentest_results.json"
echo "   - security_check_results.json"

