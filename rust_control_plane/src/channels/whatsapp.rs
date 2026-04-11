//! WhatsApp webhook payload parser
//!
//! Parses WhatsApp Business Cloud API webhooks into a normalized MessagePayload struct.
//!
//! WhatsApp webhook format:
//! - entry[0].changes[0].value.messages[0] contains message data
//! - entry[0].changes[0].value.statuses[0] contains status updates
//! - Message types: text, image, audio, document, video, location, contacts
//!
//! Reference: https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload

use serde_json::Value;
use anyhow::{Result, Context};

/// Normalized message payload from WhatsApp webhook
#[derive(Debug, Clone, PartialEq)]
pub struct MessagePayload {
    /// Unique message ID from WhatsApp (wamid.*)
    pub message_id: String,
    /// Sender phone number (in international format)
    pub sender: String,
    /// Recipient phone number (WhatsApp Business ID)
    pub recipient: Option<String>,
    /// Message type: text, image, audio, document, video, location, contacts
    pub message_type: String,
    /// Message content (text body or caption for media)
    pub content: Option<String>,
    /// Media URL (for image, audio, document, video)
    pub media_url: Option<String>,
    /// Timestamp from WhatsApp (Unix epoch)
    pub timestamp: Option<i64>,
}

/// Extract message ID from WhatsApp webhook payload
///
/// Returns: entry[0].changes[0].value.messages[0].id
pub fn extract_message_id(payload: &Value) -> Result<String> {
    let id = payload["entry"][0]["changes"][0]["value"]["messages"][0]["id"]
        .as_str()
        .ok_or_else(|| anyhow::anyhow!("Message ID not found in payload"))?;

    Ok(id.to_string())
}

/// Extract sender phone number from WhatsApp webhook payload
///
/// Returns: entry[0].changes[0].value.messages[0].from
pub fn extract_sender_phone(payload: &Value) -> Result<String> {
    let phone = payload["entry"][0]["changes"][0]["value"]["messages"][0]["from"]
        .as_str()
        .ok_or_else(|| anyhow::anyhow!("Sender phone not found in payload"))?;

    Ok(phone.to_string())
}

/// Check if webhook is a message (not a status update)
///
/// Returns true if payload contains messages array
/// Returns false if payload contains statuses array
pub fn is_message_webhook(payload: &Value) -> bool {
    payload["entry"][0]["changes"][0]["value"]["messages"].is_array()
}

/// Parse WhatsApp webhook payload into normalized MessagePayload
///
/// Extracts message_id, sender, message_type, content, media_url, timestamp
/// Handles text, image, audio, document message types
pub fn parse_whatsapp_webhook(payload: Value) -> Result<MessagePayload> {
    // Extract message array
    let message = &payload["entry"][0]["changes"][0]["value"]["messages"][0];

    // Extract required fields
    let message_id = message["id"]
        .as_str()
        .context("Message ID is required")?
        .to_string();

    let sender = message["from"]
        .as_str()
        .context("Sender phone is required")?
        .to_string();

    let recipient = message["to"].as_str().map(|s| s.to_string());

    let timestamp = message["timestamp"]
        .as_str()
        .and_then(|s| s.parse::<i64>().ok());

    // Determine message type and extract content
    let (message_type, content, media_url) = if message.contains_key("text") {
        let text_body = message["text"]["body"]
            .as_str()
            .map(|s| s.to_string());
        ("text".to_string(), text_body, None)
    } else if message.contains_key("image") {
        let caption = message["image"]["caption"]
            .as_str()
            .map(|s| s.to_string());
        let url = message["image"]["url"]
            .as_str()
            .map(|s| s.to_string());
        ("image".to_string(), caption, url)
    } else if message.contains_key("audio") {
        let url = message["audio"]["url"]
            .as_str()
            .map(|s| s.to_string());
        ("audio".to_string(), None, url)
    } else if message.contains_key("document") {
        let caption = message["document"]["caption"]
            .as_str()
            .map(|s| s.to_string());
        let url = message["document"]["url"]
            .as_str()
            .map(|s| s.to_string());
        ("document".to_string(), caption, url)
    } else if message.contains_key("video") {
        let caption = message["video"]["caption"]
            .as_str()
            .map(|s| s.to_string());
        let url = message["video"]["url"]
            .as_str()
            .map(|s| s.to_string());
        ("video".to_string(), caption, url)
    } else if message.contains_key("location") {
        let location_text = format!(
            "{},{}",
            message["location"]["latitude"].as_f64().unwrap_or(0.0),
            message["location"]["longitude"].as_f64().unwrap_or(0.0)
        );
        ("location".to_string(), Some(location_text), None)
    } else if message.contains_key("contacts") {
        ("contacts".to_string(), None, None)
    } else if message.contains_key("interactive") {
        // Interactive response (button, list reply)
        let interactive_type = message["interactive"]["type"]
            .as_str()
            .unwrap_or("unknown")
            .to_string();
        (format!("interactive_{}", interactive_type), None, None)
    } else {
        ("unknown".to_string(), None, None)
    };

    Ok(MessagePayload {
        message_id,
        sender,
        recipient,
        message_type,
        content,
        media_url,
        timestamp,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_extract_message_id() {
        let payload = json!({
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{"id": "wamid.example123"}]
                    }
                }]
            }]
        });

        let id = extract_message_id(&payload).unwrap();
        assert_eq!(id, "wamid.example123");
    }

    #[test]
    fn test_extract_sender_phone() {
        let payload = json!({
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{"from": "1234567890"}]
                    }
                }]
            }]
        });

        let phone = extract_sender_phone(&payload).unwrap();
        assert_eq!(phone, "1234567890");
    }

    #[test]
    fn test_is_message_webhook() {
        let message_payload = json!({
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{"id": "wamid.example123"}]
                    }
                }]
            }]
        });

        assert!(is_message_webhook(&message_payload));

        let status_payload = json!({
            "entry": [{
                "changes": [{
                    "value": {
                        "statuses": [{"id": "wamid.example123", "status": "sent"}]
                    }
                }]
            }]
        });

        assert!(!is_message_webhook(&status_payload));
    }

    #[test]
    fn test_parse_text_message() {
        let payload = json!({
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "1234567890",
                            "id": "wamid.example123",
                            "timestamp": "1699999999",
                            "text": {"body": "Hello, world!"}
                        }]
                    }
                }]
            }]
        });

        let parsed = parse_whatsapp_webhook(payload).unwrap();
        assert_eq!(parsed.message_id, "wamid.example123");
        assert_eq!(parsed.sender, "1234567890");
        assert_eq!(parsed.message_type, "text");
        assert_eq!(parsed.content, Some("Hello, world!".to_string()));
        assert!(parsed.media_url.is_none());
        assert_eq!(parsed.timestamp, Some(1699999999));
    }

    #[test]
    fn test_parse_image_message() {
        let payload = json!({
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "1234567890",
                            "id": "wamid.example456",
                            "timestamp": "1699999999",
                            "image": {
                                "caption": "Check this out",
                                "url": "https://example.com/image.jpg"
                            }
                        }]
                    }
                }]
            }]
        });

        let parsed = parse_whatsapp_webhook(payload).unwrap();
        assert_eq!(parsed.message_type, "image");
        assert_eq!(parsed.content, Some("Check this out".to_string()));
        assert_eq!(parsed.media_url, Some("https://example.com/image.jpg".to_string()));
    }

