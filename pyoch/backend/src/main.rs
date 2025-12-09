mod models;
mod ai_engine;
mod rule_engine;
mod utils;
mod user_models;
mod auth;
mod paypal;
mod app_generator;
mod user_handlers;

use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware::Logger};
use serde_json::json;
use crate::models::{PromptRequest, EvaluationResponse};
use crate::ai_engine::AIEngine;
use crate::rule_engine::RuleEngine;
use crate::user_handlers::{
    register_user, login_user, 
    get_user_profile, get_user_payments, 
    get_user_applications, create_payment, 
    execute_payment
};
use std::sync::{Arc, Mutex};
use env_logger;
use sqlx::PgPool;

struct AppState {
    ai_engine: AIEngine,
    rule_engine: Arc<Mutex<RuleEngine>>,
    db_pool: PgPool,
}

async fn health_check() -> impl Responder {
    HttpResponse::Ok().json(json!({"status": "healthy"}))
}

async fn register_user_handler(
    pool: web::Data<PgPool>,
    user_data: web::Json<crate::user_models::CreateUserRequest>,
) -> impl Responder {
    register_user(pool, user_data).await
}

async fn login_user_handler(
    pool: web::Data<PgPool>,
    login_data: web::Json<crate::user_models::LoginRequest>,
) -> impl Responder {
    login_user(pool, login_data).await
}

async fn get_profile_handler(
    pool: web::Data<PgPool>,
    req: actix_web::HttpRequest,
) -> impl Responder {
    get_user_profile(pool, req).await
}

async fn get_payments_handler(
    pool: web::Data<PgPool>,
    req: actix_web::HttpRequest,
) -> impl Responder {
    get_user_payments(pool, req).await
}

async fn get_applications_handler(
    pool: web::Data<PgPool>,
    req: actix_web::HttpRequest,
) -> impl Responder {
    get_user_applications(pool, req).await
}

async fn create_payment_handler(
    pool: web::Data<PgPool>,
    req: actix_web::HttpRequest,
    payment_data: web::Json<crate::user_models::CreatePaymentRequest>,
) -> impl Responder {
    create_payment(pool, req, payment_data).await
}

async fn execute_payment_handler(
    pool: web::Data<PgPool>,
    req: actix_web::HttpRequest,
    payment_data: web::Json<crate::user_models::ExecutePaymentRequest>,
) -> impl Responder {
    execute_payment(pool, req, payment_data).await
}

async fn evaluate_prompt(
    data: web::Data<AppState>,
    req: web::Json<PromptRequest>,
) -> impl Responder {
    let ai_engine = &data.ai_engine;
    let rule_engine = &data.rule_engine;

    match ai_engine.generate_business_logic(&req).await {
        Ok(response) => {
            // Update rule engine based on the prompt
            let rules = rule_engine.lock().unwrap().apply_rules(&req.prompt);
            
            HttpResponse::Ok().json(EvaluationResponse {
                rules_generated: rules,
                ..response
            })
        }
        Err(e) => {
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
    
    // Add feedback to the engine
    {
        let mut engine = rule_engine.lock().unwrap();
        engine.add_feedback(feedback.into_inner());
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

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    env_logger::init();
    
    // Load environment variables
    dotenv::dotenv().ok();
    
    // Create database connection pool
    let database_url = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "postgresql://user:password@localhost/pyoch".to_string());
    let db_pool = PgPool::connect(&database_url)
        .await
        .expect("Failed to connect to database");
    
    let ai_engine = AIEngine::new();
    let rule_engine = Arc::new(Mutex::new(RuleEngine::new()));
    
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
    
    let app_state = web::Data::new(AppState {
        ai_engine,
        rule_engine,
        db_pool: db_pool.clone(),
    });

    println!("Starting PYOCH server at http://localhost:3030");
    
    HttpServer::new(move || {
        App::new()
            .app_data(web::Data::new(db_pool.clone()))
            .app_data(app_state.clone())
            .wrap(Logger::default())
            .route("/health", web::get().to(health_check))
            .route("/evaluate", web::post().to(evaluate_prompt))
            .route("/feedback", web::post().to(submit_feedback))
            .route("/app-types", web::get().to(get_application_types))
            // User authentication routes
            .route("/register", web::post().to(register_user_handler))
            .route("/login", web::post().to(login_user_handler))
            // User profile routes (protected)
            .route("/profile", web::get().to(get_profile_handler))
            .route("/payments", web::get().to(get_payments_handler))
            .route("/applications", web::get().to(get_applications_handler))
            // Payment routes
            .route("/create-payment", web::post().to(create_payment_handler))
            .route("/execute-payment", web::post().to(execute_payment_handler))
            // File download route
            .service(actix_files::Files::new("/download", "./downloads/").use_last_modified(true))
            // Static files
            .service(actix_files::Files::new("/", "./static/").index_file("index.html"))
    })
    .bind("0.0.0.0:3030")?
    .run()
    .await
}