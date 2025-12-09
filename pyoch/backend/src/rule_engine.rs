use crate::models::{Rule, Feedback, BusinessApplication};
use uuid::Uuid;
use chrono::Utc;
use anyhow::Result;

pub struct RuleEngine {
    rules: Vec<Rule>,
    feedbacks: Vec<Feedback>,
}

impl RuleEngine {
    pub fn new() -> Self {
        RuleEngine {
            rules: Vec::new(),
            feedbacks: Vec::new(),
        }
    }

    pub fn add_rule(&mut self, rule: Rule) {
        self.rules.push(rule);
    }

    pub fn get_rules(&self) -> &Vec<Rule> {
        &self.rules
    }

    pub fn add_feedback(&mut self, feedback: Feedback) {
        self.feedbacks.push(feedback);
    }

    pub fn apply_rules(&self, business_prompt: &str) -> Vec<Rule> {
        // In a real implementation, this would evaluate the business prompt
        // against the rules and return applicable ones
        // For now, we'll return all rules as a placeholder
        self.rules.clone()
    }

    pub fn update_rule_based_on_feedback(&mut self, feedback: &Feedback) -> Result<()> {
        // Find the rule that received feedback
        if let Some(rule) = self.rules.iter_mut().find(|r| r.id == feedback.rule_id) {
            // In a real implementation, we would adjust the rule based on feedback
            // For now, we just log that feedback was received
            println!("Received feedback for rule {}: relevant={}", rule.name, feedback.is_relevant);
            
            // In a real system, we would adjust the rule based on feedback
            // For example, if the feedback indicates the rule was not relevant,
            // we might decrease its priority or modify its condition
            if !feedback.is_relevant {
                rule.priority = rule.priority.saturating_sub(1);
            } else {
                rule.priority = rule.priority.saturating_add(1);
            }
        }
        
        Ok(())
    }

    pub fn generate_business_application(&self, app_type: &str, name: &str) -> BusinessApplication {
        BusinessApplication {
            id: Uuid::new_v4(),
            name: name.to_string(),
            application_type: app_type.to_string(),
            rules: self.rules.clone(),
            feedbacks: self.feedbacks.clone(),
            created_at: Utc::now(),
            updated_at: Utc::now(),
        }
    }
}