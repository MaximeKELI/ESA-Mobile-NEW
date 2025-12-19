"""
Script d'initialisation complète de la base de données SQLite
Combine tous les schémas et crée des utilisateurs de test
"""
import sqlite3
import os
from pathlib import Path
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def init_complete_database():
    """Initialise la base de données avec tous les schémas"""
    db_path = Path(__file__).parent / "esa.db"
    
    # Supprimer la base existante pour une réinitialisation propre
    if db_path.exists():
        print(f"⚠️  Suppression de la base existante: {db_path}")
        db_path.unlink()
    
    # Créer la connexion
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    print("📚 Chargement des schémas...")
    
    # 1. Schéma de base
    schema_path = Path(__file__).parent / "schema.sql"
    if schema_path.exists():
        print("   - Chargement schema.sql...")
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = f.read()
        cursor.executescript(schema)
    
    # 2. Schéma étendu
    schema_extended_path = Path(__file__).parent / "schema_extended.sql"
    if schema_extended_path.exists():
        print("   - Chargement schema_extended.sql...")
        with open(schema_extended_path, 'r', encoding='utf-8') as f:
            schema_extended = f.read()
        try:
            cursor.executescript(schema_extended)
        except sqlite3.OperationalError as e:
            print(f"   ⚠️  Erreur dans schema_extended.sql (peut être normal): {e}")
    
    # 3. Schéma Top 10 fonctionnalités
    schema_top10_path = Path(__file__).parent / "schema_top10.sql"
    if schema_top10_path.exists():
        print("   - Chargement schema_top10.sql...")
        with open(schema_top10_path, 'r', encoding='utf-8') as f:
            schema_top10 = f.read()
        try:
            cursor.executescript(schema_top10)
        except sqlite3.OperationalError as e:
            print(f"   ⚠️  Erreur dans schema_top10.sql (peut être normal): {e}")
    
    print("✅ Schémas chargés")
    print("")
    
    # Insérer les données initiales
    print("👥 Création des utilisateurs de test...")
    insert_test_users(cursor)
    
    print("📅 Création des données de base...")
    insert_initial_data(cursor)
    
    conn.commit()
    conn.close()
    
    print("")
    print(f"✅ Base de données initialisée avec succès: {db_path}")
    print("")
    print("🔑 Utilisateurs de test créés:")
    print("   - admin / admin123 (Administrateur)")
    print("   - comptable / comptable123 (Comptabilité)")
    print("   - enseignant1 / enseignant123 (Enseignant)")
    print("   - etudiant1 / etudiant123 (Étudiant)")
    print("   - parent1 / parent123 (Parent)")

def insert_test_users(cursor):
    """Crée des utilisateurs de test pour tous les rôles"""
    from datetime import datetime
    
    # Mot de passe par défaut pour tous: "password123"
    default_password = "password123"
    password_hash = bcrypt.generate_password_hash(default_password).decode('utf-8')
    
    users = [
        # Admin
        ("admin", "admin@esa.tg", password_hash, "admin", "Administrateur", "ESA", "+22890123456", "Lomé, Togo", 1),
        
        # Comptabilité
        ("comptable", "comptable@esa.tg", password_hash, "comptabilite", "Comptable", "Principal", "+22890123457", "Lomé, Togo", 1),
        
        # Enseignants
        ("enseignant1", "enseignant1@esa.tg", password_hash, "enseignant", "Koffi", "Jean", "+22890123458", "Lomé, Togo", 1),
        ("enseignant2", "enseignant2@esa.tg", password_hash, "enseignant", "Ama", "Marie", "+22890123459", "Lomé, Togo", 1),
        
        # Étudiants
        ("etudiant1", "etudiant1@esa.tg", password_hash, "etudiant", "Doe", "John", "+22890123460", "Lomé, Togo", 1),
        ("etudiant2", "etudiant2@esa.tg", password_hash, "etudiant", "Smith", "Jane", "+22890123461", "Lomé, Togo", 1),
        
        # Parents
        ("parent1", "parent1@esa.tg", password_hash, "parent", "Doe", "Parent", "+22890123462", "Lomé, Togo", 1),
    ]
    
    for username, email, pwd_hash, role, nom, prenom, telephone, adresse, is_active in users:
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, email, password_hash, role, nom, prenom, telephone, adresse, is_active, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, email, pwd_hash, role, nom, prenom, telephone, adresse, is_active, datetime.now().isoformat()))
        
        user_id = cursor.lastrowid if cursor.lastrowid else cursor.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()[0]
        
        # Créer les profils spécifiques selon le rôle
        if role == "etudiant":
            cursor.execute("""
                INSERT OR IGNORE INTO etudiants (user_id, numero_etudiant, date_inscription, is_active)
                VALUES (?, ?, ?, ?)
            """, (user_id, f"ETU{user_id:04d}", datetime.now().date().isoformat(), 1))
        
        elif role == "enseignant":
            cursor.execute("""
                INSERT OR IGNORE INTO enseignants (user_id, numero_enseignant, date_embauche, is_active)
                VALUES (?, ?, ?, ?)
            """, (user_id, f"ENS{user_id:04d}", datetime.now().date().isoformat(), 1))
        
        elif role == "parent":
            cursor.execute("""
                INSERT OR IGNORE INTO parents (user_id, numero_parent, is_active)
                VALUES (?, ?, ?)
            """, (user_id, f"PAR{user_id:04d}", 1))
    
    print(f"   ✅ {len(users)} utilisateurs créés")

def insert_initial_data(cursor):
    """Insère les données initiales nécessaires"""
    from datetime import datetime
    
    # Année académique
    cursor.execute("""
        INSERT OR IGNORE INTO annees_academiques (code, libelle, date_debut, date_fin, is_active)
        VALUES (?, ?, ?, ?, ?)
    """, ("2024-2025", "Année académique 2024-2025", "2024-09-01", "2025-07-31", 1))
    
    # Paramètres globaux
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
    
    # Créer quelques widgets système pour les tableaux de bord
    widgets = [
        ("stats_etudiants", "Statistiques Étudiants", "statistique", '{"type": "nombre"}', 1),
        ("stats_paiements", "Statistiques Paiements", "statistique", '{"type": "montant"}', 1),
        ("graphique_notes", "Graphique des Notes", "graphique", '{"type": "bar"}', 1),
        ("calendrier_events", "Calendrier", "calendrier", '{"type": "mois"}', 1),
    ]
    
    for code, nom, type_widget, config, is_systeme in widgets:
        cursor.execute("""
            INSERT OR IGNORE INTO widgets (code, nom, type_widget, configuration_defaut, is_systeme)
            VALUES (?, ?, ?, ?, ?)
        """, (code, nom, type_widget, config, is_systeme))
    
    # Créer quelques compétences pour le portfolio
    competences = [
        ("COMP001", "Mathématiques", "Compétences en mathématiques", "academique"),
        ("COMP002", "Informatique", "Compétences en programmation", "technique"),
        ("COMP003", "Communication", "Compétences en communication", "soft_skills"),
        ("COMP004", "Gestion", "Compétences en gestion", "professionnel"),
    ]
    
    for code, libelle, description, categorie in competences:
        cursor.execute("""
            INSERT OR IGNORE INTO competences (code, libelle, description, categorie, is_active)
            VALUES (?, ?, ?, ?, ?)
        """, (code, libelle, description, categorie, 1))
    
    print("   ✅ Données initiales insérées")

if __name__ == "__main__":
    init_complete_database()

