use reqwest::Client;
use serde_json::Value;
use anyhow::Result;
use crate::models::{PromptRequest, EvaluationResponse};

pub struct AIEngine {
    client: Client,
}

impl AIEngine {
    pub fn new() -> Self {
        AIEngine {
            client: Client::new(),
        }
    }

    pub async fn call_qwen_local(&self, prompt: &str) -> Result<String> {
        let response = self.client
            .post("http://localhost:11434/api/generate")
            .json(&serde_json::json!({
                "model": "qwen:latest",
                "prompt": prompt,
                "stream": false
            }))
            .send()
            .await?;

        let json_response: Value = response.json().await?;
        let response_text = json_response["response"].as_str().unwrap_or_default().to_string();

        Ok(response_text)
    }

    pub async fn call_mistral_local(&self, prompt: &str) -> Result<String> {
        let response = self.client
            .post("http://localhost:11434/api/generate")
            .json(&serde_json::json!({
                "model": "mistral:latest",
                "prompt": prompt,
                "stream": false
            }))
            .send()
            .await?;

        let json_response: Value = response.json().await?;
        let response_text = json_response["response"].as_str().unwrap_or_default().to_string();

        Ok(response_text)
    }

    pub async fn call_openai_cloud(&self, prompt: &str, api_key: &str) -> Result<String> {
        let response = self.client
            .post("https://api.openai.com/v1/completions")
            .header("Authorization", format!("Bearer {}", api_key))
            .header("Content-Type", "application/json")
            .json(&serde_json::json!({
                "model": "text-davinci-003",
                "prompt": prompt,
                "max_tokens": 2048,
                "temperature": 0.7
            }))
            .send()
            .await?;

        let json_response: Value = response.json().await?;
        let response_text = json_response["choices"][0]["text"].as_str().unwrap_or_default().to_string();

        Ok(response_text)
    }

    pub async fn generate_backend_preview(&self, prompt: &str) -> String {
        // Simulation de génération de code backend
        let app_type = if prompt.to_lowercase().contains("api") || prompt.to_lowercase().contains("backend") {
            "api"
        } else {
            "web"
        };
        
        format!(r#"// Aperçu Backend pour: {}
// Type d'application: {}

const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Routes API simulées
app.get('/api/data', (req, res) => {{
  res.json({{ message: 'Données de l\'application', prompt: '{}' }});
}});

app.listen(PORT, () => {{
  console.log(`Serveur {} démarré sur le port ${{PORT}}`);
}});

// Modèles de données simulés
class BusinessModel {{
  constructor(data) {{
    this.data = data;
    this.createdAt = new Date();
  }}
  
  async save() {{
    // Logique de sauvegarde simulée
    console.log('Données sauvegardées:', this.data);
    return this;
  }}
}}
"#, prompt, app_type, prompt, app_type)
    }

    pub async fn generate_frontend_preview(&self, prompt: &str) -> String {
        // Simulation de génération de code frontend
        let framework = if prompt.to_lowercase().contains("react") {
            "React"
        } else {
            "HTML/JS"
        };
        
        format!(r#"<!-- Aperçu Frontend pour: {} -->
<!-- Framework: {} -->

<!DOCTYPE html>
<html>
<head>
  <title>Preview - {}...</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    .container {{ max-width: 800px; margin: 0 auto; }}
    .component {{ border: 1px solid #ccc; padding: 15px; margin: 10px 0; border-radius: 5px; }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Application: {}</h1>
    <div class="component">
      <h2>Interface Utilisateur</h2>
      <p>Cette interface serait générée dynamiquement selon vos besoins métier.</p>
      <button onclick="handleAction()">Exécuter Action</button>
    </div>
  </div>

  <script>
    function handleAction() {{
      alert('Action simulée pour: {}');
    }}
    
    // Logique métier simulée
    console.log('Frontend chargé pour: {}');
  </script>
</body>
</html>
"#, prompt, framework, if prompt.len() > 30 { &prompt[..30] } else { prompt }, prompt, prompt, prompt)
    }

    pub async fn generate_business_logic(&self, prompt_request: &PromptRequest) -> Result<EvaluationResponse> {
        // First try local Qwen
        let result = self.call_qwen_local(&prompt_request.prompt).await?;
        
        // For now, return a basic response - in a real implementation, 
        // we would parse the AI response to extract rules and application structure
        Ok(EvaluationResponse {
            application: None,
            generated_code: Some(result),
            rules_generated: vec![],
            backend_preview: None,
            frontend_preview: None,
            error: None,
        })
    }
}