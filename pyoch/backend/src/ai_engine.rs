use reqwest::Client;
use serde_json::Value;
use anyhow::Result;
use crate::models::{PromptRequest, EvaluationResponse};
use std::env;
use crate::config::AIConfig;

pub struct AIEngine {
    client: Client,
    config: AIConfig,
}

impl AIEngine {
    pub fn new() -> Self {
        AIEngine {
            client: Client::new(),
            config: AIConfig::new(),
        }
    }

    pub async fn call_qwen_local(&self, prompt: &str) -> Result<String> {
        let response = self.client
            .post(&self.config.qwen_endpoint)
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
            .post(&self.config.mistral_endpoint)
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
            .post(&self.config.openai_endpoint)
            .header("Authorization", format!("Bearer {}", api_key))
            .header("Content-Type", "application/json")
            .json(&serde_json::json!({
                "model": "gpt-3.5-turbo-instruct", // Using the instruct model which is similar to the old completions API
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
        // Try local Qwen first
        if let Ok(result) = self.call_qwen_local(&prompt_request.prompt).await {
            println!("Successfully used local Qwen model");
            return Ok(EvaluationResponse {
                application: None,
                generated_code: Some(result),
                rules_generated: vec![],
                error: None,
            });
        }
        
        // If Qwen fails, try local Mistral
        if let Ok(result) = self.call_mistral_local(&prompt_request.prompt).await {
            println!("Successfully used local Mistral model");
            return Ok(EvaluationResponse {
                application: None,
                generated_code: Some(result),
                rules_generated: vec![],
                error: None,
            });
        }
        
        // If both local models fail, use PYOCH's own logic (fallback implementation)
        println!("Both local models failed, using PYOCH's own brain");
        let fallback_result = self.poch_brain_fallback(&prompt_request.prompt).await;
        
        // If fallback also fails, try OpenAI as backup if API key is available
        if fallback_result.is_err() {
            if let Ok(api_key) = env::var("OPENAI_API_KEY") {
                println!("Using OpenAI as backup");
                if let Ok(result) = self.call_openai_cloud(&prompt_request.prompt, &api_key).await {
                    return Ok(EvaluationResponse {
                        application: None,
                        generated_code: Some(result),
                        rules_generated: vec![],
                        error: None,
                    });
                }
            }
        }
        
        // Return the fallback result or an error if everything failed
        match fallback_result {
            Ok(result) => {
                Ok(EvaluationResponse {
                    application: None,
                    generated_code: Some(result),
                    rules_generated: vec![],
                    error: None,
                })
            }
            Err(e) => {
                Ok(EvaluationResponse {
                    application: None,
                    generated_code: None,
                    rules_generated: vec![],
                    error: Some(format!("All AI connectors failed: {}", e)),
                })
            }
        }
    }

    // PYOCH's own brain implementation - this would contain the core logic
    async fn poch_brain_fallback(&self, prompt: &str) -> Result<String> {
        // This is where PYOCH's own logic would be implemented
        // For now, we'll return a basic implementation
        println!("PYOCH is thinking with its own brain...");
        
        // A simple fallback implementation - in reality this would contain
        // PYOCH's own business logic generation algorithms
        let response = format!(
            "PYOCH's own brain response to: {}\n\nThis is a fallback response from PYOCH's internal logic system.",
            prompt
        );
        
        Ok(response)
    }
}