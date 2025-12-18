"""
Service de notifications amélioré
"""
from database.db import get_db
from datetime import datetime
import json

def send_notification(user_id, type_notification, titre, message, lien=None, data=None):
    """Envoie une notification à un utilisateur"""
    db = get_db()
    
    db.execute("""
        INSERT INTO notifications (user_id, type_notification, titre, message, lien)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, type_notification, titre, message, lien))
    db.commit()
    
    # En production, envoyer aussi une notification push via FCM
    # send_push_notification(user_id, titre, message, data)

def send_bulk_notification(user_ids, type_notification, titre, message, lien=None):
    """Envoie une notification à plusieurs utilisateurs"""
    db = get_db()
    
    for user_id in user_ids:
        db.execute("""
            INSERT INTO notifications (user_id, type_notification, titre, message, lien)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, type_notification, titre, message, lien))
    
    db.commit()

def send_email_notification(user_email, subject, body, html_body=None):
    """Envoie une notification par email"""
    from flask_mail import Message
    from app import mail
    
    try:
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=body,
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False

def send_sms_notification(phone_number, message):
    """Envoie une notification par SMS"""
    try:
        import os
        from twilio.rest import Client
        
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            return False
        
        client = Client(account_sid, auth_token)
        
        client.messages.create(
            body=message,
            from_=from_number,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Erreur envoi SMS: {e}")
        return False

def send_push_notification(user_id, title, body, data=None):
    """Envoie une notification push via FCM"""
    # À implémenter avec firebase-admin
    pass

def notify_payment_received(etudiant_id, montant, type_frais):
    """Notifie la réception d'un paiement"""
    db = get_db()
    
    # Notifier l'étudiant
    etudiant = db.execute("SELECT user_id FROM etudiants WHERE id = ?", (etudiant_id,)).fetchone()
    if etudiant:
        send_notification(
            etudiant['user_id'],
            'paiement_reçu',
            'Paiement reçu',
            f'Votre paiement de {montant} FCFA pour {type_frais} a été reçu et validé.',
            f'/etudiant/paiements'
        )
        
        # Notifier les parents
        parents = db.execute("""
            SELECT p.user_id FROM parents p
            JOIN parent_etudiants pe ON p.id = pe.parent_id
            WHERE pe.etudiant_id = ?
        """, (etudiant_id,)).fetchall()
        
        for parent in parents:
            send_notification(
                parent['user_id'],
                'paiement_enfant',
                'Paiement reçu',
                f'Le paiement de {montant} FCFA a été effectué pour votre enfant.',
                f'/parent/enfants/{etudiant_id}/finances'
            )

def notify_grade_added(etudiant_id, matiere, note):
    """Notifie l'ajout d'une note"""
    db = get_db()
    
    etudiant = db.execute("SELECT user_id FROM etudiants WHERE id = ?", (etudiant_id,)).fetchone()
    if etudiant:
        send_notification(
            etudiant['user_id'],
            'note_ajoutee',
            'Nouvelle note',
            f'Une nouvelle note a été ajoutée en {matiere}: {note}/20',
            f'/etudiant/notes'
        )
        
        # Notifier les parents
        parents = db.execute("""
            SELECT p.user_id FROM parents p
            JOIN parent_etudiants pe ON p.id = pe.parent_id
            WHERE pe.etudiant_id = ?
        """, (etudiant_id,)).fetchall()
        
        for parent in parents:
            send_notification(
                parent['user_id'],
                'note_enfant',
                'Nouvelle note',
                f'Une nouvelle note a été ajoutée pour votre enfant en {matiere}: {note}/20',
                f'/parent/enfants/{etudiant_id}/notes'
            )

def notify_absence_recorded(etudiant_id, date_absence):
    """Notifie l'enregistrement d'une absence"""
    db = get_db()
    
    etudiant = db.execute("SELECT user_id FROM etudiants WHERE id = ?", (etudiant_id,)).fetchone()
    if etudiant:
        send_notification(
            etudiant['user_id'],
            'absence',
            'Absence enregistrée',
            f'Une absence a été enregistrée pour le {date_absence}',
            f'/etudiant/absences'
        )
        
        # Notifier les parents
        parents = db.execute("""
            SELECT p.user_id FROM parents p
            JOIN parent_etudiants pe ON p.id = pe.parent_id
            WHERE pe.etudiant_id = ?
        """, (etudiant_id,)).fetchall()
        
        for parent in parents:
            send_notification(
                parent['user_id'],
                'absence_enfant',
                'Absence de votre enfant',
                f'Une absence a été enregistrée pour votre enfant le {date_absence}',
                f'/parent/enfants/{etudiant_id}/absences'
            )

def notify_unpaid_fees(etudiant_id, montant_du):
    """Notifie les frais impayés"""
    db = get_db()
    
    etudiant = db.execute("SELECT user_id FROM etudiants WHERE id = ?", (etudiant_id,)).fetchone()
    if etudiant:
        send_notification(
            etudiant['user_id'],
            'frais_impayes',
            'Frais impayés',
            f'Vous avez un solde impayé de {montant_du} FCFA. Veuillez régulariser votre situation.',
            f'/etudiant/finances'
        )
        
        # Envoyer aussi un email et SMS si configuré
        user = db.execute("SELECT email, telephone FROM users WHERE id = ?", 
                         (etudiant['user_id'],)).fetchone()
        
        if user and user['email']:
            send_email_notification(
                user['email'],
                'Rappel: Frais impayés',
                f'Vous avez un solde impayé de {montant_du} FCFA.'
            )
        
        if user and user['telephone']:
            send_sms_notification(
                user['telephone'],
                f'ESA: Solde impayé de {montant_du} FCFA. Veuillez régulariser.'
            )

