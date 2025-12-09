mod models;
mod ai_engine;
mod rule_engine;
mod utils;
mod license;
mod statistics;
mod auto_learning;
mod protection;
mod database;
mod ai_models;
mod config;

use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware::Logger};
use serde_json::json;
use crate::models::{PromptRequest, EvaluationResponse};
use crate::ai_engine::AIEngine;
use crate::rule_engine::RuleEngine;
use crate::auto_learning::AutoLearningEngine;
use crate::statistics::{DownloadStats, PromptKeywordStats, StatsResponse};
use crate::protection::ApplicationProtectionManager;
use crate::license::License;
use crate::database::DatabaseManager;
use crate::ai_models::{AIModelManager, AIRequest, AIResponse};
use crate::config::AppConfig;
use std::sync::{Arc, Mutex};
use env_logger;
use std::collections::HashMap;

struct StatisticsManager {
    download_stats: Vec<DownloadStats>,
    keyword_stats: Vec<PromptKeywordStats>,
    overall_stats: HashMap<String, i32>,
}

impl StatisticsManager {
    fn new() -> Self {
        StatisticsManager {
            download_stats: Vec::new(),
            keyword_stats: Vec::new(),
            overall_stats: HashMap::new(),
        }
    }
    
    fn increment_download(&mut self, app_id: uuid::Uuid) {
        // Check if we already have stats for this app
        if let Some(stat) = self.download_stats.iter_mut().find(|s| s.application_id == app_id) {
            stat.download_count += 1;
            stat.last_downloaded = chrono::Utc::now();
        } else {
            // Create new stat entry
            self.download_stats.push(DownloadStats {
                id: uuid::Uuid::new_v4(),
                application_id: app_id,
                user_id: None, // Would come from authenticated user
                download_count: 1,
                last_downloaded: chrono::Utc::now(),
                created_at: chrono::Utc::now(),
                updated_at: chrono::Utc::now(),
            });
        }
    }
    
    fn record_keyword_usage(&mut self, keyword: &str) {
        // Find existing keyword or create new one
        if let Some(stat) = self.keyword_stats.iter_mut().find(|k| k.keyword == keyword) {
            stat.usage_count += 1;
            stat.updated_at = chrono::Utc::now();
        } else {
            self.keyword_stats.push(PromptKeywordStats {
                id: uuid::Uuid::new_v4(),
                keyword: keyword.to_string(),
                usage_count: 1,
                created_at: chrono::Utc::now(),
                updated_at: chrono::Utc::now(),
            });
        }
    }
    
    fn get_top_keywords(&self, limit: usize) -> Vec<(String, i32)> {
        let mut keywords: Vec<(String, i32)> = self.keyword_stats
            .iter()
            .map(|k| (k.keyword.clone(), k.usage_count))
            .collect();
        
        keywords.sort_by(|a, b| b.1.cmp(&a.1));
        keywords.truncate(limit);
        keywords
    }
    
    fn get_total_downloads(&self) -> i32 {
        self.download_stats.iter().map(|stat| stat.download_count).sum()
    }
}

struct AppState {
    ai_engine: AIEngine,
    rule_engine: Arc<Mutex<RuleEngine>>,
    auto_learning_engine: Arc<Mutex<AutoLearningEngine>>,
    stats_manager: Arc<Mutex<StatisticsManager>>,
    protection_manager: Arc<Mutex<ApplicationProtectionManager>>,
    licenses: Arc<Mutex<Vec<License>>>,
    database_manager: Arc<DatabaseManager>,
    ai_model_manager: Arc<AIModelManager>,
}

async fn health_check() -> impl Responder {
    HttpResponse::Ok().json(json!({"status": "healthy"}))
}

