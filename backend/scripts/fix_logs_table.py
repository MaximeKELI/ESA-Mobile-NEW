"""
Script pour corriger la table logs_actions
Permet user_id NULL ou utilise 0 pour les événements anonymes
"""
import sqlite3
from pathlib import Path

def fix_logs_table():
    """Corrige la table logs_actions pour permettre user_id NULL"""
    db_path = Path(__file__).parent.parent / "database" / "esa.db"
    
    if not db_path.exists():
        print("Base de données non trouvée")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Créer une nouvelle table temporaire
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs_actions_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER DEFAULT 0,
                action VARCHAR(100) NOT NULL,
                table_affectee VARCHAR(50),
                enregistrement_id INTEGER,
                anciennes_valeurs TEXT,
                nouvelles_valeurs TEXT,
                ip_address VARCHAR(45),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Copier les données existantes
        cursor.execute("""
            INSERT INTO logs_actions_new 
            SELECT id, COALESCE(user_id, 0), action, table_affectee, enregistrement_id,
                   anciennes_valeurs, nouvelles_valeurs, ip_address, created_at
            FROM logs_actions
        """)
        
        # Supprimer l'ancienne table
        cursor.execute("DROP TABLE logs_actions")
        
        # Renommer la nouvelle table
        cursor.execute("ALTER TABLE logs_actions_new RENAME TO logs_actions")
        
        conn.commit()
        print("✅ Table logs_actions corrigée avec succès")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_logs_table()

