//! Instagram Graph API webhook parser
//!
//! Handles Instagram webhooks for:
//! - Comments on media posts
//! - Mentions in comments
//! - Direct messages (DMs)
//!
//! Reference: https://developers.facebook.com/docs/graph-api/webhooks/reference/instagram

use serde::{Deserialize, Serialize};
use serde_json::Value;
use anyhow::{anyhow, Result};

/// Standardized Instagram comment webhook payload
///
/// Extracted from Instagram Graph API webhook format:
/// changes[0].value contains the comment data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InstagramComment {
    /// Unique comment ID from Instagram
    pub comment_id: String,

    /// Media ID where comment was posted (for comments)
    /// or conversation ID (for DMs)
    pub media_id: String,

    /// Username of the commenter
    pub username: String,

    /// Comment text content
    pub comment_text: String,

    /// Media URL (if comment includes media attachment)
    pub media_url: Option<String>,

    /// Timestamp from webhook (Unix timestamp in milliseconds)
    pub timestamp: i64,

    /// Parent comment ID (for threaded replies)
    /// None for top-level comments
    pub parent_comment_id: Option<String>,

    /// Type of webhook: "comment" or "message"
    pub webhook_type: String,
}

/// Parse Instagram webhook payload into standardized InstagramComment
///
/// # Arguments
/// * `payload` - Raw JSON webhook payload from Instagram
///
/// # Returns
/// * `Ok(InstagramComment)` - Parsed comment data
/// * `Err(anyhow::Error)` - Parsing failed
///
/// # Example Payload (Comment)
/// ```json
/// {
///   "changes": [{
///     "value": {
///       "id": "123456789",
///       "media": {"id": "987654321", "image_url": "https://..."},
///       "from": {"username": "john_doe"},
///       "text": "Great post!"
///     }
///   }]
/// }
/// ```
pub fn parse_instagram_webhook(payload: &Value) -> Result<InstagramComment> {
    // Extract changes array
    let changes = payload["changes"]
        .as_array()
        .ok_or_else(|| anyhow!("Missing 'changes' array"))?;

    let change = changes.first()
        .ok_or_else(|| anyhow!("Empty 'changes' array"))?;

    let value = &change["value"];

    // Extract comment ID
    let comment_id = value["id"]
        .as_str()
        .ok_or_else(|| anyhow!("Missing comment 'id'"))?
        .to_string();

    // Extract media ID
    let media_id = value["media"]
        .as_object()
        .and_then(|m| m.get("id"))
        .and_then(|v| v.as_str())
        .ok_or_else(|| anyhow!("Missing media 'id'"))?
        .to_string();

    // Extract username
    let username = value["from"]
        .as_object()
        .and_then(|f| f.get("username"))
        .and_then(|v| v.as_str())
        .ok_or_else(|| anyhow!("Missing 'from.username'"))?
        .to_string();

    // Extract comment text
    let comment_text = value["text"]
        .as_str()
        .unwrap_or("")
        .to_string();

    // Extract media URL (optional)
    let media_url = value["media"]
        .as_object()
        .and_then(|m| m.get("image_url"))
        .and_then(|v| v.as_str())
        .map(|s| s.to_string());

    // Extract timestamp (convert to milliseconds if in seconds)
    let timestamp = value["timestamp"]
        .as_i64()
        .unwrap_or_else(|| {
            chrono::Utc::now().timestamp_millis()
        });

    // Extract parent comment ID (for replies)
    let parent_comment_id = value["parent_comment_id"]
        .as_str()
        .map(|s| s.to_string());

    // Determine webhook type
    let webhook_type = if value.get("conversation_id").is_some() {
        "message".to_string()
    } else {
        "comment".to_string()
    };

    Ok(InstagramComment {
        comment_id,
        media_id,
        username,
        comment_text,
        media_url,
        timestamp,
        parent_comment_id,
        webhook_type,
    })
}

/// Extract comment ID from Instagram webhook payload
///
/// # Arguments
/// * `payload` - Raw JSON webhook payload
///
/// # Returns
/// * `Ok(String)` - Comment ID
/// * `Err(anyhow::Error)` - Extraction failed
pub fn extract_comment_id(payload: &Value) -> Result<String> {
    let comment_id = payload["changes"][0]["value"]["id"]
        .as_str()
        .ok_or_else(|| anyhow!("Missing comment 'id' in payload"))?;

    Ok(comment_id.to_string())
}

/// Extract media URL from Instagram webhook payload
///
/// # Arguments
/// * `payload` - Raw JSON webhook payload
///
/// # Returns
/// * `Ok(String)` - Media URL
/// * `Err(anyhow::Error)` - Extraction failed or no media
pub fn extract_media_url(payload: &Value) -> Result<String> {
    let media_url = payload["changes"][0]["value"]["media"]["image_url"]
        .as_str()
        .ok_or_else(|| anyhow!("Missing media 'image_url' in payload"))?;

    Ok(media_url.to_string())
}

