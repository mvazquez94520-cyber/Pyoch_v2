use actix_web::{web, HttpResponse, Result};
use serde::{Deserialize, Serialize};
use serde_json::json;
use bcrypt::{hash, verify, DEFAULT_COST};
use jsonwebtoken::{encode, decode, Header, Validation, EncodingKey, DecodingKey};
use chrono::{Utc, Duration};
use uuid::Uuid;
use std::env;

use crate::user_models::{User, CreateUserRequest, LoginRequest};

#[derive(Debug, Serialize, Deserialize)]
struct Claims {
    sub: String,
    exp: i64,
    iat: i64,
}

pub struct AuthService;

impl AuthService {
    pub fn hash_password(password: &str) -> String {
        hash(password, DEFAULT_COST).expect("Failed to hash password")
    }

    pub fn verify_password(password: &str, hash: &str) -> bool {
        verify(password, hash).unwrap_or(false)
    }

    pub fn generate_token(user_id: Uuid) -> String {
        let expiration = Utc::now()
            .checked_add_signed(Duration::days(7))
            .expect("Valid timestamp")
            .timestamp();

        let claims = Claims {
            sub: user_id.to_string(),
            exp: expiration,
            iat: Utc::now().timestamp(),
        };

        let secret = env::var("JWT_SECRET").unwrap_or_else(|_| "default_secret_key".to_string());
        encode(&Header::default(), &claims, &EncodingKey::from_secret(secret.as_ref()))
            .expect("Failed to encode token")
    }

    pub fn validate_token(token: &str) -> Option<Uuid> {
        let secret = env::var("JWT_SECRET").unwrap_or_else(|_| "default_secret_key".to_string());
        
        match decode::<Claims>(
            token,
            &DecodingKey::from_secret(secret.as_ref()),
            &Validation::default(),
        ) {
            Ok(token_data) => Uuid::parse_str(&token_data.claims.sub).ok(),
            Err(_) => None,
        }
    }
}