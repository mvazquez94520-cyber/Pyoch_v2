/// Configuration for AI Connectors
pub struct AIConfig {
    pub qwen_endpoint: String,
    pub mistral_endpoint: String,
    pub openai_api_key: Option<String>,
    pub openai_endpoint: String,
    pub local_model_timeout: u64,
}

impl AIConfig {
    pub fn new() -> Self {
        AIConfig {
            qwen_endpoint: std::env::var("QWEN_ENDPOINT")
                .unwrap_or_else(|_| "http://localhost:11434/api/generate".to_string()),
            mistral_endpoint: std::env::var("MISTRAL_ENDPOINT")
                .unwrap_or_else(|_| "http://localhost:11434/api/generate".to_string()),
            openai_api_key: std::env::var("OPENAI_API_KEY").ok(),
            openai_endpoint: std::env::var("OPENAI_ENDPOINT")
                .unwrap_or_else(|_| "https://api.openai.com/v1/chat/completions".to_string()),
            local_model_timeout: 30, // 30 seconds timeout
        }
    }
}