"""
Générateur de documents PDF
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import os

def generate_receipt(paiement_data, output_path):
    """Génère un reçu de paiement en PDF"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Style personnalisé
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    # En-tête
    story.append(Paragraph("ÉCOLE SUPÉRIEURE DES AFFAIRES", title_style))
    story.append(Paragraph("Lomé - Togo", styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("REÇU DE PAIEMENT", styles['Heading2']))
    story.append(Spacer(1, 0.5*cm))
    
    # Informations du paiement
    data = [
        ['Référence:', paiement_data.get('reference', 'N/A')],
        ['Date:', paiement_data.get('date_paiement', datetime.now().strftime('%d/%m/%Y'))],
        ['Étudiant:', f"{paiement_data.get('etudiant_nom', '')} {paiement_data.get('etudiant_prenom', '')}"],
        ['Type de frais:', paiement_data.get('type_frais', 'N/A')],
        ['Montant:', f"{paiement_data.get('montant', 0):,.0f} FCFA"],
        ['Mode de paiement:', paiement_data.get('mode_paiement', 'N/A')],
    ]
    
    table = Table(data, colWidths=[5*cm, 10*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(f"Date d'émission: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                          ParagraphStyle('RightAlign', parent=styles['Normal'], alignment=TA_RIGHT)))
    
    doc.build(story)
    return output_path

def generate_bulletin(etudiant_data, notes_data, output_path):
    """Génère un bulletin scolaire en PDF"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # En-tête
    story.append(Paragraph("ÉCOLE SUPÉRIEURE DES AFFAIRES", 
                          ParagraphStyle('Title', parent=styles['Heading1'], alignment=TA_CENTER)))
    story.append(Paragraph("BULLETIN SCOLAIRE", 
                          ParagraphStyle('Subtitle', parent=styles['Heading2'], alignment=TA_CENTER)))
    story.append(Spacer(1, 0.5*cm))
    
    # Informations étudiant
    info_data = [
        ['Nom:', etudiant_data.get('nom', '')],
        ['Prénom:', etudiant_data.get('prenom', '')],
        ['Classe:', etudiant_data.get('classe', '')],
        ['Période:', etudiant_data.get('periode', '')],
    ]
    
    info_table = Table(info_data, colWidths=[4*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))
    
    # Tableau des notes
    table_data = [['Matière', 'Note', 'Coeff', 'Moyenne']]
    for note in notes_data:
        table_data.append([
            note.get('matiere', ''),
            str(note.get('note', 0)),
            str(note.get('coefficient', 1)),
            str(note.get('moyenne', 0))
        ])
    
    notes_table = Table(table_data)
    notes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(notes_table)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(f"Moyenne générale: {etudiant_data.get('moyenne_generale', 0):.2f}/20", 
                          ParagraphStyle('Bold', parent=styles['Normal'])))
    
    doc.build(story)
    return output_path

def generate_cv_pdf(etudiant_data, portfolio_data, output_path):
    """Génère un CV PDF à partir du portfolio"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # En-tête
    title_style = ParagraphStyle(
        'CVTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1a237e'),
        spaceAfter=10,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph(f"{etudiant_data.get('prenom', '')} {etudiant_data.get('nom', '')}", title_style))
    story.append(Paragraph(etudiant_data.get('email', ''), styles['Normal']))
    if etudiant_data.get('telephone'):
        story.append(Paragraph(etudiant_data.get('telephone'), styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Compétences
    if portfolio_data.get('competences'):
        story.append(Paragraph("COMPÉTENCES", styles['Heading2']))
        for comp in portfolio_data['competences']:
            story.append(Paragraph(f"• {comp.get('competence_libelle', '')} - Niveau {comp.get('niveau', 0)}/5", 
                                 styles['Normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Projets
    if portfolio_data.get('projets'):
        story.append(Paragraph("PROJETS", styles['Heading2']))
        for projet in portfolio_data['projets']:
            story.append(Paragraph(f"• {projet.get('titre', '')}", styles['Normal']))
            if projet.get('description'):
                story.append(Paragraph(projet.get('description'), styles['Normal']))
        story.append(Spacer(1, 0.3*cm))
    
    # Certifications
    if portfolio_data.get('certifications'):
        story.append(Paragraph("CERTIFICATIONS", styles['Heading2']))
        for cert in portfolio_data['certifications']:
            story.append(Paragraph(f"• {cert.get('nom_certification', '')} - {cert.get('organisme', '')}", 
                                 styles['Normal']))
        story.append(Spacer(1, 0.3*cm))
    
    doc.build(story)
    return output_path