/// Download media from WhatsApp Media URL
///
/// TODO: Implement full media download logic for MVP
/// - Download media from WhatsApp Media API
/// - Store media in S3 or local storage
/// - Return stored media URL
///
/// Args:
///     media_url: Media URL from WhatsApp webhook
///
/// Returns:
///     Stored media URL or original URL if not implemented
pub async fn download_media(media_url: &str) -> Result<String> {
    // MVP STUB: Return original URL
    // TODO: Implement media download and storage
    ::tracing::warn!("WhatsApp media download not implemented yet (MVP stub)");
    Ok(media_url.to_string())
}

/// Store media file from WhatsApp
///
/// TODO: Implement full media storage logic for MVP
/// - Download media from URL
/// - Generate unique filename
/// - Store in configured storage backend (S3, local, etc.)
/// - Return stored media URL
///
/// Args:
///     media_url: Media URL from WhatsApp webhook
///     message_id: Message ID for filename generation
///
/// Returns:
///     Stored media URL
pub async fn store_media(media_url: &str, message_id: &str) -> Result<String> {
    // MVP STUB: Return original URL with message_id prefix
    // TODO: Implement media storage
    ::tracing::warn!(
        "WhatsApp media storage not implemented yet (MVP stub): url={}, message_id={}",
        media_url,
        message_id
    );
    Ok(format!("{}#{}", media_url, message_id))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_audio_message() {
        let payload = json!({
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "1234567890",
                            "id": "wamid.example789",
                            "audio": {
                                "url": "https://example.com/audio.mp3"
                            }
                        }]
                    }
                }]
            }]
        });

        let parsed = parse_whatsapp_webhook(payload).unwrap();
        assert_eq!(parsed.message_type, "audio");
        assert_eq!(parsed.media_url, Some("https://example.com/audio.mp3".to_string()));
    }

    #[test]
    fn test_parse_document_message() {
        let payload = json!({
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "1234567890",
                            "id": "wamid.example999",
                            "document": {
                                "caption": "Important doc",
                                "url": "https://example.com/document.pdf"
                            }
                        }]
                    }
                }]
            }]
        });

        let parsed = parse_whatsapp_webhook(payload).unwrap();
        assert_eq!(parsed.message_type, "document");
        assert_eq!(parsed.content, Some("Important doc".to_string()));
        assert_eq!(parsed.media_url, Some("https://example.com/document.pdf".to_string()));
    }
}
