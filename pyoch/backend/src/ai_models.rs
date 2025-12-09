use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;
use reqwest;
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AIModelConfig {
    pub mistral_url: String,
    pub qwen_url: String,
    pub timeout_seconds: u64,
}

pub struct AIModelManager {
    pub config: AIModelConfig,
    pub client: reqwest::Client,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AIRequest {
    pub prompt: String,
    pub max_tokens: Option<u32>,
    pub temperature: Option<f32>,
    pub model: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AIResponse {
    pub response: String,
    pub model_used: String,
    pub tokens_used: Option<u32>,
    pub execution_time: f64,
}

impl AIModelManager {
    pub fn new(config: AIModelConfig) -> Self {
        let client = reqwest::Client::builder()
            .timeout(std::time::Duration::from_secs(config.timeout_seconds))
            .build()
            .expect("Failed to build reqwest client");

        AIModelManager {
            config,
            client,
        }
    }

    pub async fn generate_with_mistral(&self, request: &AIRequest) -> Result<AIResponse, Box<dyn std::error::Error>> {
        let start_time = std::time::Instant::now();

        let payload = serde_json::json!({
            "prompt": request.prompt,
            "max_tokens": request.max_tokens.unwrap_or(512),
            "temperature": request.temperature.unwrap_or(0.7),
            "stream": false
        });

        let response = self.client
            .post(&self.config.mistral_url)
            .header("Content-Type", "application/json")
            .json(&payload)
            .send()
            .await?;

        if !response.status().is_success() {
            return Err(format!("Mistral API error: {}", response.status()).into());
        }

        let json_response: serde_json::Value = response.json().await?;
        
        let response_text = json_response
            .get("response")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let tokens_used = json_response
            .get("usage")
            .and_then(|u| u.get("total_tokens"))
            .and_then(|t| t.as_u64())
            .map(|t| t as u32);

        Ok(AIResponse {
            response: response_text,
            model_used: "mistral".to_string(),
            tokens_used,
            execution_time: start_time.elapsed().as_secs_f64(),
        })
    }

    pub async fn generate_with_qwen(&self, request: &AIRequest) -> Result<AIResponse, Box<dyn std::error::Error>> {
        let start_time = std::time::Instant::now();

        let payload = serde_json::json!({
            "prompt": request.prompt,
            "max_tokens": request.max_tokens.unwrap_or(512),
            "temperature": request.temperature.unwrap_or(0.7),
            "stream": false
        });

        let response = self.client
            .post(&self.config.qwen_url)
            .header("Content-Type", "application/json")
            .json(&payload)
            .send()
            .await?;

        if !response.status().is_success() {
            return Err(format!("Qwen API error: {}", response.status()).into());
        }

        let json_response: serde_json::Value = response.json().await?;
        
        let response_text = json_response
            .get("response")
            .and_then(|v| v.as_str())
            .unwrap_or("")
            .to_string();

        let tokens_used = json_response
            .get("usage")
            .and_then(|u| u.get("total_tokens"))
            .and_then(|t| t.as_u64())
            .map(|t| t as u32);

        Ok(AIResponse {
            response: response_text,
            model_used: "qwen".to_string(),
            tokens_used,
            execution_time: start_time.elapsed().as_secs_f64(),
        })
    }

    pub async fn generate_with_model(&self, request: &AIRequest) -> Result<AIResponse, Box<dyn std::error::Error>> {
        match request.model.to_lowercase().as_str() {
            "mistral" => self.generate_with_mistral(request).await,
            "qwen" => self.generate_with_qwen(request).await,
            _ => {
                // Default to mistral if model is not specified or unknown
                self.generate_with_mistral(request).await
            }
        }
    }

    pub async fn generate_optimal(&self, request: &AIRequest) -> Result<AIResponse, Box<dyn std::error::Error>> {
        // Try both models and return the one that responds faster or has better quality
        // For now, we'll just try mistral first and fall back to qwen if needed
        match self.generate_with_mistral(request).await {
            Ok(response) => Ok(response),
            Err(_) => {
                // If mistral fails, try qwen
                self.generate_with_qwen(request).await
            }
        }
    }

    pub async fn health_check(&self) -> Result<HashMap<String, bool>, Box<dyn std::error::Error>> {
        let mut results = HashMap::new();
        
        // Check Mistral
        match self.client.get(&self.config.mistral_url.replace("/v1/completions", "/health"))
            .send()
            .await
        {
            Ok(resp) => {
                results.insert("mistral".to_string(), resp.status().is_success());
            }
            Err(_) => {
                results.insert("mistral".to_string(), false);
            }
        }

        // Check Qwen
        match self.client.get(&self.config.qwen_url.replace("/v1/completions", "/health"))
            .send()
            .await
        {
            Ok(resp) => {
                results.insert("qwen".to_string(), resp.status().is_success());
            }
            Err(_) => {
                results.insert("qwen".to_string(), false);
            }
        }

        Ok(results)
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelLoadBalancer {
    pub models: Vec<String>,
    pub current_index: usize,
    pub model_stats: HashMap<String, ModelStats>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ModelStats {
    pub requests_count: u64,
    pub avg_response_time: f64,
    pub errors_count: u64,
}

impl ModelLoadBalancer {
    pub fn new() -> Self {
        ModelLoadBalancer {
            models: vec!["mistral".to_string(), "qwen".to_string()],
            current_index: 0,
            model_stats: HashMap::new(),
        }
    }

    pub fn get_next_model(&mut self) -> String {
        if self.models.is_empty() {
            return "mistral".to_string();
        }
        
        let model = self.models[self.current_index].clone();
        self.current_index = (self.current_index + 1) % self.models.len();
        model
    }

    pub fn update_model_stats(&mut self, model: &str, response_time: f64, success: bool) {
        let stats = self.model_stats.entry(model.to_string()).or_insert(ModelStats {
            requests_count: 0,
            avg_response_time: 0.0,
            errors_count: 0,
        });

        stats.requests_count += 1;
        
        // Update average response time
        stats.avg_response_time = 
            (stats.avg_response_time * (stats.requests_count - 1) as f64 + response_time) / stats.requests_count as f64;
        
        if !success {
            stats.errors_count += 1;
        }
    }

    pub fn get_best_model(&self) -> String {
        if self.model_stats.is_empty() {
            return "mistral".to_string();
        }

        let mut best_model = "mistral".to_string();
        let mut best_score = f64::MAX; // Lower is better

        for (model, stats) in &self.model_stats {
            // Calculate a score based on response time and error rate
            let error_rate = stats.errors_count as f64 / stats.requests_count as f64;
            let score = stats.avg_response_time + (error_rate * 10.0); // Penalty for errors
            
            if score < best_score {
                best_score = score;
                best_model = model.clone();
            }
        }

        best_model
    }
}