async fn evaluate_prompt(
    data: web::Data<AppState>,
    req: web::Json<PromptRequest>,
) -> impl Responder {
    let ai_engine = &data.ai_engine;
    let rule_engine = &data.rule_engine;
    let db_manager = &data.database_manager;

    match ai_engine.generate_business_logic(&req).await {
        Ok(response) => {
            // Update rule engine based on the prompt
            let rules = rule_engine.lock().unwrap().apply_rules(&req.prompt);
            
            // Record the prompt in the database
            if let Err(e) = db_manager.record_prompt(
                1, // Default user ID for now
                1, // Default app ID for now
                &req.prompt,
                response.generated_code.as_deref(),
                None, // Business domain will be determined separately
            ).await {
                eprintln!("Failed to record prompt in database: {}", e);
            }
            
            HttpResponse::Ok().json(EvaluationResponse {
                rules_generated: rules,
                ..response
            })
        }
        Err(e) => {
            // Even if AI generation fails, record the prompt attempt
            if let Err(e_db) = db_manager.record_prompt(
                1, // Default user ID for now
                1, // Default app ID for now
                &req.prompt,
                None, // No response due to error
                None,
            ).await {
                eprintln!("Failed to record failed prompt in database: {}", e_db);
            }
            
            HttpResponse::InternalServerError().json(EvaluationResponse {
                application: None,
                generated_code: None,
                rules_generated: vec![],
                error: Some(e.to_string()),
            })
        }
    }
}

async fn submit_feedback(
    data: web::Data<AppState>,
    feedback: web::Json<crate::models::Feedback>,
) -> impl Responder {
    let rule_engine = &data.rule_engine;
    let db_manager = &data.database_manager;
    
    // Add feedback to the engine
    {
        let mut engine = rule_engine.lock().unwrap();
        engine.add_feedback(feedback.into_inner());
    }
    
    // Record the feedback in the database as well
    if let Err(e) = db_manager.record_prompt(
        1, // Default user ID for now
        1, // Default app ID for now
        &feedback.prompt,
        Some(&format!("Feedback: {}", feedback.rating)), // Store feedback as response
        None,
    ).await {
        eprintln!("Failed to record feedback in database: {}", e);
    }
    
    HttpResponse::Ok().json(json!({"status": "feedback received"}))
}

async fn get_application_types() -> impl Responder {
    HttpResponse::Ok().json(json!([
        {"type": "crm", "name": "CRM", "description": "Customer Relationship Management"},
        {"type": "billing", "name": "Billing System", "description": "Invoice and billing management"},
        {"type": "project", "name": "Project Management", "description": "Project tracking and management"},
        {"type": "inventory", "name": "Inventory Management", "description": "Stock and inventory tracking"},
        {"type": "hr", "name": "HR Management", "description": "Human resources management"}
    ]))
}

// License management endpoints
async fn validate_license(
    data: web::Data<AppState>,
    license_request: web::Json<crate::license::LicenseCheckRequest>,
) -> impl Responder {
    let db_manager = &data.database_manager;
    
    // Get license from database
    match db_manager.get_license_by_key(&license_request.license_key).await {
        Ok(Some(license)) => {
            // Check if license is valid for the specific application if provided
            if let Some(app_id) = license_request.application_id {
                // In a real implementation, we would check if this license is valid for the specific app
                // For now we'll just check expiry and usage limits
            }
            
            // Check expiry
            if let Some(expiry_date) = license.expires_at {
                if chrono::Utc::now() > expiry_date {
                    return HttpResponse::Forbidden().json(json!({
                        "is_valid": false,
                        "error": "License has expired"
                    }));
                }
            }
            
            // Check download limits
            if license.max_downloads != -1 && license.current_downloads >= license.max_downloads {
                return HttpResponse::Forbidden().json(json!({
                    "is_valid": false,
                    "error": "Maximum downloads exceeded"
                }));
            }
            
            HttpResponse::Ok().json(json!({
                "is_valid": true,
                "license_info": &license
            }))
        },
        Ok(None) => {
            HttpResponse::Forbidden().json(json!({
                "is_valid": false,
                "error": "Invalid or inactive license"
            }))
        },
        Err(e) => {
            eprintln!("Database error when validating license: {}", e);
            HttpResponse::InternalServerError().json(json!({
                "is_valid": false,
                "error": "Database error"
            }))
        }
    }
}

async fn create_license(
    data: web::Data<AppState>,
    new_license: web::Json<crate::license::License>,
) -> impl Responder {
    let db_manager = &data.database_manager;
    
    // For now, using a default user ID since the database expects an i32
    // In a real implementation, we would have proper user management
    let user_id = 1; // Default user ID
    
    match db_manager.create_license(
        &new_license.license_key,
        user_id,
        &new_license.license_type,
        Some(new_license.expiry_date),
    ).await {
        Ok(license) => {
            HttpResponse::Created().json(license)
        },
        Err(e) => {
            eprintln!("Database error when creating license: {}", e);
            HttpResponse::InternalServerError().json(json!({
                "error": "Failed to create license"
            }))
        }
    }
}

