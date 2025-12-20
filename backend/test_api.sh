#!/bin/bash

# Script de test rapide de l'API ESA

BASE_URL="http://localhost:5000/api"

echo "🧪 Tests de l'API ESA"
echo "===================="
echo ""

# Test 1: Health Check
echo "1️⃣  Test Health Check..."
response=$(curl -s -w "\n%{http_code}" "$BASE_URL/health")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" == "200" ]; then
    echo "✅ Health Check OK"
    echo "   Réponse: $body"
else
    echo "❌ Health Check FAILED (Code: $http_code)"
fi
echo ""

# Test 2: Login (si des utilisateurs existent)
echo "2️⃣  Test Login..."
response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" == "200" ]; then
    echo "✅ Login OK"
    TOKEN=$(echo "$body" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    if [ ! -z "$TOKEN" ]; then
        echo "   Token obtenu: ${TOKEN:0:20}..."
        export TOKEN
    fi
elif [ "$http_code" == "401" ]; then
    echo "⚠️  Login FAILED - Utilisateur non trouvé ou mot de passe incorrect"
    echo "   Créez un utilisateur admin d'abord"
else
    echo "❌ Login FAILED (Code: $http_code)"
    echo "   Réponse: $body"
fi
echo ""

# Test 3: Endpoint protégé (si token disponible)
if [ ! -z "$TOKEN" ]; then
    echo "3️⃣  Test Endpoint Protégé..."
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL/admin/dashboard" \
      -H "Authorization: Bearer $TOKEN")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" == "200" ]; then
        echo "✅ Endpoint protégé OK"
    else
        echo "❌ Endpoint protégé FAILED (Code: $http_code)"
    fi
    echo ""
fi

echo "✅ Tests terminés"
echo ""
echo "💡 Pour plus de tests, consultez TEST_API.md"


