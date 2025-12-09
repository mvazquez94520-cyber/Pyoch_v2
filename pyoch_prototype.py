"""
Prototype de PYOCH - Plateforme de Génération d'Applications Métiers
===============================================================

Ce prototype simule le comportement de PYOCH en Python pour démontrer
le concept sans dépendance à Rust dans l'environnement actuel.
"""

import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.responses import FileResponse
import uvicorn
import os

# Modèles de données
@dataclass
class Rule:
    id: str
    name: str
    description: str
    condition: str
    action: str
    priority: int
    created_at: str
    updated_at: str

@dataclass
class Feedback:
    id: str
    rule_id: str
    is_relevant: bool
    user_comment: Optional[str]
    timestamp: str

@dataclass
class BusinessApplication:
    id: str
    name: str
    application_type: str
    rules: List[Rule]
    feedbacks: List[Feedback]
    created_at: str
    updated_at: str

class ApplicationType(str, Enum):
    CRM = "crm"
    BILLING = "billing"
    PROJECT = "project"
    INVENTORY = "inventory"
    HR = "hr"

# Modèle Pydantic pour FastAPI
class PromptRequest(BaseModel):
    prompt: str

class EvaluationResponse(BaseModel):
    application: Optional[Dict] = None
    generated_code: Optional[str] = None
    rules_generated: List[Dict] = []
    error: Optional[str] = None

class FeedbackRequest(BaseModel):
    rule_id: str
    is_relevant: bool
    user_comment: Optional[str] = None

# Moteur d'IA simulé
class AIEngine:
    def __init__(self):
        pass
    
    async def call_qwen_local(self, prompt: str) -> str:
        # Simulation de réponse d'IA
        return f"Code généré pour: {prompt}\n// Ceci est une simulation de code généré par Qwen"
    
    async def call_mistral_local(self, prompt: str) -> str:
        # Simulation de réponse d'IA
        return f"Logique métier suggérée pour: {prompt}"
    
    async def generate_business_logic(self, prompt_request: PromptRequest) -> EvaluationResponse:
        try:
            generated_code = await self.call_qwen_local(prompt_request.prompt)
            return EvaluationResponse(
                generated_code=generated_code,
                rules_generated=[],
                error=None
            )
        except Exception as e:
            return EvaluationResponse(
                application=None,
                generated_code=None,
                rules_generated=[],
                error=str(e)
            )