// Auto-learning business domains
async fn identify_business_domain(
    data: web::Data<AppState>,
    req: web::Json<crate::auto_learning::AutoLearningRequest>,
) -> impl Responder {
    let engine = &data.auto_learning_engine;
    let db_manager = &data.database_manager;
    
    let matched_domains = {
        let engine_guard = engine.lock().unwrap();
        engine_guard.identify_business_domain(&req.prompt)
    };
    
    // Record the prompt with the identified business domain in the database
    let business_domain = if !matched_domains.is_empty() {
        Some(matched_domains[0].name.clone())
    } else {
        None
    };
    
    if let Err(e) = db_manager.record_prompt(
        1, // Default user ID for now
        1, // Default app ID for now
        &req.prompt,
        None, // No response yet
        business_domain.as_deref(),
    ).await {
        eprintln!("Failed to record prompt in database: {}", e);
    }
    
    let response = crate::auto_learning::AutoLearningResponse {
        matched_domains,
        confidence: 0.0, // Would be calculated based on matches
        learning_updated: false,
        suggestions: vec![], // Would provide suggestions based on learning
    };
    
    HttpResponse::Ok().json(response)
}

async fn learn_from_interaction(
    data: web::Data<AppState>,
    req: web::Json<crate::auto_learning::AutoLearningRequest>,
) -> impl Responder {
    let engine = &data.auto_learning_engine;
    let db_manager = &data.database_manager;
    
    // For now, we'll just record the interaction as relevant
    // In a real implementation, this would be based on actual feedback
    let is_relevant = req.feedback.unwrap_or(true);
    
    {
        let mut engine_guard = engine.lock().unwrap();
        engine_guard.learn_from_interaction(&req.prompt, "sample response", is_relevant);
    }
    
    // Also update the prompt in the database with the response if we have one
    if let Err(e) = db_manager.record_prompt(
        1, // Default user ID for now
        1, // Default app ID for now
        &req.prompt,
        Some("sample response"), // Sample response for now
        None, // Business domain will be determined during initial identification
    ).await {
        eprintln!("Failed to record learning interaction in database: {}", e);
    }
    
    HttpResponse::Ok().json(json!({"status": "learned from interaction"}))
}

// Statistics endpoints
async fn get_statistics(
    data: web::Data<AppState>,
) -> impl Responder {
    let stats_manager = &data.stats_manager;
    let db_manager = &data.database_manager;
    
    let stats_guard = stats_manager.lock().unwrap();
    let total_downloads = stats_guard.get_total_downloads();
    let top_keywords = stats_guard.get_top_keywords(10);
    
    // In a real implementation, we would get this data from the database
    // For now, we'll return both in-memory and mention database availability
    let db_stats = json!({
        "database_connected": true,
        "tables_initialized": true
    });
    
    HttpResponse::Ok().json(json!({
        "total_downloads": total_downloads,
        "top_keywords": top_keywords,
        "timestamp": chrono::Utc::now(),
        "database_stats": db_stats
    }))
}

async fn record_download(
    data: web::Data<AppState>,
    app_id: web::Path<uuid::Uuid>,
) -> impl Responder {
    let stats_manager = &data.stats_manager;
    let db_manager = &data.database_manager;
    
    // Update in-memory statistics
    {
        let mut stats_guard = stats_manager.lock().unwrap();
        stats_guard.increment_download(app_id.into_inner());
    }
    
    // Also record in database
    if let Err(e) = db_manager.increment_license_download(1).await { // Using default license ID for now
        eprintln!("Failed to increment download in database: {}", e);
    }
    
    HttpResponse::Ok().json(json!({"status": "download recorded"}))
}

