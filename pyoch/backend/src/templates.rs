pub mod prospection_b2b;

use actix_web::{web, HttpResponse, Responder};
use serde::{Deserialize, Serialize};
use crate::templates::prospection_b2b::{B2BProspectionEngine, SearchRequest};

#[derive(Debug, Serialize, Deserialize)]
struct SearchCompaniesRequest {
    keywords: Vec<String>,
}

pub async fn search_companies_handler(
    search_request: web::Json<SearchCompaniesRequest>,
) -> impl Responder {
    let engine = B2BProspectionEngine::new();
    
    let request = SearchRequest {
        keywords: search_request.keywords.clone(),
        sectors: vec![], // Default empty, could be extended with user input
        min_employees: None,
        max_employees: None,
        location: None,
    };
    
    match engine.search_companies(&request).await {
        Ok(result) => {
            let companies: Vec<serde_json::Value> = result.companies
                .iter()
                .map(|company| {
                    serde_json::json!({
                        "id": company.id,
                        "name": company.name,
                        "email": company.email,
                        "sector": company.sector,
                        "employees": company.employees,
                        "location": company.location,
                        "technology": company.technology,
                        "contact_status": format!("{:?}", company.contact_status)
                    })
                })
                .collect();
                
            HttpResponse::Ok().json(serde_json::json!({
                "companies": companies,
                "total_found": result.total_found,
                "search_time": result.search_time.num_seconds()
            }))
        }
        Err(e) => {
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": e.to_string()
            }))
        }
    }
}

pub async fn export_companies_handler() -> impl Responder {
    // For this example, we'll create a sample list of companies and export them
    // In a real implementation, this would receive the companies to export from a request
    // or from a database query
    use crate::templates::prospection_b2b::{B2BProspectionEngine, Company, ContactStatus};
    use uuid::Uuid;
    use chrono::Utc;

    let engine = B2BProspectionEngine::new();
    
    // Create sample companies
    let companies = vec![
        Company {
            id: Uuid::new_v4(),
            name: "TechAI Solutions".to_string(),
            email: "contact@techai-solutions.fr".to_string(),
            sector: "Intelligence Artificielle".to_string(),
            employees: 50,
            location: "Paris".to_string(),
            technology: Some("TensorFlow, PyTorch".to_string()),
            contact_status: ContactStatus::NotContacted,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        },
        Company {
            id: Uuid::new_v4(),
            name: "Render3D Studio".to_string(),
            email: "info@render3d-studio.fr".to_string(),
            sector: "Rendu 3D".to_string(),
            employees: 25,
            location: "Lyon".to_string(),
            technology: Some("Blender, Unreal Engine".to_string()),
            contact_status: ContactStatus::NotContacted,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        },
        Company {
            id: Uuid::new_v4(),
            name: "VFX Pro".to_string(),
            email: "hello@vfxpro.fr".to_string(),
            sector: "Effets Visuels".to_string(),
            employees: 30,
            location: "Bordeaux".to_string(),
            technology: Some("Maya, Nuke".to_string()),
            contact_status: ContactStatus::NotContacted,
            created_at: Utc::now(),
            updated_at: Utc::now(),
        },
    ];

    let filename = "prospects.xlsx";
    match engine.export_to_excel(&companies, filename) {
        Ok(_) => {
            HttpResponse::Ok().json(serde_json::json!({
                "status": "export completed",
                "filename": filename,
                "companies_exported": companies.len()
            }))
        }
        Err(e) => {
            HttpResponse::InternalServerError().json(serde_json::json!({
                "error": e.to_string(),
                "status": "export failed"
            }))
        }
    }
}

// Add the new routes to the application
pub fn configure_routes(cfg: &mut web::ServiceConfig) {
    cfg
        .route("/prospection/search", web::post().to(search_companies_handler))
        .route("/prospection/export", web::get().to(export_companies_handler));
}