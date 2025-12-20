"""
Script d'initialisation de la base de données SQLite
"""
import sqlite3
import os
from pathlib import Path

def init_database():
    """Initialise la base de données avec le schéma complet"""
    db_path = Path(__file__).parent / "esa.db"
    
    # Supprimer la base existante si nécessaire (pour développement)
    if db_path.exists() and os.getenv("RESET_DB", "false").lower() == "true":
        db_path.unlink()
    
    # Lire le schéma SQL
    schema_path = Path(__file__).parent / "schema.sql"
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = f.read()
    
    # Créer la connexion et exécuter le schéma
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Exécuter le schéma
    cursor.executescript(schema)
    
    # Insérer des données initiales
    insert_initial_data(cursor)
    
    conn.commit()
    conn.close()
    
    print(f"Base de données initialisée avec succès: {db_path}")

def insert_initial_data(cursor):
    """Insère les données initiales nécessaires"""
    import hashlib
    from datetime import datetime
    
    # Créer un utilisateur admin par défaut (mot de passe: admin123)
    password_hash = hashlib.sha256("admin123".encode()).hexdigest()  # En production, utiliser bcrypt
    
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, email, password_hash, role, nom, prenom, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("admin", "admin@esa.tg", password_hash, "admin", "Administrateur", "ESA", 1))
    
    # Insérer une année académique par défaut
    cursor.execute("""
        INSERT OR IGNORE INTO annees_academiques (code, libelle, date_debut, date_fin, is_active)
        VALUES (?, ?, ?, ?, ?)
    """, ("2024-2025", "Année académique 2024-2025", "2024-09-01", "2025-07-31", 1))
    
    # Insérer des paramètres globaux
    parametres = [
        ("nom_ecole", "École Supérieure des Affaires", "string", "Nom de l'établissement"),
        ("adresse_ecole", "Lomé, Togo", "string", "Adresse de l'établissement"),
        ("telephone_ecole", "+228 XX XX XX XX", "string", "Téléphone de l'établissement"),
        ("email_ecole", "contact@esa.tg", "string", "Email de l'établissement"),
        ("seuil_reussite", "10.0", "float", "Note minimale pour réussir"),
        ("penalite_retard_paiement", "5.0", "float", "Pourcentage de pénalité pour retard de paiement"),
        ("delai_verrouillage_impaye", "30", "integer", "Délai en jours avant verrouillage pour impayé"),
    ]
    
    for cle, valeur, type_valeur, description in parametres:
        cursor.execute("""
            INSERT OR IGNORE INTO parametres (cle, valeur, type_valeur, description)
            VALUES (?, ?, ?, ?)
        """, (cle, valeur, type_valeur, description))
    
    print("Données initiales insérées avec succès")

if __name__ == "__main__":
    init_database()


