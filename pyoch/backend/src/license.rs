use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct License {
    pub id: Uuid,
    pub license_key: String,
    pub user_id: Uuid,
    pub application_id: Option<Uuid>,
    pub license_type: String, // trial, basic, pro, enterprise
    pub max_applications: Option<i32>,
    pub max_downloads: Option<i32>,
    pub expiry_date: DateTime<Utc>,
    pub is_active: bool,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct LicenseCheckRequest {
    pub license_key: String,
    pub application_id: Option<Uuid>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct LicenseCheckResponse {
    pub is_valid: bool,
    pub license_info: Option<License>,
    pub error: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ApplicationProtection {
    pub id: Uuid,
    pub application_id: Uuid,
    pub protection_level: String, // basic, advanced, enterprise
    pub encrypted_core: Vec<u8>,
    pub checksum: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ProtectedApplication {
    pub id: Uuid,
    pub name: String,
    pub application_type: String,
    pub protected_core: Option<ApplicationProtection>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}