/// Check if webhook is a comment (not like, follow, etc.)
///
/// Instagram webhooks can be for various events:
/// - comments (what we want)
/// - likes (ignore)
/// - follows (ignore)
/// - mentions (treat as comment)
///
/// # Arguments
/// * `payload` - Raw JSON webhook payload
///
/// # Returns
/// * `true` - Webhook is comment-related
/// * `false` - Webhook is for other event type
pub fn is_comment_webhook(payload: &Value) -> bool {
    // Check if 'changes' array exists
    let changes = match payload["changes"].as_array() {
        Some(c) => c,
        None => return false,
    };

    // Check if first change has 'value' field
    let value = match changes.first().and_then(|v| v.get("value")) {
        Some(v) => v,
        None => return false,
    };

    // Comment webhooks have 'id' and 'text' fields
    value.get("id").is_some() && value.get("text").is_some()
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_parse_instagram_comment() {
        let payload = json!({
            "changes": [{
                "value": {
                    "id": "123456789",
                    "media": {
                        "id": "987654321",
                        "image_url": "https://instagram.com/example.jpg"
                    },
                    "from": {"username": "john_doe"},
                    "text": "Great post!",
                    "timestamp": 1712829600
                }
            }]
        });

        let comment = parse_instagram_webhook(&payload).unwrap();
        assert_eq!(comment.comment_id, "123456789");
        assert_eq!(comment.media_id, "987654321");
        assert_eq!(comment.username, "john_doe");
        assert_eq!(comment.comment_text, "Great post!");
        assert_eq!(comment.media_url, Some("https://instagram.com/example.jpg".to_string()));
        assert_eq!(comment.webhook_type, "comment");
        assert!(comment.parent_comment_id.is_none());
    }

    #[test]
    fn test_parse_instagram_comment_reply() {
        let payload = json!({
            "changes": [{
                "value": {
                    "id": "987654321",
                    "media": {"id": "123456789"},
                    "from": {"username": "jane_smith"},
                    "text": "I agree!",
                    "parent_comment_id": "123456789",
                    "timestamp": 1712829700
                }
            }]
        });

        let comment = parse_instagram_webhook(&payload).unwrap();
        assert_eq!(comment.comment_id, "987654321");
        assert_eq!(comment.parent_comment_id, Some("123456789".to_string()));
        assert_eq!(comment.comment_text, "I agree!");
    }

    #[test]
    fn test_parse_instagram_comment_no_media() {
        let payload = json!({
            "changes": [{
                "value": {
                    "id": "111111111",
                    "media": {"id": "222222222"},
                    "from": {"username": "bob_test"},
                    "text": "No media here"
                }
            }]
        });

        let comment = parse_instagram_webhook(&payload).unwrap();
        assert_eq!(comment.comment_id, "111111111");
        assert!(comment.media_url.is_none());
        assert_eq!(comment.comment_text, "No media here");
    }

    #[test]
    fn test_extract_comment_id() {
        let payload = json!({
            "changes": [{
                "value": {"id": "comment_123"}
            }]
        });

        let id = extract_comment_id(&payload).unwrap();
        assert_eq!(id, "comment_123");
    }

    #[test]
    fn test_extract_media_url() {
        let payload = json!({
            "changes": [{
                "value": {
                    "media": {"image_url": "https://example.com/media.jpg"}
                }
            }]
        });

        let url = extract_media_url(&payload).unwrap();
        assert_eq!(url, "https://example.com/media.jpg");
    }

    #[test]
    fn test_is_comment_webhook_true() {
        let payload = json!({
            "changes": [{
                "value": {
                    "id": "123",
                    "text": "This is a comment"
                }
            }]
        });

        assert!(is_comment_webhook(&payload));
    }

/// Download media from Instagram Media URL
///
/// TODO: Implement full media download logic for MVP
/// - Download media from Instagram Graph API
/// - Handle authentication with access token
/// - Store media in S3 or local storage
/// - Return stored media URL
///
/// Args:
///     media_url: Media URL from Instagram webhook
///
/// Returns:
///     Stored media URL or original URL if not implemented
pub async fn download_instagram_media(media_url: &str) -> Result<String> {
    // MVP STUB: Return original URL
    // TODO: Implement media download and storage
    ::tracing::warn!("Instagram media download not implemented yet (MVP stub)");
    Ok(media_url.to_string())
}

    #[test]
    fn test_is_comment_webhook_false_like() {
        let payload = json!({
            "changes": [{
                "value": {
                    "action": "like"
                }
            }]
        });

        assert!(!is_comment_webhook(&payload));
    }

    #[test]
    fn test_is_comment_webhook_false_empty() {
        let payload = json!({
            "changes": []
        });

        assert!(!is_comment_webhook(&payload));
    }

    #[test]
    fn test_parse_invalid_payload_missing_changes() {
        let payload = json!({
            "data": "something"
        });

        let result = parse_instagram_webhook(&payload);
        assert!(result.is_err());
    }

    #[test]
    fn test_parse_invalid_payload_missing_id() {
        let payload = json!({
            "changes": [{
                "value": {
                    "media": {"id": "123"}
                }
            }]
        });

        let result = parse_instagram_webhook(&payload);
        assert!(result.is_err());
    }
}
