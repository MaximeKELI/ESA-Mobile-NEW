"""
Validateurs de données
"""
import re
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

def validate_email_format(email):
    """Valide le format d'un email"""
    try:
        # check_deliverability=False pour ne pas vérifier l'existence du domaine
        # Utile en développement avec des domaines de test
        validate_email(email, check_deliverability=False)
        return True, None
    except EmailNotValidError as e:
        return False, str(e)

def validate_phone(phone):
    """Valide un numéro de téléphone"""
    if not phone:
        return True, None
    # Format international ou local
    pattern = r'^(\+228|00228|228)?[0-9]{8}$'
    if re.match(pattern, phone.replace(' ', '').replace('-', '')):
        return True, None
    return False, "Format de téléphone invalide"

def validate_date(date_string, format='%Y-%m-%d'):
    """Valide une date"""
    try:
        datetime.strptime(date_string, format)
        return True, None
    except ValueError:
        return False, f"Format de date invalide. Attendu: {format}"

def validate_note(note):
    """Valide une note (0-20)"""
    try:
        note_float = float(note)
        if 0 <= note_float <= 20:
            return True, None
        return False, "La note doit être entre 0 et 20"
    except (ValueError, TypeError):
        return False, "La note doit être un nombre"

def validate_montant(montant):
    """Valide un montant"""
    try:
        montant_float = float(montant)
        if montant_float >= 0:
            return True, None
        return False, "Le montant doit être positif"
    except (ValueError, TypeError):
        return False, "Le montant doit être un nombre"

def validate_required(data, fields):
    """Valide que les champs requis sont présents"""
    missing = [field for field in fields if field not in data or not data[field]]
    if missing:
        return False, f"Champs manquants: {', '.join(missing)}"
    return True, None

