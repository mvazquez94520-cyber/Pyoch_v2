use serde::{Deserialize, Serialize};
use uuid::Uuid;
use chrono::Utc;
use anyhow::Result;
use xlsxwriter::*;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Company {
    pub id: Uuid,
    pub name: String,
    pub email: String,
    pub sector: String,
    pub employees: u32,
    pub location: String,
    pub technology: Option<String>,
    pub contact_status: ContactStatus,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum ContactStatus {
    NotContacted,
    Contacted,
    Responded,
    Interested,
    NotInterested,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SearchRequest {
    pub keywords: Vec<String>,
    pub sectors: Vec<String>,
    pub min_employees: Option<u32>,
    pub max_employees: Option<u32>,
    pub location: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SearchResult {
    pub companies: Vec<Company>,
    pub total_found: usize,
    pub search_time: chrono::Duration,
}

pub struct B2BProspectionEngine {
    // This would contain the logic for searching companies
    // using SERP API and other data sources
}

impl B2BProspectionEngine {
    pub fn new() -> Self {
        B2BProspectionEngine {}
    }

    pub async fn search_companies(&self, request: &SearchRequest) -> Result<SearchResult> {
        // In a real implementation, this would call the SERP API
        // and other data sources to find companies based on the criteria
        println!("Searching for companies with keywords: {:?}", request.keywords);
        
        // For demonstration, return some sample data
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

        Ok(SearchResult {
            companies,
            total_found: 3,
            search_time: chrono::Duration::seconds(2),
        })
    }

    pub fn export_to_excel(&self, companies: &[Company], filename: &str) -> Result<()> {
        // Create a new workbook
        let workbook = Workbook::new(filename);
        
        // Add a worksheet
        let worksheet = workbook.add_worksheet(None)?;
        
        // Write headers
        worksheet.write_string(0, 0, "Nom de l'entreprise", None)?;
        worksheet.write_string(0, 1, "Email", None)?;
        worksheet.write_string(0, 2, "Secteur", None)?;
        worksheet.write_string(0, 3, "Nombre d'employés", None)?;
        worksheet.write_string(0, 4, "Localisation", None)?;
        worksheet.write_string(0, 5, "Technologie", None)?;
        worksheet.write_string(0, 6, "Statut de contact", None)?;
        
        // Write data
        for (i, company) in companies.iter().enumerate() {
            let row = (i + 1) as u32;
            worksheet.write_string(row, 0, &company.name, None)?;
            worksheet.write_string(row, 1, &company.email, None)?;
            worksheet.write_string(row, 2, &company.sector, None)?;
            worksheet.write_number(row, 3, company.employees as f64, None)?;
            worksheet.write_string(row, 4, &company.location, None)?;
            if let Some(ref tech) = company.technology {
                worksheet.write_string(row, 5, tech, None)?;
            } else {
                worksheet.write_string(row, 5, "", None)?;
            }
            worksheet.write_string(row, 6, &format!("{:?}", company.contact_status), None)?;
        }
        
        // Close the workbook
        workbook.close()?;
        
        println!("Exported {} companies to Excel file: {}", companies.len(), filename);
        Ok(())
    }

    pub fn generate_email_template(&self, company: &Company) -> String {
        // Generate a personalized email based on the company's sector
        let subject = match company.sector.as_str() {
            "Intelligence Artificielle" | "AI/ML" => "Accélérez vos modèles ML avec nos workstations GPU",
            "Rendu 3D" => "Optimisez votre rendu 3D avec notre matériel professionnel",
            "Effets Visuels" => "Accélérez vos effets visuels avec nos solutions GPU",
            _ => "Solutions GPU pour votre secteur d'activité",
        };

        format!(
            "Sujet: {}\n\nBonjour,\n\nNous avons remarqué que {} travaille dans le domaine {} et utilise {}. \n\nNos workstations équipées de GPU haute performance pourraient considérablement améliorer votre productivité et réduire vos temps de calcul.\n\nSouhaitez-vous un essai gratuit ou une démonstration ?\n\nCordialement,\nL'équipe commerciale",
            subject,
            company.name,
            company.sector,
            company.technology.as_deref().unwrap_or("des technologies non spécifiées")
        )
    }
}