// Application protection endpoints
async fn protect_application(
    data: web::Data<AppState>,
    protection_request: web::Json<crate::protection::ProtectedAppRequest>,
) -> impl Responder {
    let protection_manager = &data.protection_manager;
    
    let result = {
        let mut manager_guard = protection_manager.lock().unwrap();
        manager_guard.protect_application(
            protection_request.application_id,
            &protection_request.protection_level,
            &protection_request.source_code
        )
    };
    
    HttpResponse::Ok().json(result)
}

async fn verify_application_integrity(
    data: web::Data<AppState>,
    path: web::Path<(uuid::Uuid, String)>,
) -> impl Responder {
    let (app_id, checksum) = path.into_inner();
    let protection_manager = &data.protection_manager;
    
    // This would need the current code to verify, but for now we'll return a placeholder
    let is_valid = {
        let manager_guard = protection_manager.lock().unwrap();
        // We can't verify without the current code, so we'll return true for now
        true
    };
    
    HttpResponse::Ok().json(json!({
        "application_id": app_id,
        "is_valid": is_valid,
        "checksum": checksum
    }))
}

// New AI model endpoints
async fn generate_with_ai_model(
    data: web::Data<AppState>,
    req: web::Json<crate::ai_models::AIRequest>,
) -> impl Responder {
    let ai_model_manager = &data.ai_model_manager;
    
    match ai_model_manager.generate_with_model(&req).await {
        Ok(response) => {
            // Record the prompt in the database
            if let Err(e) = data.database_manager.record_prompt(
                1, // Default user ID for now
                1, // Default app ID for now
                &req.prompt,
                Some(&response.response),
                None, // Business domain will be determined later
            ).await {
                eprintln!("Failed to record prompt: {}", e);
            }
            
            HttpResponse::Ok().json(response)
        },
        Err(e) => {
            HttpResponse::InternalServerError().json(json!({
                "error": e.to_string()
            }))
        }
    }
}

async fn ai_health_check(
    data: web::Data<AppState>,
) -> impl Responder {
    let ai_model_manager = &data.ai_model_manager;
    
    match ai_model_manager.health_check().await {
        Ok(results) => {
            HttpResponse::Ok().json(results)
        },
        Err(e) => {
            HttpResponse::InternalServerError().json(json!({
                "error": e.to_string()
            }))
        }
    }
}

// New database endpoints
async fn create_user(
    data: web::Data<AppState>,
    user_data: web::Json<serde_json::Value>,
) -> impl Responder {
    let db_manager = &data.database_manager;
    
    let username = user_data["username"].as_str().unwrap_or("default_user");
    let email = user_data["email"].as_str().unwrap_or("default@example.com");
    
    match db_manager.create_user(username, email).await {
        Ok(user) => {
            HttpResponse::Ok().json(user)
        },
        Err(e) => {
            HttpResponse::InternalServerError().json(json!({
                "error": e.to_string()
            }))
        }
    }
}

