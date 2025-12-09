use sqlx::{PgPool, Row};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DatabaseConfig {
    pub url: String,
    pub max_connections: u32,
}

pub struct DatabaseManager {
    pub pool: PgPool,
}

impl DatabaseManager {
    pub async fn new(config: &DatabaseConfig) -> Result<Self, sqlx::Error> {
        let pool = PgPool::connect_with(
            sqlx::postgres::PgPoolOptions::new()
                .max_connections(config.max_connections)
                .connect(&config.url)
                .await?
        ).await?;

        Ok(DatabaseManager { pool })
    }

    pub async fn init_tables(&self) -> Result<(), sqlx::Error> {
        // Create users table
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )"
        ).execute(&self.pool).await?;

        // Create applications table
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS applications (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                owner_id INTEGER REFERENCES users(id),
                created_at TIMESTAMP DEFAULT NOW()
            )"
        ).execute(&self.pool).await?;

        // Create prompts table
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS prompts (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                application_id INTEGER REFERENCES applications(id),
                prompt_text TEXT NOT NULL,
                response_text TEXT,
                business_domain VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW()
            )"
        ).execute(&self.pool).await?;

        // Create licenses table
        sqlx::query(
            "CREATE TABLE IF NOT EXISTS licenses (
                id SERIAL PRIMARY KEY,
                license_key VARCHAR(255) UNIQUE NOT NULL,
                user_id INTEGER REFERENCES users(id),
                license_type VARCHAR(50) NOT NULL,
                expires_at TIMESTAMP,
                max_downloads INTEGER DEFAULT -1, -- -1 means unlimited
                current_downloads INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW()
            )"
        ).execute(&self.pool).await?;

        Ok(())
    }

    pub async fn get_user_by_email(&self, email: &str) -> Result<Option<User>, sqlx::Error> {
        let row = sqlx::query("SELECT id, username, email, created_at FROM users WHERE email = $1")
            .bind(email)
            .fetch_optional(&self.pool)
            .await?;

        if let Some(row) = row {
            Ok(Some(User {
                id: row.get("id"),
                username: row.get("username"),
                email: row.get("email"),
                created_at: row.get("created_at"),
            }))
        } else {
            Ok(None)
        }
    }

    pub async fn create_user(&self, username: &str, email: &str) -> Result<User, sqlx::Error> {
        let row = sqlx::query(
            "INSERT INTO users (username, email) VALUES ($1, $2) RETURNING id, username, email, created_at"
        )
        .bind(username)
        .bind(email)
        .fetch_one(&self.pool)
        .await?;

        Ok(User {
            id: row.get("id"),
            username: row.get("username"),
            email: row.get("email"),
            created_at: row.get("created_at"),
        })
    }

    pub async fn create_application(&self, name: &str, description: &str, owner_id: i32) -> Result<Application, sqlx::Error> {
        let row = sqlx::query(
            "INSERT INTO applications (name, description, owner_id) VALUES ($1, $2, $3) RETURNING id, name, description, owner_id, created_at"
        )
        .bind(name)
        .bind(description)
        .bind(owner_id)
        .fetch_one(&self.pool)
        .await?;

        Ok(Application {
            id: row.get("id"),
            name: row.get("name"),
            description: row.get("description"),
            owner_id: row.get("owner_id"),
            created_at: row.get("created_at"),
        })
    }

    pub async fn record_prompt(&self, user_id: i32, application_id: i32, prompt_text: &str, response_text: Option<&str>, business_domain: Option<&str>) -> Result<Prompt, sqlx::Error> {
        let row = sqlx::query(
            "INSERT INTO prompts (user_id, application_id, prompt_text, response_text, business_domain) VALUES ($1, $2, $3, $4, $5) RETURNING id, user_id, application_id, prompt_text, response_text, business_domain, created_at"
        )
        .bind(user_id)
        .bind(application_id)
        .bind(prompt_text)
        .bind(response_text)
        .bind(business_domain)
        .fetch_one(&self.pool)
        .await?;

        Ok(Prompt {
            id: row.get("id"),
            user_id: row.get("user_id"),
            application_id: row.get("application_id"),
            prompt_text: row.get("prompt_text"),
            response_text: row.get("response_text"),
            business_domain: row.get("business_domain"),
            created_at: row.get("created_at"),
        })
    }

    pub async fn get_license_by_key(&self, license_key: &str) -> Result<Option<License>, sqlx::Error> {
        let row = sqlx::query("SELECT id, license_key, user_id, license_type, expires_at, max_downloads, current_downloads, created_at FROM licenses WHERE license_key = $1")
            .bind(license_key)
            .fetch_optional(&self.pool)
            .await?;

        if let Some(row) = row {
            Ok(Some(License {
                id: row.get("id"),
                license_key: row.get("license_key"),
                user_id: row.get("user_id"),
                license_type: row.get("license_type"),
                expires_at: row.get("expires_at"),
                max_downloads: row.get("max_downloads"),
                current_downloads: row.get("current_downloads"),
                created_at: row.get("created_at"),
            }))
        } else {
            Ok(None)
        }
    }

    pub async fn create_license(&self, license_key: &str, user_id: i32, license_type: &str, expires_at: Option<chrono::DateTime<chrono::Utc>>) -> Result<License, sqlx::Error> {
        let row = sqlx::query(
            "INSERT INTO licenses (license_key, user_id, license_type, expires_at) VALUES ($1, $2, $3, $4) RETURNING id, license_key, user_id, license_type, expires_at, max_downloads, current_downloads, created_at"
        )
        .bind(license_key)
        .bind(user_id)
        .bind(license_type)
        .bind(expires_at)
        .fetch_one(&self.pool)
        .await?;

        Ok(License {
            id: row.get("id"),
            license_key: row.get("license_key"),
            user_id: row.get("user_id"),
            license_type: row.get("license_type"),
            expires_at: row.get("expires_at"),
            max_downloads: row.get("max_downloads"),
            current_downloads: row.get("current_downloads"),
            created_at: row.get("created_at"),
        })
    }

    pub async fn increment_license_download(&self, license_id: i32) -> Result<(), sqlx::Error> {
        sqlx::query("UPDATE licenses SET current_downloads = current_downloads + 1 WHERE id = $1")
            .bind(license_id)
            .execute(&self.pool)
            .await?;
        
        Ok(())
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: i32,
    pub username: String,
    pub email: String,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Application {
    pub id: i32,
    pub name: String,
    pub description: String,
    pub owner_id: i32,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Prompt {
    pub id: i32,
    pub user_id: i32,
    pub application_id: i32,
    pub prompt_text: String,
    pub response_text: Option<String>,
    pub business_domain: Option<String>,
    pub created_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct License {
    pub id: i32,
    pub license_key: String,
    pub user_id: i32,
    pub license_type: String,
    pub expires_at: Option<chrono::DateTime<chrono::Utc>>,
    pub max_downloads: i32,
    pub current_downloads: i32,
    pub created_at: chrono::DateTime<chrono::Utc>,
}