"""
CRM Template for VAT Management
===============================

This application helps companies manage their VAT with:
- PDF reading capabilities to extract invoice data
- Excel generation containing data (Nomination, Montant HT, TVA, Montant TTC)
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from starlette.responses import HTMLResponse
import uvicorn
import pandas as pd
from pdfminer.high_level import extract_text
import re


@dataclass
class VATRecord:
    """Represents a VAT record with essential fields"""
    id: str
    nomination: str
    montant_ht: float
    tva_rate: float
    montant_tva: float
    montant_ttc: float
    date: str
    supplier: str = ""
    invoice_number: str = ""


class VATRecordRequest(BaseModel):
    """Request model for VAT record creation"""
    nomination: str
    montant_ht: float
    tva_rate: float = 20.0  # Default VAT rate is 20%
    date: Optional[str] = None
    supplier: str = ""
    invoice_number: str = ""


class VATCRMApp:
    """Main VAT CRM Application Class"""
    
    def __init__(self):
        self.records: List[VATRecord] = []
        self.upload_dir = "/workspace/vat_crm_app/uploads"
        self.excel_dir = "/workspace/vat_crm_app/excel_exports"
        
        # Create necessary directories
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.excel_dir, exist_ok=True)
    
    def add_record(self, record_data: VATRecordRequest) -> VATRecord:
        """Add a new VAT record"""
        # Calculate TVA and TTC
        montant_tva = (record_data.montant_ht * record_data.tva_rate) / 100
        montant_ttc = record_data.montant_ht + montant_tva
        
        # Set date to current date if not provided
        date = record_data.date or datetime.now().strftime("%Y-%m-%d")
        
        record = VATRecord(
            id=str(uuid.uuid4()),
            nomination=record_data.nomination,
            montant_ht=record_data.montant_ht,
            tva_rate=record_data.tva_rate,
            montant_tva=montant_tva,
            montant_ttc=montant_ttc,
            date=date,
            supplier=record_data.supplier,
            invoice_number=record_data.invoice_number
        )
        
        self.records.append(record)
        return record
    
    def get_all_records(self) -> List[VATRecord]:
        """Get all VAT records"""
        return self.records
    
    def export_to_excel(self) -> str:
        """Export all records to Excel file"""
        if not self.records:
            raise ValueError("No records to export")
        
        # Create DataFrame from records
        data = []
        for record in self.records:
            data.append({
                'ID': record.id,
                'Nomination': record.nomination,
                'Montant HT': record.montant_ht,
                'Taux TVA (%)': record.tva_rate,
                'Montant TVA': record.montant_tva,
                'Montant TTC': record.montant_ttc,
                'Date': record.date,
                'Fournisseur': record.supplier,
                'Numéro Facture': record.invoice_number
            })
        
        df = pd.DataFrame(data)
        
        # Generate filename with timestamp
        filename = f"vat_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        filepath = os.path.join(self.excel_dir, filename)
        
        # Export to Excel
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='VAT_Records', index=False)
            
            # Format the Excel sheet
            worksheet = writer.sheets['VAT_Records']
            
            # Auto-adjust column widths
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        return filepath
    
    def process_pdf(self, file_path: str) -> List[Dict]:
        """Extract invoice data from PDF file"""
        try:
            text = extract_text(file_path)
            
            # Simple regex patterns to extract invoice information
            # These are basic patterns - in a real application, you'd need more sophisticated extraction
            patterns = {
                'date': r'(?:date|date de facture|facturé le)[:\s]*([0-9]{2}[\/\-\.][0-9]{2}[\/\-\.][0-9]{4}|[0-9]{4}[\/\-\.][0-9]{2}[\/\-\.][0-9]{2})',
                'invoice_number': r'(?:facture|invoice|n°|numéro)[:\s]*([A-Z0-9\-\/]+)',
                'supplier': r'(?:fournisseur|supplier|facturé par)[:\s]*([A-Z0-9\s\-_\.]+?)(?:\n|$)',
                'amount_ht': r'(?:hors taxe|ht|excl\. tax|subtotal|sous-total)[\s\:€]*([0-9\.,]+)',
                'amount_ttc': r'(?:total|toutes taxes comprises|ttc|grand total)[\s\:€]*([0-9\.,]+)',
                'tva_rate': r'([0-9]+)[\s\%]*(?:tva|taxe|vat|tax)',
            }
            
            extracted_data = {}
            
            for key, pattern in patterns.items():
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    extracted_data[key] = match.group(1).strip()
            
            # Additional pattern for amount without specific label
            if 'amount_ht' not in extracted_data:
                amount_match = re.search(r'(?:montant|amount)[\s\:€]*([0-9\.,]+)', text, re.IGNORECASE)
                if amount_match:
                    extracted_data['amount_ht'] = amount_match.group(1).strip()
            
            return extracted_data
            
        except Exception as e:
            print(f"Error processing PDF: {str(e)}")
            return {}


# Initialize the application
app = VATCRMApp()
fastapi_app = FastAPI(title="VAT CRM System", description="CRM for VAT Management with PDF reading and Excel export")

@fastapi_app.get("/")
async def read_root():
    """Serve the main HTML interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CRM de Gestion de TVA</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { 
                color: #333; 
                text-align: center;
                margin-bottom: 30px;
            }
            .form-section {
                margin-bottom: 30px;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 8px;
                background-color: #f9f9f9;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            input, select, textarea {
                width: 100%;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                box-sizing: border-box;
            }
            .button-group {
                display: flex;
                gap: 10px;
                margin-top: 15px;
            }
            button { 
                padding: 12px 24px; 
                background-color: #007BFF; 
                color: white; 
                border: none; 
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #0056b3;
            }
            button:disabled {
                background-color: #cccccc;
                cursor: not-allowed;
            }
            .upload-section {
                margin-top: 20px;
                padding: 15px;
                border: 1px dashed #ccc;
                border-radius: 4px;
                text-align: center;
            }
            .records-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            .records-table th, .records-table td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            .records-table th {
                background-color: #f2f2f2;
                font-weight: bold;
            }
            .records-table tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .export-section {
                margin-top: 30px;
                text-align: center;
            }
            .status-message {
                padding: 10px;
                margin: 10px 0;
                border-radius: 4px;
                display: none;
            }
            .success {
                background-color: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .error {
                background-color: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .hidden {
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>CRM de Gestion de TVA</h1>
            
            <div class="form-section">
                <h2>Ajouter un nouveau document</h2>
                
                <div class="form-group">
                    <label for="nomination">Nomination (Libellé de la dépense):</label>
                    <input type="text" id="nomination" placeholder="Ex: Fournitures de bureau">
                </div>
                
                <div class="form-group">
                    <label for="montant_ht">Montant HT (€):</label>
                    <input type="number" id="montant_ht" step="0.01" placeholder="Ex: 100.00">
                </div>
                
                <div class="form-group">
                    <label for="tva_rate">Taux de TVA (%):</label>
                    <select id="tva_rate">
                        <option value="20.0">20% - Taux normal</option>
                        <option value="10.0">10% - Taux intermédiaire</option>
                        <option value="5.5">5.5% - Taux réduit</option>
                        <option value="2.1">2.1% - Taux super réduit</option>
                        <option value="0.0">0% - Exonéré</option>
                        <option value="custom">Autre taux</option>
                    </select>
                    <input type="number" id="tva_rate_custom" step="0.01" placeholder="Taux personnalisé" style="margin-top: 5px;" class="hidden">
                </div>
                
                <div class="form-group">
                    <label for="date">Date:</label>
                    <input type="date" id="date" value="">
                </div>
                
                <div class="form-group">
                    <label for="supplier">Fournisseur:</label>
                    <input type="text" id="supplier" placeholder="Nom du fournisseur">
                </div>
                
                <div class="form-group">
                    <label for="invoice_number">Numéro de facture:</label>
                    <input type="text" id="invoice_number" placeholder="Numéro de facture">
                </div>
                
                <div class="button-group">
                    <button id="addRecordBtn" onclick="addRecord()">Ajouter le document</button>
                    <button id="clearFormBtn" onclick="clearForm()">Effacer le formulaire</button>
                </div>
                
                <div class="upload-section">
                    <h3>Lecture de PDF de facture</h3>
                    <p>Téléchargez un PDF de facture pour extraire automatiquement les informations</p>
                    <input type="file" id="pdfFile" accept=".pdf">
                    <button onclick="uploadPDF()" style="margin-top: 10px;">Lire le PDF</button>
                </div>
            </div>
            
            <div class="export-section">
                <button onclick="exportToExcel()">Exporter vers Excel</button>
            </div>
            
            <div id="statusMessage" class="status-message"></div>
            
            <h2>Documents TVA enregistrés</h2>
            <div id="recordsContainer">
                <table class="records-table" id="recordsTable">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nomination</th>
                            <th>Montant HT</th>
                            <th>Taux TVA</th>
                            <th>Montant TVA</th>
                            <th>Montant TTC</th>
                            <th>Date</th>
                            <th>Fournisseur</th>
                            <th>Facture</th>
                        </tr>
                    </thead>
                    <tbody id="recordsTableBody">
                        <!-- Records will be populated here -->
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            // Set today's date as default
            document.getElementById('date').valueAsDate = new Date();
            
            // Handle VAT rate selection
            document.getElementById('tva_rate').addEventListener('change', function() {
                const customField = document.getElementById('tva_rate_custom');
                if (this.value === 'custom') {
                    customField.classList.remove('hidden');
                    customField.value = '';
                } else {
                    customField.classList.add('hidden');
                }
            });
            
            // Load existing records on page load
            window.onload = function() {
                loadRecords();
            };
            
            async function loadRecords() {
                try {
                    const response = await fetch('/api/records');
                    const records = await response.json();
                    
                    const tbody = document.getElementById('recordsTableBody');
                    tbody.innerHTML = '';
                    
                    records.forEach(record => {
                        const row = tbody.insertRow();
                        row.insertCell(0).textContent = record.id.substring(0, 8);
                        row.insertCell(1).textContent = record.nomination;
                        row.insertCell(2).textContent = parseFloat(record.montant_ht).toFixed(2) + ' €';
                        row.insertCell(3).textContent = parseFloat(record.tva_rate).toFixed(1) + ' %';
                        row.insertCell(4).textContent = parseFloat(record.montant_tva).toFixed(2) + ' €';
                        row.insertCell(5).textContent = parseFloat(record.montant_ttc).toFixed(2) + ' €';
                        row.insertCell(6).textContent = record.date;
                        row.insertCell(7).textContent = record.supplier || 'N/A';
                        row.insertCell(8).textContent = record.invoice_number || 'N/A';
                    });
                } catch (error) {
                    showStatus('Erreur lors du chargement des enregistrements: ' + error.message, 'error');
                }
            }
            
            async function addRecord() {
                const nomination = document.getElementById('nomination').value;
                const montant_ht = parseFloat(document.getElementById('montant_ht').value);
                const date = document.getElementById('date').value;
                const supplier = document.getElementById('supplier').value;
                const invoice_number = document.getElementById('invoice_number').value;
                
                // Get VAT rate
                const tva_rate_select = document.getElementById('tva_rate');
                let tva_rate;
                if (tva_rate_select.value === 'custom') {
                    tva_rate = parseFloat(document.getElementById('tva_rate_custom').value);
                } else {
                    tva_rate = parseFloat(tva_rate_select.value);
                }
                
                // Validation
                if (!nomination || isNaN(montant_ht) || montant_ht <= 0) {
                    showStatus('Veuillez remplir tous les champs obligatoires correctement', 'error');
                    return;
                }
                
                if (isNaN(tva_rate) || tva_rate < 0) {
                    showStatus('Taux de TVA invalide', 'error');
                    return;
                }
                
                if (!date) {
                    showStatus('Veuillez sélectionner une date', 'error');
                    return;
                }
                
                try {
                    const response = await fetch('/api/records', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            nomination: nomination,
                            montant_ht: montant_ht,
                            tva_rate: tva_rate,
                            date: date,
                            supplier: supplier,
                            invoice_number: invoice_number
                        })
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        showStatus('Document TVA ajouté avec succès!', 'success');
                        loadRecords(); // Reload records
                        clearForm(); // Clear the form
                    } else {
                        const error = await response.json();
                        showStatus('Erreur: ' + error.detail || 'Impossible d\'ajouter le document', 'error');
                    }
                } catch (error) {
                    showStatus('Erreur de connexion: ' + error.message, 'error');
                }
            }
            
            async function exportToExcel() {
                try {
                    showStatus('Génération du fichier Excel en cours...', 'success');
                    
                    const response = await fetch('/api/export-excel', {
                        method: 'GET'
                    });
                    
                    if (response.ok) {
                        const blob = await response.blob();
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'vat_records.xlsx';
                        document.body.appendChild(a);
                        a.click();
                        a.remove();
                        window.URL.revokeObjectURL(url);
                        
                        showStatus('Fichier Excel téléchargé avec succès!', 'success');
                    } else {
                        const error = await response.json();
                        showStatus('Erreur lors de l\'export: ' + error.detail || 'Impossible d\'exporter', 'error');
                    }
                } catch (error) {
                    showStatus('Erreur de connexion: ' + error.message, 'error');
                }
            }
            
            async function uploadPDF() {
                const fileInput = document.getElementById('pdfFile');
                const file = fileInput.files[0];
                
                if (!file) {
                    showStatus('Veuillez sélectionner un fichier PDF', 'error');
                    return;
                }
                
                if (file.type !== 'application/pdf') {
                    showStatus('Veuillez sélectionner un fichier PDF valide', 'error');
                    return;
                }
                
                try {
                    showStatus('Lecture du PDF en cours...', 'success');
                    
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch('/api/process-pdf', {
                        method: 'POST',
                        body: formData
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        
                        // Fill form fields with extracted data
                        if (data.nomination) {
                            document.getElementById('nomination').value = data.nomination;
                        }
                        if (data.amount_ht) {
                            document.getElementById('montant_ht').value = parseFloat(data.amount_ht).toString();
                        }
                        if (data.tva_rate) {
                            document.getElementById('tva_rate').value = 'custom';
                            document.getElementById('tva_rate_custom').classList.remove('hidden');
                            document.getElementById('tva_rate_custom').value = data.tva_rate;
                        }
                        if (data.date) {
                            // Try to parse date from various formats
                            let date = new Date(data.date);
                            if (!isNaN(date.getTime())) {
                                document.getElementById('date').valueAsDate = date;
                            }
                        }
                        if (data.supplier) {
                            document.getElementById('supplier').value = data.supplier;
                        }
                        if (data.invoice_number) {
                            document.getElementById('invoice_number').value = data.invoice_number;
                        }
                        
                        showStatus('PDF lu avec succès! Les champs ont été remplis automatiquement.', 'success');
                    } else {
                        const error = await response.json();
                        showStatus('Erreur lors de la lecture du PDF: ' + error.detail || 'Impossible de traiter le PDF', 'error');
                    }
                } catch (error) {
                    showStatus('Erreur de connexion: ' + error.message, 'error');
                }
            }
            
            function clearForm() {
                document.getElementById('nomination').value = '';
                document.getElementById('montant_ht').value = '';
                document.getElementById('tva_rate').value = '20.0';
                document.getElementById('tva_rate_custom').value = '';
                document.getElementById('tva_rate_custom').classList.add('hidden');
                document.getElementById('date').valueAsDate = new Date();
                document.getElementById('supplier').value = '';
                document.getElementById('invoice_number').value = '';
                document.getElementById('pdfFile').value = '';
            }
            
            function showStatus(message, type) {
                const statusDiv = document.getElementById('statusMessage');
                statusDiv.textContent = message;
                statusDiv.className = 'status-message ' + type;
                statusDiv.style.display = 'block';
                
                // Auto-hide after 5 seconds
                setTimeout(() => {
                    statusDiv.style.display = 'none';
                }, 5000);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@fastapi_app.post("/api/records")
async def add_vat_record(record_data: VATRecordRequest):
    """Add a new VAT record"""
    try:
        record = app.add_record(record_data)
        return {"status": "success", "record": asdict(record)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@fastapi_app.get("/api/records")
async def get_vat_records():
    """Get all VAT records"""
    records = app.get_all_records()
    return [asdict(record) for record in records]


@fastapi_app.get("/api/export-excel")
async def export_excel():
    """Export all records to Excel file"""
    try:
        filepath = app.export_to_excel()
        return FileResponse(
            path=filepath,
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            filename=os.path.basename(filepath)
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@fastapi_app.post("/api/process-pdf")
async def process_pdf(file: UploadFile = File(...)):
    """Process PDF file and extract VAT information"""
    try:
        # Save uploaded file temporarily
        file_path = os.path.join(app.upload_dir, f"temp_{uuid.uuid4()}_{file.filename}")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the PDF
        extracted_data = app.process_pdf(file_path)
        
        # Clean up the temporary file
        os.remove(file_path)
        
        return extracted_data
    except Exception as e:
        # Clean up the temporary file if it exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


if __name__ == "__main__":
    print("Démarrage de l'application CRM de gestion de TVA...")
    print("L'API sera disponible à l'adresse: http://localhost:8080")
    print("Interface web: http://localhost:8080")
    
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8080)