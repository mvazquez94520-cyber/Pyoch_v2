use serde::{Deserialize, Serialize};
use std::env;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AppConfig {
    pub server_port: u16,
    pub database: DatabaseConfig,
    pub ai_models: AIModelConfig,
    pub security: SecurityConfig,
    pub logging: LoggingConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    pub url: String,
    pub max_connections: u32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AIModelConfig {
    pub mistral_url: String,
    pub qwen_url: String,
    pub timeout_seconds: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityConfig {
    pub jwt_secret: String,
    pub api_key: String,
    pub rate_limit_requests: u32,
    pub rate_limit_window: u64, // in seconds
    pub allowed_origins: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LoggingConfig {
    pub level: String,
    pub log_file: Option<String>,
    pub enable_console_logging: bool,
    pub retention_days: u32,
}

impl AppConfig {
    pub fn from_env() -> Result<Self, Box<dyn std::error::Error>> {
        Ok(AppConfig {
            server_port: env::var("SERVER_PORT")
                .unwrap_or_else(|_| "8080".to_string())
                .parse()
                .unwrap_or(8080),
            database: DatabaseConfig {
                url: env::var("DATABASE_URL").unwrap_or_else(|_| "postgresql://localhost/pyoch".to_string()),
                max_connections: env::var("DB_MAX_CONNECTIONS")
                    .unwrap_or_else(|_| "20".to_string())
                    .parse()
                    .unwrap_or(20),
            },
            ai_models: AIModelConfig {
                mistral_url: env::var("MISTRAL_URL").unwrap_or_else(|_| "http://localhost:11434/v1/completions".to_string()),
                qwen_url: env::var("QWEN_URL").unwrap_or_else(|_| "http://localhost:11435/v1/completions".to_string()),
                timeout_seconds: env::var("AI_TIMEOUT_SECONDS")
                    .unwrap_or_else(|_| "60".to_string())
                    .parse()
                    .unwrap_or(60),
            },
            security: SecurityConfig {
                jwt_secret: env::var("JWT_SECRET").unwrap_or_else(|_| "default_secret_key_change_in_production".to_string()),
                api_key: env::var("API_KEY").unwrap_or_else(|_| "default_api_key_change_in_production".to_string()),
                rate_limit_requests: env::var("RATE_LIMIT_REQUESTS")
                    .unwrap_or_else(|_| "100".to_string())
                    .parse()
                    .unwrap_or(100),
                rate_limit_window: env::var("RATE_LIMIT_WINDOW")
                    .unwrap_or_else(|_| "60".to_string())
                    .parse()
                    .unwrap_or(60),
                allowed_origins: env::var("ALLOWED_ORIGINS")
                    .unwrap_or_else(|_| "http://localhost:3000,http://localhost:5173".to_string())
                    .split(',')
                    .map(|s| s.trim().to_string())
                    .collect(),
            },
            logging: LoggingConfig {
                level: env::var("LOG_LEVEL").unwrap_or_else(|_| "info".to_string()),
                log_file: env::var("LOG_FILE").ok(),
                enable_console_logging: env::var("ENABLE_CONSOLE_LOGGING")
                    .unwrap_or_else(|_| "true".to_string())
                    .parse()
                    .unwrap_or(true),
                retention_days: env::var("LOG_RETENTION_DAYS")
                    .unwrap_or_else(|_| "30".to_string())
                    .parse()
                    .unwrap_or(30),
            },
        })
    }

    pub fn validate(&self) -> Result<(), String> {
        // Validate database URL
        if self.database.url.is_empty() {
            return Err("Database URL cannot be empty".to_string());
        }

        // Validate AI model URLs
        if self.ai_models.mistral_url.is_empty() {
            return Err("Mistral URL cannot be empty".to_string());
        }

        if self.ai_models.qwen_url.is_empty() {
            return Err("Qwen URL cannot be empty".to_string());
        }

        // Validate port
        if self.server_port == 0 {
            return Err("Server port must be greater than 0".to_string());
        }

        // Validate timeout
        if self.ai_models.timeout_seconds == 0 {
            return Err("AI timeout must be greater than 0".to_string());
        }

        Ok(())
    }
}

// Helper function to initialize environment from a config file
pub fn load_config_from_file(path: &str) -> Result<AppConfig, Box<dyn std::error::Error>> {
    let contents = std::fs::read_to_string(path)?;
    let config: AppConfig = serde_json::from_str(&contents)?;
    config.validate().map_err(|e| e.into())?;
    Ok(config)
}

// Default configuration for development
pub fn default_dev_config() -> AppConfig {
    AppConfig {
        server_port: 8080,
        database: DatabaseConfig {
            url: "postgresql://localhost/pyoch_dev".to_string(),
            max_connections: 10,
        },
        ai_models: AIModelConfig {
            mistral_url: "http://localhost:11434/v1/completions".to_string(),
            qwen_url: "http://localhost:11435/v1/completions".to_string(),
            timeout_seconds: 60,
        },
        security: SecurityConfig {
            jwt_secret: "dev_jwt_secret_key".to_string(),
            api_key: "dev_api_key".to_string(),
            rate_limit_requests: 1000,
            rate_limit_window: 60,
            allowed_origins: vec![
                "http://localhost:3000".to_string(),
                "http://localhost:5173".to_string(),
                "http://localhost:8080".to_string(),
            ],
        },
        logging: LoggingConfig {
            level: "debug".to_string(),
            log_file: Some("./logs/app.log".to_string()),
            enable_console_logging: true,
            retention_days: 7,
        },
    }
}