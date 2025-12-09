use actix_web::{web, HttpResponse, Result, HttpRequest};
use serde_json::json;
use sqlx::{PgPool, Row};
use uuid::Uuid;
use chrono::Utc;

use crate::user_models::*;
use crate::auth::AuthService;
use crate::paypal::PayPalService;
use crate::app_generator::AppGenerator;
use crate::models::BusinessApplication;

pub async fn register_user(
    pool: web::Data<PgPool>,
    user_data: web::Json<CreateUserRequest>,
) -> Result<HttpResponse> {
    // Hash the password
    let password_hash = AuthService::hash_password(&user_data.password);

    // Insert the new user into the database
    let query = r#"
        INSERT INTO users (id, email, username, password_hash, created_at, updated_at, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING id, email, username, created_at, updated_at
    "#;

    let user_id = Uuid::new_v4();
    let now = Utc::now();

    let row = sqlx::query(query)
        .bind(user_id)
        .bind(&user_data.email)
        .bind(&user_data.username)
        .bind(&password_hash)
        .bind(now)
        .bind(now)
        .bind(true)
        .fetch_one(pool.get_ref())
        .await;

    match row {
        Ok(row) => {
            let response = json!({
                "id": row.get::<Uuid, _>("id"),
                "email": row.get::<String, _>("email"),
                "username": row.get::<String, _>("username"),
                "created_at": row.get::<chrono::DateTime<Utc>, _>("created_at"),
            });
            Ok(HttpResponse::Created().json(response))
        }
        Err(e) => {
            eprintln!("Database error during registration: {:?}", e);
            Ok(HttpResponse::InternalServerError().json(json!({"error": "Registration failed"})))
        }
    }
}

pub async fn login_user(
    pool: web::Data<PgPool>,
    login_data: web::Json<LoginRequest>,
) -> Result<HttpResponse> {
    let query = r#"SELECT id, password_hash FROM users WHERE email = $1 AND is_active = true"#;

    let row = sqlx::query(query)
        .bind(&login_data.email)
        .fetch_optional(pool.get_ref())
        .await;

    match row {
        Ok(Some(row)) => {
            let user_id: Uuid = row.get("id");
            let stored_hash: String = row.get("password_hash");

            if AuthService::verify_password(&login_data.password, &stored_hash) {
                let token = AuthService::generate_token(user_id);
                
                Ok(HttpResponse::Ok().json(json!({
                    "token": token,
                    "user_id": user_id,
                    "message": "Login successful"
                })))
            } else {
                Ok(HttpResponse::Unauthorized().json(json!({"error": "Invalid credentials"})))
            }
        }
        Ok(None) => {
            Ok(HttpResponse::Unauthorized().json(json!({"error": "Invalid credentials"})))
        }
        Err(e) => {
            eprintln!("Database error during login: {:?}", e);
            Ok(HttpResponse::InternalServerError().json(json!({"error": "Login failed"})))
        }
    }
}

// Middleware-like function to extract user ID from token
pub fn extract_user_id(req: &HttpRequest) -> Option<Uuid> {
    let auth_header = req.headers().get("Authorization")?
        .to_str().ok()?;
    
    if !auth_header.starts_with("Bearer ") {
        return None;
    }
    
    let token = &auth_header[7..];
    AuthService::validate_token(token)
}

pub async fn create_payment(
    pool: web::Data<PgPool>,
    req: HttpRequest,
    payment_data: web::Json<CreatePaymentRequest>,
) -> Result<HttpResponse> {
    // Extract user ID from token
    let user_id = match extract_user_id(&req) {
        Some(id) => id,
        None => return Ok(HttpResponse::Unauthorized().json(json!({"error": "Authentication required"}))),
    };

    // Verify that the user owns the application
    let query = r#"SELECT user_id FROM applications WHERE id = $1"#;
    let row = sqlx::query(query)
        .bind(payment_data.application_id)
        .fetch_optional(pool.get_ref())
        .await;

    match row {
        Ok(Some(row)) => {
            let app_user_id: Uuid = row.get("user_id");
            if app_user_id != user_id {
                return Ok(HttpResponse::Forbidden().json(json!({"error": "Access denied"})));
            }
        }
        Ok(None) => {
            return Ok(HttpResponse::NotFound().json(json!({"error": "Application not found"})));
        }
        Err(e) => {
            eprintln!("Database error checking application ownership: {:?}", e);
            return Ok(HttpResponse::InternalServerError().json(json!({"error": "Internal error"})));
        }
    }

    // Create payment record in database with pending status
    let payment_id = Uuid::new_v4();
    let now = Utc::now();
    let query = r#"
        INSERT INTO payments (id, user_id, amount, currency, payment_method, status, created_at, updated_at, application_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    "#;

    if let Err(e) = sqlx::query(query)
        .bind(payment_id)
        .bind(user_id)
        .bind(payment_data.amount)
        .bind("USD")  // Default currency, could be configurable
        .bind("paypal")
        .bind(PaymentStatus::Pending)
        .bind(now)
        .bind(now)
        .bind(payment_data.application_id)
        .execute(pool.get_ref())
        .await
    {
        eprintln!("Database error creating payment: {:?}", e);
        return Ok(HttpResponse::InternalServerError().json(json!({"error": "Payment creation failed"})));
    }

    // Create PayPal payment
    match PayPalService::create_payment(payment_data.amount, "USD").await {
        Ok(paypal_response) => {
            // Update payment record with PayPal ID
            let update_query = r#"UPDATE payments SET paypal_payment_id = $1 WHERE id = $2"#;
            if let Err(e) = sqlx::query(update_query)
                .bind(&paypal_response.approval_url) // Actually storing the approval URL temporarily
                .bind(payment_id)
                .execute(pool.get_ref())
                .await
            {
                eprintln!("Database error updating payment: {:?}", e);
            }

            Ok(HttpResponse::Ok().json(paypal_response))
        }
        Err(e) => {
            eprintln!("PayPal error: {:?}", e);
            Ok(HttpResponse::InternalServerError().json(json!({"error": "Payment processing error"})))
        }
    }
}

pub async fn get_user_profile(
    pool: web::Data<PgPool>,
    req: HttpRequest,
) -> Result<HttpResponse> {
    let user_id = match extract_user_id(&req) {
        Some(id) => id,
        None => return Ok(HttpResponse::Unauthorized().json(json!({"error": "Authentication required"}))),
    };

    let query = r#"SELECT id, email, username, created_at FROM users WHERE id = $1 AND is_active = true"#;
    let row = sqlx::query(query)
        .bind(user_id)
        .fetch_optional(pool.get_ref())
        .await;

    match row {
        Ok(Some(row)) => {
            let response = json!({
                "id": row.get::<Uuid, _>("id"),
                "email": row.get::<String, _>("email"),
                "username": row.get::<String, _>("username"),
                "created_at": row.get::<chrono::DateTime<Utc>, _>("created_at"),
            });
            Ok(HttpResponse::Ok().json(response))
        }
        Ok(None) => {
            Ok(HttpResponse::NotFound().json(json!({"error": "User not found"})))
        }
        Err(e) => {
            eprintln!("Database error fetching user profile: {:?}", e);
            Ok(HttpResponse::InternalServerError().json(json!({"error": "Failed to fetch profile"})))
        }
    }
}

pub async fn get_user_payments(
    pool: web::Data<PgPool>,
    req: HttpRequest,
) -> Result<HttpResponse> {
    let user_id = match extract_user_id(&req) {
        Some(id) => id,
        None => return Ok(HttpResponse::Unauthorized().json(json!({"error": "Authentication required"}))),
    };

    let query = r#"SELECT id, amount, currency, status, created_at FROM payments WHERE user_id = $1 ORDER BY created_at DESC"#;
    let rows = sqlx::query(query)
        .bind(user_id)
        .fetch_all(pool.get_ref())
        .await;

    match rows {
        Ok(rows) => {
            let payments: Vec<_> = rows.iter().map(|row| {
                json!({
                    "id": row.get::<Uuid, _>("id"),
                    "amount": row.get::<f64, _>("amount"),
                    "currency": row.get::<String, _>("currency"),
                    "status": row.get::<PaymentStatus, _>("status"),
                    "created_at": row.get::<chrono::DateTime<Utc>, _>("created_at"),
                })
            }).collect();

            Ok(HttpResponse::Ok().json(payments))
        }
        Err(e) => {
            eprintln!("Database error fetching user payments: {:?}", e);
            Ok(HttpResponse::InternalServerError().json(json!({"error": "Failed to fetch payments"})))
        }
    }
}

pub async fn get_user_applications(
    pool: web::Data<PgPool>,
    req: HttpRequest,
) -> Result<HttpResponse> {
    let user_id = match extract_user_id(&req) {
        Some(id) => id,
        None => return Ok(HttpResponse::Unauthorized().json(json!({"error": "Authentication required"}))),
    };

    let query = r#"SELECT id, name, application_type, created_at FROM applications WHERE user_id = $1 ORDER BY created_at DESC"#;
    let rows = sqlx::query(query)
        .bind(user_id)
        .fetch_all(pool.get_ref())
        .await;

    match rows {
        Ok(rows) => {
            let applications: Vec<_> = rows.iter().map(|row| {
                json!({
                    "id": row.get::<Uuid, _>("id"),
                    "name": row.get::<String, _>("name"),
                    "application_type": row.get::<String, _>("application_type"),
                    "created_at": row.get::<chrono::DateTime<Utc>, _>("created_at"),
                })
            }).collect();

            Ok(HttpResponse::Ok().json(applications))
        }
        Err(e) => {
            eprintln!("Database error fetching user applications: {:?}", e);
            Ok(HttpResponse::InternalServerError().json(json!({"error": "Failed to fetch applications"})))
        }
    }
}

pub async fn execute_payment(
    pool: web::Data<PgPool>,
    req: HttpRequest,
    payment_data: web::Json<ExecutePaymentRequest>,
) -> Result<HttpResponse> {
    let user_id = match extract_user_id(&req) {
        Some(id) => id,
        None => return Ok(HttpResponse::Unauthorized().json(json!({"error": "Authentication required"}))),
    };

    // First, verify that the payment belongs to the user
    let query = r#"SELECT id, application_id FROM payments WHERE paypal_payment_id = $1 AND user_id = $2"#;
    let row = sqlx::query(query)
        .bind(&payment_data.payment_id)
        .bind(user_id)
        .fetch_optional(pool.get_ref())
        .await;

    match row {
        Ok(Some(row)) => {
            let payment_db_id: Uuid = row.get("id");
            let application_id: Uuid = row.get("application_id");

            // Execute payment with PayPal
            match PayPalService::execute_payment(&payment_data.payment_id).await {
                Ok(success) => {
                    if success {
                        // Update payment status to completed
                        let update_query = r#"
                            UPDATE payments 
                            SET status = $1, paypal_payer_id = $2, updated_at = $3 
                            WHERE id = $4
                        "#;
                        
                        if let Err(e) = sqlx::query(update_query)
                            .bind(PaymentStatus::Completed)
                            .bind(&payment_data.payer_id)
                            .bind(Utc::now())
                            .bind(payment_db_id)
                            .execute(pool.get_ref())
                            .await
                        {
                            eprintln!("Database error updating payment status: {:?}", e);
                            return Ok(HttpResponse::InternalServerError().json(json!({"error": "Failed to update payment status"})));
                        }

                        // Retrieve the application details to generate the Windows app
                        let app_query = r#"SELECT * FROM applications WHERE id = $1"#;
                        let app_row = sqlx::query(app_query)
                            .bind(application_id)
                            .fetch_optional(pool.get_ref())
                            .await;

                        if let Ok(Some(app_row)) = app_row {
                            // In a real implementation, you would reconstruct the BusinessApplication from DB data
                            // For now, we'll create a placeholder
                            let application = BusinessApplication {
                                id: application_id,
                                name: app_row.get::<String, _>("name"),
                                application_type: app_row.get::<String, _>("application_type"),
                                rules: vec![], // Would need to fetch from separate table
                                feedbacks: vec![], // Would need to fetch from separate table
                                created_at: app_row.get::<chrono::DateTime<Utc>, _>("created_at"),
                                updated_at: app_row.get::<chrono::DateTime<Utc>, _>("updated_at"),
                            };

                            // Generate the Windows application
                            match AppGenerator::generate_windows_app(&application, user_id).await {
                                Ok(download_info) => {
                                    // Save download information to database
                                    let download_query = r#"
                                        INSERT INTO application_downloads (id, user_id, application_id, download_url, file_path, expires_at, created_at)
                                        VALUES ($1, $2, $3, $4, $5, $6, $7)
                                    "#;

                                    if let Err(e) = sqlx::query(download_query)
                                        .bind(download_info.id)
                                        .bind(user_id)
                                        .bind(application_id)
                                        .bind(&download_info.download_url)
                                        .bind(&download_info.file_path)
                                        .bind(download_info.expires_at)
                                        .bind(download_info.created_at)
                                        .execute(pool.get_ref())
                                        .await
                                    {
                                        eprintln!("Database error saving download info: {:?}", e);
                                    }

                                    Ok(HttpResponse::Ok().json(json!({
                                        "status": "completed",
                                        "download_url": download_info.download_url,
                                        "message": "Payment successful and application generated!"
                                    })))
                                }
                                Err(e) => {
                                    eprintln!("Error generating application: {:?}", e);
                                    Ok(HttpResponse::InternalServerError().json(json!({"error": "Failed to generate application"})))
                                }
                            }
                        } else {
                            eprintln!("Application not found for payment");
                            Ok(HttpResponse::InternalServerError().json(json!({"error": "Application generation failed"})))
                        }
                    } else {
                        // Update payment status to failed
                        let update_query = r#"UPDATE payments SET status = $1, updated_at = $2 WHERE id = $3"#;
                        if let Err(e) = sqlx::query(update_query)
                            .bind(PaymentStatus::Failed)
                            .bind(Utc::now())
                            .bind(payment_db_id)
                            .execute(pool.get_ref())
                            .await
                        {
                            eprintln!("Database error updating failed payment status: {:?}", e);
                        }

                        Ok(HttpResponse::BadRequest().json(json!({"error": "Payment execution failed"})))
                    }
                }
                Err(e) => {
                    eprintln!("PayPal execution error: {:?}", e);
                    Ok(HttpResponse::InternalServerError().json(json!({"error": "Payment execution error"})))
                }
            }
        }
        Ok(None) => {
            Ok(HttpResponse::NotFound().json(json!({"error": "Payment not found"})))
        }
        Err(e) => {
            eprintln!("Database error verifying payment: {:?}", e);
            Ok(HttpResponse::InternalServerError().json(json!({"error": "Payment verification failed"})))
        }
    }
}