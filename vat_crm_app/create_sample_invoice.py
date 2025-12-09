"""
Script to create a sample invoice PDF for testing the VAT CRM application
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def create_sample_invoice():
    # Create a PDF with invoice information
    filename = "/workspace/vat_crm_app/sample_invoice.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "FACTURE")
    
    # Invoice details
    c.setFont("Helvetica", 12)
    y_position = height - 100
    
    c.drawString(50, y_position, f"Numéro de facture: FACT-{datetime.now().strftime('%Y%m%d')}")
    y_position -= 20
    c.drawString(50, y_position, f"Date: {datetime.now().strftime('%d/%m/%Y')}")
    y_position -= 20
    c.drawString(50, y_position, "Fournisseur: SARL Services Informatiques")
    y_position -= 40
    
    # Bill to
    c.drawString(50, y_position, "Facturé à:")
    y_position -= 20
    c.drawString(50, y_position, "SASU Gestion Commerciale")
    y_position -= 20
    c.drawString(50, y_position, "123 Avenue des Champs Elysées")
    y_position -= 20
    c.drawString(50, y_position, "75008 PARIS")
    y_position -= 40
    
    # Items table header
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_position, "Description")
    c.drawString(300, y_position, "Montant HT")
    c.drawString(400, y_position, "TVA")
    c.drawString(480, y_position, "Total")
    y_position -= 20
    c.line(50, y_position, 550, y_position)
    
    # Item details
    c.setFont("Helvetica", 12)
    c.drawString(50, y_position, "Maintenance informatique - Janvier 2025")
    c.drawString(300, y_position, "500,00 €")
    c.drawString(400, y_position, "20%")
    c.drawString(480, y_position, "600,00 €")
    y_position -= 20
    
    # Subtotal
    c.drawString(400, y_position, "Sous-total:")
    c.drawString(480, y_position, "500,00 €")
    y_position -= 20
    
    # TVA
    c.drawString(400, y_position, "TVA (20%):")
    c.drawString(480, y_position, "100,00 €")
    y_position -= 20
    
    # Total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(400, y_position, "TOTAL TTC:")
    c.drawString(480, y_position, "600,00 €")
    
    # Footer
    y_position -= 60
    c.setFont("Helvetica", 10)
    c.drawString(50, y_position, "Conditions de paiement: 30 jours nets")
    y_position -= 15
    c.drawString(50, y_position, "IBAN: FR76 1234 5678 9012 3456 7890 123")
    y_position -= 15
    c.drawString(50, y_position, "SIRET: 123 456 789 00012")
    
    c.save()
    print(f"Sample invoice created: {filename}")

if __name__ == "__main__":
    create_sample_invoice()