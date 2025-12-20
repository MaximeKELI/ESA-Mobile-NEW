#!/bin/bash

# Script de démarrage du serveur Flask ESA

echo "🚀 Démarrage du serveur Flask ESA..."
echo ""

# Vérifier que Python 3 est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé"
    exit 1
fi

# Vérifier que les dépendances sont installées
echo "📦 Vérification des dépendances..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Installation des dépendances..."
    pip3 install -r requirements.txt
    if [ -f requirements_security.txt ]; then
        pip3 install -r requirements_security.txt
    fi
fi

# Vérifier que la base de données existe
if [ ! -f "database/esa.db" ]; then
    echo "⚠️  Base de données non trouvée. Initialisation..."
    if [ -f "database/init_db.py" ]; then
        python3 database/init_db.py
    else
        echo "⚠️  Script d'initialisation non trouvé. Création de la base vide..."
        sqlite3 database/esa.db "SELECT 1;" 2>/dev/null || touch database/esa.db
    fi
fi

# Démarrer le serveur
echo "✅ Démarrage du serveur sur http://localhost:5000"
echo "   Appuyez sur Ctrl+C pour arrêter"
echo ""

python3 app.py


