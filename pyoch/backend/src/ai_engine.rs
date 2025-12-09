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

    pub async fn generate_business_logic(&self, prompt_request: &PromptRequest) -> Result<EvaluationResponse> {
        // First try local Qwen
        let result = self.call_qwen_local(&prompt_request.prompt).await?;
        
        // For now, return a basic response - in a real implementation, 
        // we would parse the AI response to extract rules and application structure
        Ok(EvaluationResponse {
            application: None,
            generated_code: Some(result),
            rules_generated: vec![],
            error: None,
        })
    }
}