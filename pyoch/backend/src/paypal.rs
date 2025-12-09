use actix_web::{web, HttpResponse, Result};
use serde::{Deserialize, Serialize};
use serde_json::json;
use reqwest;
use std::env;
use base64;

use crate::user_models::{CreatePaymentRequest, CreatePaymentResponse, ExecutePaymentRequest};

#[derive(Debug, Serialize, Deserialize)]
struct PayPalCreateOrderRequest {
    intent: String,
    purchase_units: Vec<PurchaseUnit>,
}

#[derive(Debug, Serialize, Deserialize)]
struct PurchaseUnit {
    amount: Amount,
}

#[derive(Debug, Serialize, Deserialize)]
struct Amount {
    currency_code: String,
    value: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct PayPalCreateOrderResponse {
    id: String,
    status: String,
    links: Vec<Link>,
}

#[derive(Debug, Serialize, Deserialize)]
struct Link {
    href: String,
    rel: String,
    method: String,
}

pub struct PayPalService;

impl PayPalService {
    pub async fn create_payment(amount: f64, currency: &str) -> Result<CreatePaymentResponse, Box<dyn std::error::Error>> {
        let client = reqwest::Client::new();
        
        // Get PayPal credentials from environment
        let client_id = env::var("PAYPAL_CLIENT_ID").unwrap_or_else(|_| "your_paypal_client_id".to_string());
        let client_secret = env::var("PAYPAL_CLIENT_SECRET").unwrap_or_else(|_| "your_paypal_client_secret".to_string());
        let paypal_url = if cfg!(debug_assertions) {
            "https://api.sandbox.paypal.com"
        } else {
            "https://api.paypal.com"
        };

        // Get access token
        let auth_token = base64::encode(format!("{}:{}", client_id, client_secret));
        let token_response = client
            .post(&format!("{}/v1/oauth2/token", paypal_url))
            .header("Authorization", format!("Basic {}", auth_token))
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body("grant_type=client_credentials")
            .send()
            .await?;

        let token_data: serde_json::Value = token_response.json().await?;
        let access_token = token_data["access_token"].as_str().unwrap_or_default();

        // Create payment order
        let order_request = PayPalCreateOrderRequest {
            intent: "CAPTURE".to_string(),
            purchase_units: vec![PurchaseUnit {
                amount: Amount {
                    currency_code: currency.to_string(),
                    value: format!("{:.2}", amount),
                },
            }],
        };

        let order_response = client
            .post(&format!("{}/v2/checkout/orders", paypal_url))
            .header("Authorization", format!("Bearer {}", access_token))
            .header("Content-Type", "application/json")
            .json(&order_request)
            .send()
            .await?;

        let order_data: PayPalCreateOrderResponse = order_response.json().await?;

        // Find the approval URL
        let approval_url = order_data.links
            .iter()
            .find(|link| link.rel == "approve")
            .map(|link| link.href.clone())
            .unwrap_or_default();

        Ok(CreatePaymentResponse {
            payment_id: uuid::Uuid::parse_str(&order_data.id).unwrap_or_else(|_| uuid::Uuid::new_v4()),
            approval_url,
            status: order_data.status,
        })
    }

    pub async fn execute_payment(payment_id: &str) -> Result<bool, Box<dyn std::error::Error>> {
        let client = reqwest::Client::new();
        
        let client_id = env::var("PAYPAL_CLIENT_ID").unwrap_or_else(|_| "your_paypal_client_id".to_string());
        let client_secret = env::var("PAYPAL_CLIENT_SECRET").unwrap_or_else(|_| "your_paypal_client_secret".to_string());
        let paypal_url = if cfg!(debug_assertions) {
            "https://api.sandbox.paypal.com"
        } else {
            "https://api.paypal.com"
        };

        // Get access token
        let auth_token = base64::encode(format!("{}:{}", client_id, client_secret));
        let token_response = client
            .post(&format!("{}/v1/oauth2/token", paypal_url))
            .header("Authorization", format!("Basic {}", auth_token))
            .header("Content-Type", "application/x-www-form-urlencoded")
            .body("grant_type=client_credentials")
            .send()
            .await?;

        let token_data: serde_json::Value = token_response.json().await?;
        let access_token = token_data["access_token"].as_str().unwrap_or_default();

        // Capture the order
        let capture_response = client
            .post(&format!("{}/v2/checkout/orders/{}/capture", paypal_url, payment_id))
            .header("Authorization", format!("Bearer {}", access_token))
            .header("Content-Type", "application/json")
            .send()
            .await?;

        let capture_status = capture_response.status();
        Ok(capture_status.is_success())
    }
}