"""
Script de migration des mots de passe SHA-256 vers bcrypt
"""
import sqlite3
from flask_bcrypt import Bcrypt
import hashlib

bcrypt = Bcrypt()

def migrate_passwords(db_path='database/esa.db'):
    """Migre tous les mots de passe SHA-256 vers bcrypt"""
    print("🔄 Migration des mots de passe SHA-256 vers bcrypt...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Récupérer tous les utilisateurs
    cursor.execute("SELECT id, password_hash FROM users")
    users = cursor.fetchall()
    
    migrated = 0
    already_bcrypt = 0
    errors = 0
    
    for user_id, password_hash in users:
        # Vérifier si c'est déjà bcrypt
        if password_hash.startswith('$2'):
            already_bcrypt += 1
            continue
        
        # Si c'est SHA-256 (64 caractères hex), on ne peut pas le convertir
        # Il faut demander à l'utilisateur de réinitialiser son mot de passe
        if len(password_hash) == 64:
            # Marquer pour réinitialisation
            print(f"  ⚠️  Utilisateur {user_id}: Mot de passe SHA-256 détecté")
            print(f"     → L'utilisateur devra réinitialiser son mot de passe")
            
            # Option: Générer un token de réinitialisation
            # Pour l'instant, on laisse tel quel et l'utilisateur devra réinitialiser
            errors += 1
    
    conn.close()
    
    print(f"\n📊 Résumé:")
    print(f"  ✅ Déjà en bcrypt: {already_bcrypt}")
    print(f"  ⚠️  À réinitialiser: {errors}")
    print(f"\n💡 Les utilisateurs avec mots de passe SHA-256 devront utiliser")
    print(f"   la fonction 'Mot de passe oublié' pour réinitialiser.")

if __name__ == "__main__":
    migrate_passwords()


