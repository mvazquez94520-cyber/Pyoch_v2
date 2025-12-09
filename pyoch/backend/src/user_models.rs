use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct User {
    pub id: Uuid,
    pub email: String,
    pub username: String,
    pub password_hash: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub is_active: bool,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct Payment {
    pub id: Uuid,
    pub user_id: Uuid,
    pub amount: f64,
    pub currency: String,
    pub payment_method: String, // "paypal"
    pub status: PaymentStatus,
    pub paypal_payment_id: Option<String>,
    pub paypal_payer_id: Option<String>,
    pub application_id: Option<Uuid>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum PaymentStatus {
    Pending,
    Completed,
    Failed,
    Refunded,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ApplicationDownload {
    pub id: Uuid,
    pub user_id: Uuid,
    pub application_id: Uuid,
    pub download_url: String,
    pub file_path: String,
    pub expires_at: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreateUserRequest {
    pub email: String,
    pub username: String,
    pub password: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct LoginRequest {
    pub email: String,
    pub password: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreatePaymentRequest {
    pub user_id: Uuid,
    pub application_id: Uuid,
    pub amount: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CreatePaymentResponse {
    pub payment_id: Uuid,
    pub approval_url: String,
    pub status: String,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ExecutePaymentRequest {
    pub payment_id: String,
    pub payer_id: String,
}