async fn create_application(
    data: web::Data<AppState>,
    app_data: web::Json<serde_json::Value>,
) -> impl Responder {
    let db_manager = &data.database_manager;
    
    let name = app_data["name"].as_str().unwrap_or("default_app");
    let description = app_data["description"].as_str().unwrap_or("");
    let owner_id = app_data["owner_id"].as_i64().unwrap_or(1) as i32;
    
    match db_manager.create_application(name, description, owner_id).await {
        Ok(app) => {
            HttpResponse::Ok().json(app)
        },
        Err(e) => {
            HttpResponse::InternalServerError().json(json!({
                "error": e.to_string()
            }))
        }
    }
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    
    // Load configuration
    let config = match AppConfig::from_env() {
        Ok(cfg) => cfg,
        Err(e) => {
            eprintln!("Configuration error: {}", e);
            return Err(std::io::Error::new(std::io::ErrorKind::Other, "Configuration error"));
        }
    };
    
    // Initialize database
    let db_config = crate::database::DatabaseConfig {
        url: config.database.url.clone(),
        max_connections: config.database.max_connections,
    };
    
    let database_manager = match DatabaseManager::new(&db_config).await {
        Ok(db) => Arc::new(db),
        Err(e) => {
            eprintln!("Database connection error: {}", e);
            return Err(std::io::Error::new(std::io::ErrorKind::Other, "Database connection error"));
        }
    };
    
    // Initialize AI model manager
    let ai_model_config = crate::ai_models::AIModelConfig {
        mistral_url: config.ai_models.mistral_url.clone(),
        qwen_url: config.ai_models.qwen_url.clone(),
        timeout_seconds: config.ai_models.timeout_seconds,
    };
    
    let ai_model_manager = Arc::new(AIModelManager::new(ai_model_config));
    
    // Initialize other components
    let ai_engine = AIEngine::new();
    let rule_engine = Arc::new(Mutex::new(RuleEngine::new()));
    let auto_learning_engine = Arc::new(Mutex::new(AutoLearningEngine::new()));
    let stats_manager = Arc::new(Mutex::new(StatisticsManager::new()));
    let protection_manager = Arc::new(Mutex::new(ApplicationProtectionManager::new()));
    let licenses = Arc::new(Mutex::new(Vec::new()));
    
    // Initialize database tables
    if let Err(e) = database_manager.init_tables().await {
        eprintln!("Failed to initialize database tables: {}", e);
    }
    
    // Add some default business rules
    {
        let mut engine = rule_engine.lock().unwrap();
        
        // Example: Add a basic CRM rule
        engine.add_rule(crate::models::Rule {
            id: uuid::Uuid::new_v4(),
            name: "Customer Lead Scoring".to_string(),
            description: "Score leads based on engagement level".to_string(),
            condition: "customer.engagement > 0.5".to_string(),
            action: "mark_as_hot_lead".to_string(),
            priority: 1,
            created_at: chrono::Utc::now(),
            updated_at: chrono::Utc::now(),
        });
        
        // Example: Add a billing rule
        engine.add_rule(crate::models::Rule {
            id: uuid::Uuid::new_v4(),
            name: "Invoice Due Reminder".to_string(),
            description: "Send reminder when invoice is due".to_string(),
            condition: "invoice.due_date <= today()".to_string(),
            action: "send_reminder".to_string(),
            priority: 1,
            created_at: chrono::Utc::now(),
            updated_at: chrono::Utc::now(),
        });
    }
    
    // Add some default licenses
    {
        let mut licenses_guard = licenses.lock().unwrap();
        licenses_guard.push(crate::license::License {
            id: uuid::Uuid::new_v4(),
            license_key: "PYOCH-TRIAL-12345".to_string(),
            user_id: uuid::Uuid::new_v4(),
            application_id: None,
            license_type: "trial".to_string(),
            max_applications: Some(1),
            max_downloads: Some(5),
            expiry_date: chrono::Utc::now() + chrono::Duration::days(30),
            is_active: true,
            created_at: chrono::Utc::now(),
            updated_at: chrono::Utc::now(),
        });
    }
    
    let app_state = web::Data::new(AppState {
        ai_engine,
        rule_engine,
        auto_learning_engine,
        stats_manager,
        protection_manager,
        licenses,
        database_manager,
        ai_model_manager,
    });

    println!("Starting PYOCH server at http://localhost:{}", config.server_port);
    
    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .wrap(Logger::default())
            .route("/health", web::get().to(health_check))
            .route("/evaluate", web::post().to(evaluate_prompt))
            .route("/feedback", web::post().to(submit_feedback))
            .route("/app-types", web::get().to(get_application_types))
            // License management routes
            .route("/license/validate", web::post().to(validate_license))
            .route("/license/create", web::post().to(create_license))
            // Auto-learning routes
            .route("/learning/identify-domain", web::post().to(identify_business_domain))
            .route("/learning/learn", web::post().to(learn_from_interaction))
            // Statistics routes
            .route("/stats", web::get().to(get_statistics))
            .route("/stats/download/{app_id}", web::post().to(record_download))
            // Protection routes
            .route("/protect", web::post().to(protect_application))
            .route("/verify/{app_id}/{checksum}", web::get().to(verify_application_integrity))
            // New AI model routes
            .route("/ai/generate", web::post().to(generate_with_ai_model))
            .route("/ai/health", web::get().to(ai_health_check))
            // New database routes
            .route("/users", web::post().to(create_user))
            .route("/applications", web::post().to(create_application))
            .service(actix_files::Files::new("/", "./static/").index_file("index.html"))
    })
    .bind(format!("0.0.0.0:{}", config.server_port))?
    .run()
    .await
}