# Moteur de règles
class RuleEngine:
    def __init__(self):
        self.rules: List[Rule] = []
        self.feedbacks: List[Feedback] = []
        
        # Ajout de règles par défaut
        self._add_default_rules()
    
    def _add_default_rules(self):
        # Règle CRM par défaut
        crm_rule = Rule(
            id=str(uuid.uuid4()),
            name="Scoring des leads",
            description="Attribuer un score aux nouveaux leads",
            condition="lead.score > 0.5",
            action="marquer_comme_chaud",
            priority=1,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        self.rules.append(crm_rule)
        
        # Règle de facturation par défaut
        billing_rule = Rule(
            id=str(uuid.uuid4()),
            name="Rappel de facture impayée",
            description="Envoyer un rappel quand une facture est impayée",
            condition="facture.date_echeance <= aujourd'hui()",
            action="envoyer_rappel",
            priority=1,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        self.rules.append(billing_rule)
    
    def add_rule(self, rule: Rule):
        self.rules.append(rule)
    
    def get_rules(self) -> List[Rule]:
        return self.rules
    
    def add_feedback(self, feedback: Feedback):
        self.feedbacks.append(feedback)
    
    def apply_rules(self, business_prompt: str) -> List[Dict]:
        # Retourne toutes les règles pour simplification
        return [asdict(rule) for rule in self.rules]
    
    def update_rule_based_on_feedback(self, feedback: Feedback):
        # Trouver la règle qui a reçu le feedback
        for rule in self.rules:
            if rule.id == feedback.rule_id:
                if not feedback.is_relevant:
                    rule.priority = max(0, rule.priority - 1)
                else:
                    rule.priority = min(10, rule.priority + 1)
                rule.updated_at = datetime.now().isoformat()
                break

# Application FastAPI
app = FastAPI(title="PYOCH Prototype", description="Prototype de la plateforme PYOCH")

# État global de l'application
ai_engine = AIEngine()
rule_engine = RuleEngine()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "pyoch-prototype"}

@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_prompt(request: PromptRequest):
    response = await ai_engine.generate_business_logic(request)
    
    # Appliquer les règles au prompt
    rules = rule_engine.apply_rules(request.prompt)
    response.rules_generated = rules
    
    return response

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    feedback_obj = Feedback(
        id=str(uuid.uuid4()),
        rule_id=feedback.rule_id,
        is_relevant=feedback.is_relevant,
        user_comment=feedback.user_comment,
        timestamp=datetime.now().isoformat()
    )
    
    rule_engine.add_feedback(feedback_obj)
    rule_engine.update_rule_based_on_feedback(feedback_obj)
    
    return {"status": "feedback received", "id": feedback_obj.id}

@app.get("/app-types")
async def get_application_types():
    return [
        {"type": "crm", "name": "CRM", "description": "Customer Relationship Management"},
        {"type": "billing", "name": "Billing System", "description": "Invoice and billing management"},
        {"type": "project", "name": "Project Management", "description": "Project tracking and management"},
        {"type": "inventory", "name": "Inventory Management", "description": "Stock and inventory tracking"},
        {"type": "hr", "name": "HR Management", "description": "Human resources management"}
    ]

@app.get("/")
async def read_root():
    # Retourne un HTML simple pour l'interface utilisateur
    html_content = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PYOCH - Prototype</title>
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
            #prompt { 
                width: 100%; 
                height: 100px; 
                margin-bottom: 10px; 
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 16px;
            }
            .button-group {
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
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
            #response { 
                width: 100%; 
                min-height: 300px; 
                border: 1px solid #ccc; 
                padding: 15px; 
                white-space: pre-wrap;
                background-color: #f9f9f9;
                border-radius: 4px;
                overflow: auto;
                font-family: monospace;
            }
            .feedback-section {
                margin-top: 20px;
                padding: 15px;
                background-color: #f0f8ff;
                border-radius: 4px;
            }
            .app-type-selector {
                margin-bottom: 20px;
            }
            .app-type-selector label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            .app-type-selector select {
                width: 100%;
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            .loading {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid rgba(255,255,255,.3);
                border-radius: 50%;
                border-top-color: #fff;
                animation: spin 1s ease-in-out infinite;
                margin-right: 10px;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PYOCH - Prototype de Générateur d'Applications Métiers</h1>
            
            <div class="app-type-selector">
                <label for="appType">Type d'application métier:</label>
                <select id="appType">
                    <option value="">Sélectionnez un type d'application</option>
                </select>
            </div>
            
            <textarea id="prompt" placeholder="Décrivez votre besoin métier..."></textarea>
            
            <div class="button-group">
                <button id="sendBtn" onclick="sendPrompt()">Envoyer</button>
                <button id="clearBtn" onclick="clearResponse()">Effacer</button>
            </div>
            
            <div id="response"></div>
            
            <div class="feedback-section">
                <h3>Feedback</h3>
                <p>Évaluez la pertinence des règles générées:</p>
                <button onclick="submitFeedback(true)">Pertinent</button>
                <button onclick="submitFeedback(false)">Non pertinent</button>
            </div>
        </div>

        <script>
            // Charger les types d'application au chargement de la page
            document.addEventListener('DOMContentLoaded', function() {
                loadAppTypes();
            });
            
            async function loadAppTypes() {
                try {
                    const response = await fetch('/app-types');
                    const appTypes = await response.json();
                    
                    const select = document.getElementById('appType');
                    appTypes.forEach(appType => {
                        const option = document.createElement('option');
                        option.value = appType.type;
                        option.textContent = appType.name;
                        select.appendChild(option);
                    });
                } catch (error) {
                    console.error('Erreur lors du chargement des types d\'application:', error);
                }
            }
            
            async function sendPrompt() {
                const prompt = document.getElementById('prompt').value;
                const responseDiv = document.getElementById('response');
                const sendBtn = document.getElementById('sendBtn');
                
                if (!prompt.trim()) {
                    alert('Veuillez entrer un prompt');
                    return;
                }
                
                // Afficher l'état de chargement
                sendBtn.disabled = true;
                sendBtn.innerHTML = '<div class="loading"></div>Envoi en cours...';
                responseDiv.textContent = 'Envoi du prompt en cours...';
                
                try {
                    const appType = document.getElementById('appType').value;
                    const fullPrompt = appType ? `[${appType.toUpperCase()}] ${prompt}` : prompt;
                    
                    const response = await fetch('/evaluate', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ prompt: fullPrompt }),
                    });
                    
                    const result = await response.json();
                    
                    if (result.error) {
                        responseDiv.textContent = `Erreur: ${result.error}`;
                    } else {
                        responseDiv.textContent = JSON.stringify(result, null, 2);
                    }
                } catch (error) {
                    responseDiv.textContent = `Erreur de connexion: ${error.message}`;
                } finally {
                    // Réinitialiser l'état du bouton
                    sendBtn.disabled = false;
                    sendBtn.textContent = 'Envoyer';
                }
            }
            
            function clearResponse() {
                document.getElementById('response').textContent = '';
                document.getElementById('prompt').value = '';
            }
            
            async function submitFeedback(isRelevant) {
                const responseDiv = document.getElementById('response');
                if (!responseDiv.textContent) {
                    alert('Veuillez d\'abord générer une réponse avant de fournir un feedback');
                    return;
                }
                
                try {
                    const feedbackResponse = await fetch('/feedback', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            rule_id: "placeholder-rule-id", // Dans une vraie app, ce serait l'ID réel de la règle
                            is_relevant: isRelevant,
                            user_comment: isRelevant ? "Règle pertinente" : "Règle non pertinente"
                        }),
                    });
                    
                    const result = await feedbackResponse.json();
                    alert(`Feedback ${isRelevant ? 'positif' : 'négatif'} envoyé: ${result.status}`);
                } catch (error) {
                    alert(`Erreur lors de l'envoi du feedback: ${error.message}`);
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

from starlette.responses import HTMLResponse

if __name__ == "__main__":
    print("Démarrage du prototype PYOCH...")
    print("L'API sera disponible à l'adresse: http://localhost:8000")
    print("Interface web: http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)