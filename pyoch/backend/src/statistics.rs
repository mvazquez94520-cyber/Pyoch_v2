use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct DownloadStats {
    pub id: Uuid,
    pub application_id: Uuid,
    pub user_id: Option<Uuid>,
    pub download_count: i32,
    pub last_downloaded: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct PromptKeywordStats {
    pub id: Uuid,
    pub keyword: String,
    pub usage_count: i32,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct StatsRequest {
    pub application_id: Option<Uuid>,
    pub user_id: Option<Uuid>,
    pub date_from: Option<DateTime<Utc>>,
    pub date_to: Option<DateTime<Utc>>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct StatsResponse {
    pub total_downloads: i32,
    pub top_keywords: Vec<(String, i32)>,
    pub application_stats: Vec<DownloadStats>,
    pub created_at: DateTime<Utc>,
}