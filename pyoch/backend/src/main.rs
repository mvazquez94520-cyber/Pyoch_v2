mod models;
mod ai_engine;
mod rule_engine;
mod utils;

use actix_web::{web, App, HttpServer, HttpResponse, Responder, middleware::Logger};
use serde_json::json;
use crate::models::{PromptRequest, EvaluationResponse};
use crate::ai_engine::AIEngine;
use crate::rule_engine::RuleEngine;
use std::sync::{Arc, Mutex};
use env_logger;

struct AppState {
    ai_engine: AIEngine,
    rule_engine: Arc<Mutex<RuleEngine>>,
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

    match ai_engine.generate_business_logic(&req).await {
        Ok(mut response) => {
            // Update rule engine based on the prompt
            let rules = rule_engine.lock().unwrap().apply_rules(&req.prompt);
            
            // Generate backend and frontend previews
            let backend_preview = ai_engine.generate_backend_preview(&req.prompt).await;
            let frontend_preview = ai_engine.generate_frontend_preview(&req.prompt).await;
            
            response.rules_generated = rules;
            response.backend_preview = Some(backend_preview);
            response.frontend_preview = Some(frontend_preview);

            HttpResponse::Ok().json(response)
        }
        Err(e) => {
            HttpResponse::InternalServerError().json(EvaluationResponse {
                application: None,
                generated_code: None,
                rules_generated: vec![],
                backend_preview: None,
                frontend_preview: None,
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
    });

    println!("Starting PYOCH server at http://localhost:3030");
    
    HttpServer::new(move || {
        App::new()
            .app_data(app_state.clone())
            .wrap(Logger::default())
            .route("/health", web::get().to(health_check))
            .route("/evaluate", web::post().to(evaluate_prompt))
            .route("/feedback", web::post().to(submit_feedback))
            .route("/app-types", web::get().to(get_application_types))
            .service(actix_files::Files::new("/", "./static/").index_file("index.html"))
    })
    .bind("0.0.0.0:3030")?
    .run()
    .await
}