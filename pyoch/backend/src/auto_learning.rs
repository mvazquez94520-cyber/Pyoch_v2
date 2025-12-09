use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};
use uuid::Uuid;
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct BusinessDomain {
    pub id: Uuid,
    pub name: String,
    pub description: String,
    pub keywords: Vec<String>,
    pub patterns: Vec<String>,
    pub confidence_score: f64,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct LearningRecord {
    pub id: Uuid,
    pub domain_id: Uuid,
    pub prompt: String,
    pub response: String,
    pub feedback_score: Option<f64>,
    pub is_relevant: bool,
    pub learning_timestamp: DateTime<Utc>,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AutoLearningRequest {
    pub prompt: String,
    pub feedback: Option<bool>,
    pub user_id: Option<Uuid>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct AutoLearningResponse {
    pub matched_domains: Vec<BusinessDomain>,
    pub confidence: f64,
    pub learning_updated: bool,
    pub suggestions: Vec<String>,
}

pub struct AutoLearningEngine {
    pub domains: Vec<BusinessDomain>,
    pub learning_records: Vec<LearningRecord>,
    pub keyword_stats: HashMap<String, i32>,
}

impl AutoLearningEngine {
    pub fn new() -> Self {
        AutoLearningEngine {
            domains: vec![
                BusinessDomain {
                    id: Uuid::new_v4(),
                    name: "CRM".to_string(),
                    description: "Customer Relationship Management".to_string(),
                    keywords: vec!["customer".to_string(), "contact".to_string(), "lead".to_string(), "sales".to_string()],
                    patterns: vec!["manage customers".to_string(), "track leads".to_string()],
                    confidence_score: 0.8,
                    created_at: Utc::now(),
                    updated_at: Utc::now(),
                },
                BusinessDomain {
                    id: Uuid::new_v4(),
                    name: "Inventory".to_string(),
                    description: "Inventory Management".to_string(),
                    keywords: vec!["inventory".to_string(), "stock".to_string(), "product".to_string(), "warehouse".to_string()],
                    patterns: vec!["track inventory".to_string(), "manage stock".to_string()],
                    confidence_score: 0.8,
                    created_at: Utc::now(),
                    updated_at: Utc::now(),
                },
                BusinessDomain {
                    id: Uuid::new_v4(),
                    name: "HR".to_string(),
                    description: "Human Resources".to_string(),
                    keywords: vec!["employee".to_string(), "hr".to_string(), "personnel".to_string(), "payroll".to_string()],
                    patterns: vec!["manage employees".to_string(), "track payroll".to_string()],
                    confidence_score: 0.8,
                    created_at: Utc::now(),
                    updated_at: Utc::now(),
                },
            ],
            learning_records: vec![],
            keyword_stats: HashMap::new(),
        }
    }

    pub fn identify_business_domain(&self, prompt: &str) -> Vec<BusinessDomain> {
        let mut matched_domains = Vec::new();
        let prompt_lower = prompt.to_lowercase();
        
        for domain in &self.domains {
            let mut score = 0.0;
            
            // Check for keyword matches
            for keyword in &domain.keywords {
                if prompt_lower.contains(&keyword.to_lowercase()) {
                    score += 1.0;
                }
            }
            
            // Check for pattern matches
            for pattern in &domain.patterns {
                if prompt_lower.contains(&pattern.to_lowercase()) {
                    score += 1.0;
                }
            }
            
            if score > 0.0 {
                let mut domain_with_score = domain.clone();
                // Update confidence based on matches
                domain_with_score.confidence_score = (domain.confidence_score + score / 2.0).min(1.0);
                matched_domains.push(domain_with_score);
            }
        }
        
        matched_domains.sort_by(|a, b| b.confidence_score.partial_cmp(&a.confidence_score).unwrap());
        matched_domains
    }

    pub fn learn_from_interaction(&mut self, prompt: &str, response: &str, is_relevant: bool) {
        // Record the learning interaction
        let record = LearningRecord {
            id: Uuid::new_v4(),
            domain_id: Uuid::nil(), // Will be set if matched to a specific domain
            prompt: prompt.to_string(),
            response: response.to_string(),
            feedback_score: if is_relevant { Some(1.0) } else { Some(0.0) },
            is_relevant,
            learning_timestamp: Utc::now(),
            created_at: Utc::now(),
        };
        
        self.learning_records.push(record);
        
        // Update keyword statistics
        let words: Vec<&str> = prompt.split_whitespace().collect();
        for word in words {
            let clean_word = word.trim_matches(|c: char| !c.is_alphanumeric()).to_lowercase();
            if !clean_word.is_empty() {
                *self.keyword_stats.entry(clean_word).or_insert(0) += 1;
            }
        }
        
        // Update domain knowledge based on the interaction
        if is_relevant {
            // Identify which domain this prompt relates to and update it
            let matched_domains = self.identify_business_domain(prompt);
            for mut domain in matched_domains {
                // Add new keywords or patterns from this interaction
                let words: Vec<&str> = prompt.split_whitespace().collect();
                for word in words {
                    let clean_word = word.trim_matches(|c: char| !c.is_alphanumeric()).to_lowercase();
                    if !clean_word.is_empty() && !domain.keywords.contains(&clean_word) {
                        domain.keywords.push(clean_word);
                    }
                }
                
                // Update the domain in our collection
                if let Some(existing_domain) = self.domains.iter_mut().find(|d| d.id == domain.id) {
                    existing_domain.keywords = domain.keywords;
                    existing_domain.updated_at = Utc::now();
                }
            }
        }
    }

    pub fn get_top_keywords(&self, limit: usize) -> Vec<(String, i32)> {
        let mut sorted: Vec<(String, i32)> = self.keyword_stats.iter()
            .map(|(k, v)| (k.clone(), *v))
            .collect();
        
        sorted.sort_by(|a, b| b.1.cmp(&a.1));
        sorted.truncate(limit);
        sorted
    }
}