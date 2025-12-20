#!/bin/bash

# Script pour exécuter tous les tests d'authentification

echo "=========================================="
echo "  TESTS D'AUTHENTIFICATION COMPLETS"
echo "=========================================="
echo ""

# Vérifier que le serveur est accessible
echo "🔍 Vérification du serveur..."
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ Serveur accessible"
else
    echo "❌ Serveur non accessible. Démarrez-le avec: python3 app.py"
    exit 1
fi

echo ""
echo "=========================================="
echo "  TEST SIMPLE"
echo "=========================================="
python3 tests/test_auth_simple.py

echo ""
echo "=========================================="
echo "  TEST COMPLET"
echo "=========================================="
python3 tests/test_auth_complet.py

echo ""
echo "=========================================="
echo "  TESTS TERMINÉS"
echo "=========================================="


