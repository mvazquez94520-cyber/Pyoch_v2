use std::fs;
use std::path::Path;
use uuid::Uuid;
use chrono::{Utc, Duration};
use serde_json::json;
use std::process::Command;

use crate::models::{BusinessApplication, EvaluationResponse};
use crate::user_models::ApplicationDownload;

pub struct AppGenerator;

impl AppGenerator {
    pub async fn generate_windows_app(application: &BusinessApplication, user_id: Uuid) -> Result<ApplicationDownload, Box<dyn std::error::Error>> {
        // Create a unique filename for the application
        let app_filename = format!("app_{}_{}.exe", application.id, Utc::now().format("%Y%m%d_%H%M%S"));
        let app_path = format!("./downloads/{}", app_filename);
        
        // Create downloads directory if it doesn't exist
        if !Path::new("./downloads").exists() {
            fs::create_dir_all("./downloads")?;
        }

        // Generate the Windows executable
        // This is a simplified example - in a real implementation, you would have more complex logic
        // to generate the actual Windows application based on the business logic
        Self::create_stub_exe(&app_path, application)?;

        // Set expiration date to 30 days from now
        let expires_at = Utc::now()
            .checked_add_signed(Duration::days(30))
            .expect("Valid timestamp");

        let download = ApplicationDownload {
            id: Uuid::new_v4(),
            user_id,
            application_id: application.id,
            download_url: format!("/download/{}", app_filename),
            file_path: app_path.clone(),
            expires_at,
            created_at: Utc::now(),
        };

        Ok(download)
    }

    fn create_stub_exe(path: &str, application: &BusinessApplication) -> Result<(), std::io::Error> {
        // In a real implementation, this would generate an actual Windows executable
        // For this example, we'll create a simple text file as a placeholder
        // In a production system, you would integrate with a Windows application builder
        
        // Create a stub executable or use a template to build the actual application
        // For now, creating a placeholder file
        fs::write(path, format!("Windows Application: {}\nType: {}\nGenerated at: {}\n\nRules:\n", 
            application.name, 
            application.application_type,
            Utc::now().to_rfc3339()))?;
        
        // In a real implementation, you would:
        // 1. Use the application's rules and logic to generate actual source code
        // 2. Compile it into a Windows executable using a framework like Tauri, Electron, or native Windows tools
        // 3. Possibly use Rust with winapi or other Windows-specific libraries
        // 4. Or use a cross-platform framework to create the Windows app
        
        Ok(())
    }

    pub fn cleanup_expired_downloads() -> Result<(), Box<dyn std::error::Error>> {
        let downloads_path = Path::new("./downloads");
        if !downloads_path.exists() {
            return Ok(());
        }

        for entry in fs::read_dir(downloads_path)? {
            let entry = entry?;
            let path = entry.path();
            
            if path.extension().and_then(|s| s.to_str()) == Some("exe") {
                // In a real implementation, you would check the creation/modification time
                // and compare it with the expiration time stored in a database
                // For this example, we'll just remove files older than 30 days
                if let Ok(metadata) = path.metadata() {
                    if let Ok(modified) = metadata.modified() {
                        let duration_since_modified = std::time::SystemTime::now().duration_since(modified)?;
                        if duration_since_modified.as_secs() > 30 * 24 * 60 * 60 { // 30 days in seconds
                            fs::remove_file(&path)?;
                        }
                    }
                }
            }
        }

        Ok(())
    }
}