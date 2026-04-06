//! Flow detection logic.
//!
//! This module analyzes user briefs and determines the appropriate
//! execution flow (auto, sync, async, etc.).
//!
//! Phase 13: Simple rule-based flow detection for PyO3 spike.

use std::collections::HashMap;

/// Flow types supported by the system.
#[derive(Debug, Clone, PartialEq)]
pub enum FlowType {
    /// Automatic flow detection (default)
    Auto,
    /// Synchronous execution
    Sync,
    /// Asynchronous execution
    Async,
    /// Batch processing
    Batch,
}

impl FlowType {
    /// Convert FlowType to string representation.
    pub fn as_str(&self) -> &'static str {
        match self {
            FlowType::Auto => "auto",
            FlowType::Sync => "sync",
            FlowType::Async => "async",
            FlowType::Batch => "batch",
        }
    }

    /// Parse string to FlowType.
    pub fn from_str(s: &str) -> Option<Self> {
        match s.to_lowercase().as_str() {
            "auto" => Some(FlowType::Auto),
            "sync" => Some(FlowType::Sync),
            "async" => Some(FlowType::Async),
            "batch" => Some(FlowType::Batch),
            _ => None,
        }
    }
}

/// Detect the appropriate flow type from a user brief.
///
/// This is a simplified rule-based implementation for the PyO3 spike.
/// In production, this would use more sophisticated NLP/ML.
///
/// # Arguments
/// * `brief` - User's brief text
///
/// # Returns
/// Detected FlowType
///
/// # Examples
/// ```
/// use crate::flow::detect;
///
/// let flow = detect("Create a report for me");
/// assert_eq!(flow, FlowType::Async);
///
/// let flow = detect("Tell me a joke");
/// assert_eq!(flow, FlowType::Sync);
/// ```
pub fn detect(brief: &str) -> FlowType {
    let brief_lower = brief.to_lowercase();

    // Keyword-based flow detection rules
    let sync_keywords = vec![
        "tell me", "explain", "what is", "how does", "define",
        "quick question", "simple", "easy"
    ];

    let async_keywords = vec![
        "create", "generate", "build", "write", "analyze",
        "research", "report", "document"
    ];

    let batch_keywords = vec![
        "multiple", "batch", "several", "list of", "many",
        "bulk", "all the"
    ];

    // Check for batch keywords first (highest priority)
    for keyword in &batch_keywords {
        if brief_lower.contains(keyword) {
            return FlowType::Batch;
        }
    }

    // Check for async keywords
    for keyword in &async_keywords {
        if brief_lower.contains(keyword) {
            return FlowType::Async;
        }
    }

    // Check for sync keywords
    for keyword in &sync_keywords {
        if brief_lower.contains(keyword) {
            return FlowType::Sync;
        }
    }

    // Default to auto if no keywords match
    FlowType::Auto
}

/// Get flow detection statistics.
///
/// Returns metadata about the flow detection process,
/// useful for debugging and monitoring.
///
/// # Arguments
/// * `brief` - User's brief text
///
/// # Returns
/// HashMap with detection metadata
pub fn detect_with_metadata(brief: &str) -> HashMap<&'static str, String> {
    let flow = detect(brief);

    let mut metadata = HashMap::new();
    metadata.insert("flow", flow.as_str().to_string());
    metadata.insert("brief_length", brief.len().to_string());
    metadata.insert("word_count", brief.split_whitespace().count().to_string());
    metadata.insert("has_batch_keywords",
        (brief.to_lowercase().contains("batch") ||
         brief.to_lowercase().contains("multiple")).to_string());
    metadata.insert("has_async_keywords",
        (brief.to_lowercase().contains("create") ||
         brief.to_lowercase().contains("generate")).to_string());
    metadata.insert("has_sync_keywords",
        (brief.to_lowercase().contains("tell me") ||
         brief.to_lowercase().contains("explain")).to_string());

    metadata
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_sync() {
        let brief = "Tell me a joke about programming";
        assert_eq!(detect(brief), FlowType::Sync);
    }

    #[test]
    fn test_detect_async() {
        let brief = "Create a comprehensive report on Q4 sales";
        assert_eq!(detect(brief), FlowType::Async);
    }

    #[test]
    fn test_detect_batch() {
        let brief = "Generate reports for multiple users";
        assert_eq!(detect(brief), FlowType::Batch);
    }

    #[test]
    fn test_detect_auto_default() {
        let brief = "Do something random";
        assert_eq!(detect(brief), FlowType::Auto);
    }

    #[test]
    fn test_detect_with_metadata() {
        let brief = "Create a report for me";
        let metadata = detect_with_metadata(brief);

        assert_eq!(metadata.get("flow"), Some(&"async".to_string()));
        assert!(metadata.get("brief_length").is_some());
        assert!(metadata.get("word_count").is_some());
    }

    #[test]
    fn test_flow_type_conversion() {
        assert_eq!(FlowType::Auto.as_str(), "auto");
        assert_eq!(FlowType::Sync.as_str(), "sync");
        assert_eq!(FlowType::Async.as_str(), "async");
        assert_eq!(FlowType::Batch.as_str(), "batch");

        assert_eq!(FlowType::from_str("auto"), Some(FlowType::Auto));
        assert_eq!(FlowType::from_str("sync"), Some(FlowType::Sync));
        assert_eq!(FlowType::from_str("invalid"), None);
    }
}
