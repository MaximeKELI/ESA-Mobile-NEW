"""
Générateur de QR codes pour les cartes étudiantes
"""
import qrcode
from PIL import Image
import os

def generate_qr_code(data, output_path):
    """Génère un QR code pour une carte étudiante"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_path)
    return output_path

def generate_student_qr(etudiant_id, numero_etudiant, output_dir):
    """Génère un QR code pour un étudiant"""
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"qr_{numero_etudiant}.png")
    
    # Données à encoder dans le QR code
    data = f"ESA|{etudiant_id}|{numero_etudiant}"
    
    generate_qr_code(data, output_path)
    return output_path


