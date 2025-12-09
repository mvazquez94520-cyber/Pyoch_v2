use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Rule {
    pub id: Uuid,
    pub name: String,
    pub description: String,
    pub condition: String,
    pub action: String,
    pub priority: i32,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Feedback {
    pub id: Uuid,
    pub rule_id: Uuid,
    pub is_relevant: bool,
    pub user_comment: Option<String>,
    pub timestamp: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct BusinessApplication {
    pub id: Uuid,
    pub name: String,
    pub application_type: String, // CRM, billing, project management, etc.
    pub rules: Vec<Rule>,
    pub feedbacks: Vec<Feedback>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct PromptRequest {
    pub prompt: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct EvaluationResponse {
    pub application: Option<BusinessApplication>,
    pub generated_code: Option<String>,
    pub rules_generated: Vec<Rule>,
    pub error: Option<String>,
}