//! Email webhook payload parser
//!
//! Supports SendGrid, Mailgun, and Postmark webhook formats.
//! Normalizes incoming emails into a common EmailMessage struct.
//!
//! Features:
//! - Parse email headers (Message-ID, In-Reply-To, References)
//! - Extract thread IDs for email threading
//! - Handle attachments
//! - Support multiple webhook providers

use anyhow::{anyhow, Result};
use serde_json::Value;

/// Standardized email message from webhook
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct EmailMessage {
    /// Unique message ID from Message-ID header
    pub message_id: String,
    /// Sender email address
    pub from_email: String,
    /// Recipient email address
    pub to_email: String,
    /// Email subject
    pub subject: String,
    /// Plain text body
    pub plain_text: Option<String>,
    /// HTML body
    pub html_body: Option<String>,
    /// Thread ID (from References or In-Reply-To header)
    pub thread_id: Option<String>,
    /// Message timestamp (Unix timestamp)
    pub timestamp: i64,
    /// Email attachments
    pub attachments: Vec<Attachment>,
}

/// Email attachment
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct Attachment {
    /// Attachment filename
    pub filename: String,
    /// Content type (MIME type)
    pub content_type: String,
    /// File size in bytes
    pub size: u64,
    /// Download URL
    pub url: String,
}

/// Parse email webhook payload from any supported provider
///
/// Supports:
/// - SendGrid: https://docs.sendgrid.com/for-developers/tracking-events/event
/// - Mailgun: https://documentation.mailgun.com/en/latest/user_manual.html#webhooks
/// - Postmark: https://postmarkapp.com/developer/user-guide/inbound/parse
///
/// # Arguments
/// * `payload` - JSON payload from webhook
///
/// # Returns
/// * `Ok(EmailMessage)` - Parsed email message
/// * `Err(anyhow::Error)` - Parsing error
pub fn parse_email_webhook(payload: Value) -> Result<EmailMessage> {
    // Detect webhook format
    let provider = detect_provider(&payload);

    match provider.as_str() {
        "sendgrid" => parse_sendgrid(payload),
        "mailgun" => parse_mailgun(payload),
        "postmark" => parse_postmark(payload),
        _ => Err(anyhow!("Unknown or unsupported email webhook provider")),
    }
}

/// Detect email webhook provider from payload structure
fn detect_provider(payload: &Value) -> String {
    // SendGrid has an array of events with "email" field
    if payload.get("events").and_then(|v| v.as_array()).is_some() {
        return "sendgrid".to_string();
    }

    // Mailgun has "signature" and "event-data" fields
    if payload.get("signature").is_some() || payload.get("event-data").is_some() {
        return "mailgun".to_string();
    }

    // Postmark has "From", "Subject", etc. at top level
    if payload.get("From").is_some() || payload.get("Subject").is_some() {
        return "postmark".to_string();
    }

    "unknown".to_string()
}

/// Parse SendGrid webhook payload
fn parse_sendgrid(payload: Value) -> Result<EmailMessage> {
    // SendGrid sends an array of events, take the first one
    let event = payload["events"]
        .as_array()
        .and_then(|events| events.first())
        .ok_or_else(|| anyhow!("SendGrid payload missing events array"))?;

    let message_id = event["sg_message_id"]
        .as_str()
        .ok_or_else(|| anyhow!("SendGrid missing sg_message_id"))?
        .to_string();

    let from_email = event["email"]
        .as_str()
        .or_else(|| event["from"].as_str())
        .ok_or_else(|| anyhow!("SendGrid missing email/from"))?
        .to_string();

    let to_email = event["to_email"]
        .as_str()
        .unwrap_or(&event["to"].as_str().unwrap_or("unknown"))
        .to_string();

    let subject = event["subject"]
        .as_str()
        .unwrap_or("")
        .to_string();

    let plain_text = event["text"]
        .as_str()
        .map(|s| s.to_string());

    let html_body = event["html"]
        .as_str()
        .map(|s| s.to_string());

    // Extract thread ID from headers
    let thread_id = extract_thread_id_from_headers(&event["headers"]);

    // Extract timestamp
    let timestamp = event["timestamp"]
        .as_i64()
        .unwrap_or_else(|| chrono::Utc::now().timestamp());

    // Parse attachments (SendGrid includes attachment info in event)
    let attachments = parse_sendgrid_attachments(event);

    Ok(EmailMessage {
        message_id,
        from_email,
        to_email,
        subject,
        plain_text,
        html_body,
        thread_id,
        timestamp,
        attachments,
    })
}

/// Parse Mailgun webhook payload
fn parse_mailgun(payload: Value) -> Result<EmailMessage> {
    let event_data = &payload["event-data"];

    let message_id = event_data["message"]["headers"]["message-id"]
        .as_str()
        .or_else(|| event_data["message"]["message_id"].as_str())
        .ok_or_else(|| anyhow!("Mailgun missing message-id"))?
        .to_string();

    let from_email = event_data["message"]["from"]
        .as_str()
        .ok_or_else(|| anyhow!("Mailgun missing from"))?
        .to_string();

    let to_email = event_data["message"]["to"]
        .as_str()
        .ok_or_else(|| anyhow!("Mailgun missing to"))?
        .to_string();

    let subject = event_data["message"]["subject"]
        .as_str()
        .unwrap_or("")
        .to_string();

    let plain_text = event_data["message"]["body-plain"]
        .as_str()
        .map(|s| s.to_string());

    let html_body = event_data["message"]["body-html"]
        .as_str()
        .map(|s| s.to_string());

    // Extract thread ID from headers
    let thread_id = extract_thread_id_from_headers(&event_data["message"]["headers"]);

    // Extract timestamp
    let timestamp = event_data["timestamp"]
        .as_f64()
        .unwrap_or_else(|| chrono::Utc::now().timestamp() as f64) as i64;

    // Parse attachments
    let attachments = parse_mailgun_attachments(&event_data["message"]["attachments"]);

    Ok(EmailMessage {
        message_id,
        from_email,
        to_email,
        subject,
        plain_text,
        html_body,
        thread_id,
        timestamp,
        attachments,
    })
}

/// Parse Postmark webhook payload
fn parse_postmark(payload: Value) -> Result<EmailMessage> {
    let message_id = payload["MessageID"]
        .as_str()
        .ok_or_else(|| anyhow!("Postmark missing MessageID"))?
        .to_string();

    let from_email = payload["From"]
        .as_str()
        .ok_or_else(|| anyhow!("Postmark missing From"))?
        .to_string();

    let to_email = payload["To"]
        .as_str()
        .ok_or_else(|| anyhow!("Postmark missing To"))?
        .to_string();

    let subject = payload["Subject"]
        .as_str()
        .unwrap_or("")
        .to_string();

    let plain_text = payload["TextBody"]
        .as_str()
        .map(|s| s.to_string());

    let html_body = payload["HtmlBody"]
        .as_str()
        .map(|s| s.to_string());

    // Extract thread ID from headers
    let thread_id = extract_thread_id_postmark(&payload).ok();

    // Extract timestamp
    let timestamp = payload["Timestamp"]
        .as_str()
        .and_then(|s| chrono::DateTime::parse_from_rfc3339(s).ok())
        .map(|dt| dt.timestamp())
        .unwrap_or_else(|| chrono::Utc::now().timestamp());

    // Parse attachments
    let attachments = parse_postmark_attachments(&payload["Attachments"]);

    Ok(EmailMessage {
        message_id,
        from_email,
        to_email,
        subject,
        plain_text,
        html_body,
        thread_id,
        timestamp,
        attachments,
    })
}

/// Extract Message-ID header from payload
///
/// # Arguments
/// * `payload` - Webhook payload
///
/// # Returns
/// * `Ok(String)` - Message-ID header value
/// * `Err(anyhow::Error)` - Message-ID not found
pub fn extract_message_id(payload: Value) -> Result<String> {
    let provider = detect_provider(&payload);

    match provider.as_str() {
        "sendgrid" => {
            let event = payload["events"][0].as_object()
                .ok_or_else(|| anyhow!("SendGrid missing events"))?;
            event.get("sg_message_id")
                .or_else(|| event.get("message-id"))
                .and_then(|v| v.as_str())
                .map(|s| s.to_string())
                .ok_or_else(|| anyhow!("SendGrid missing message-id"))
        }
        "mailgun" => {
            payload["event-data"]["message"]["headers"]["message-id"]
                .as_str()
                .or_else(|| payload["event-data"]["message"]["message_id"].as_str())
                .map(|s| s.to_string())
                .ok_or_else(|| anyhow!("Mailgun missing message-id"))
        }
        "postmark" => {
            payload["MessageID"]
                .as_str()
                .map(|s| s.to_string())
                .ok_or_else(|| anyhow!("Postmark missing MessageID"))
        }
        _ => Err(anyhow!("Unknown provider for message-id extraction")),
    }
}

/// Extract thread ID from References or In-Reply-To headers
///
/// Thread ID is used to group related emails in conversations.
/// Priority: References > In-Reply-To
///
/// # Arguments
/// * `payload` - Webhook payload
///
/// # Returns
/// * `Ok(String)` - Thread ID (may be empty if not a reply)
/// * `Err(anyhow::Error)` - Extraction error
pub fn extract_thread_id(payload: Value) -> Result<Option<String>> {
    let provider = detect_provider(&payload);

    match provider.as_str() {
        "sendgrid" => {
            let event = payload["events"][0].as_object()
                .ok_or_else(|| anyhow!("SendGrid missing events"))?;
            Ok(extract_thread_id_from_headers(event.get("headers").unwrap_or(&Value::Null)))
        }
        "mailgun" => {
            Ok(extract_thread_id_from_headers(&payload["event-data"]["message"]["headers"]))
        }
        "postmark" => {
            Ok(extract_thread_id_postmark(&payload).ok())
        }
        _ => Err(anyhow!("Unknown provider for thread-id extraction")),
    }
}

/// Extract thread ID from headers object (common logic)
fn extract_thread_id_from_headers(headers: &Value) -> Option<String> {
    // Try References header first (contains thread history)
    if let Some(references) = headers.get("references").and_then(|v| v.as_str()) {
        let refs: Vec<&str> = references.split_whitespace().collect();
        if !refs.is_empty() {
            // Return the first (oldest) reference as thread ID
            return Some(refs[0].to_string());
        }
    }

    // Fallback to In-Reply-To header
    if let Some(in_reply_to) = headers.get("in-reply-to").and_then(|v| v.as_str()) {
        return Some(in_reply_to.to_string());
    }

    None
}

/// Extract thread ID from Postmark-specific headers
fn extract_thread_id_postmark(payload: &Value) -> Result<String> {
    // Postmark has References header at top level
    if let Some(references) = payload.get("References").and_then(|v| v.as_str()) {
        let refs: Vec<&str> = references.split_whitespace().collect();
        if !refs.is_empty() {
            return Ok(refs[0].to_string());
        }
    }

    // Try InReplyTo header
    if let Some(in_reply_to) = payload.get("InReplyTo").and_then(|v| v.as_str()) {
        return Ok(in_reply_to.to_string());
    }

    Ok(String::new())
}

/// Check if payload is a valid email webhook
///
/// # Arguments
/// * `payload` - Webhook payload
///
/// # Returns
/// * `true` - Valid email webhook
/// * `false` - Not an email webhook
pub fn is_email_webhook(payload: &Value) -> bool {
    detect_provider(payload) != "unknown"
}

/// Parse SendGrid attachments
fn parse_sendgrid_attachments(event: &Value) -> Vec<Attachment> {
    let mut attachments = Vec::new();

    if let Some(attachment_array) = event.get("attachments").and_then(|v| v.as_array()) {
        for att in attachment_array {
            if let (Some(filename), Some(content_type), Some(size), Some(url)) = (
                att.get("filename").and_then(|v| v.as_str()),
                att.get("type").and_then(|v| v.as_str()),
                att.get("size").and_then(|v| as_u64(v)),
                att.get("url").and_then(|v| v.as_str()),
            ) {
                attachments.push(Attachment {
                    filename: filename.to_string(),
                    content_type: content_type.to_string(),
                    size,
                    url: url.to_string(),
                });
            }
        }
    }

    attachments
}

/// Parse Mailgun attachments
fn parse_mailgun_attachments(attachments: &Value) -> Vec<Attachment> {
    let mut result = Vec::new();

    if let Some(attachment_array) = attachments.as_array() {
        for att in attachment_array {
            if let (Some(filename), Some(content_type), Some(size), Some(url)) = (
                att.get("filename").and_then(|v| v.as_str()),
                att.get("content-type").and_then(|v| v.as_str()),
                att.get("size").and_then(|v| as_u64(v)),
                att.get("url").and_then(|v| v.as_str()),
            ) {
                result.push(Attachment {
                    filename: filename.to_string(),
                    content_type: content_type.to_string(),
                    size,
                    url: url.to_string(),
                });
            }
        }
    }

    result
}

/// Parse Postmark attachments
fn parse_postmark_attachments(attachments: &Value) -> Vec<Attachment> {
    let mut result = Vec::new();

    if let Some(attachment_array) = attachments.as_array() {
        for att in attachment_array {
            if let (Some(name), Some(content_type), Some(content_length), Some(url)) = (
                att.get("Name").and_then(|v| v.as_str()),
                att.get("ContentType").and_then(|v| v.as_str()),
                att.get("ContentLength").and_then(|v| as_u64(v)),
                att.get("URL").and_then(|v| v.as_str()),
            ) {
                result.push(Attachment {
                    filename: name.to_string(),
                    content_type: content_type.to_string(),
                    size: content_length,
                    url: url.to_string(),
                });
            }
        }
    }

    result
}

/// Helper to convert JSON number to u64
fn as_u64(value: &Value) -> Option<u64> {
    if let Some(i) = value.as_i64() {
        u64::try_from(i).ok()
    } else {
        value.as_u64()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_parse_sendgrid_webhook() {
        let payload = json!({
            "events": [{
                "sg_message_id": "12345@example.com",
                "email": "sender@example.com",
                "to": "recipient@example.com",
                "subject": "Test Email",
                "text": "Plain text body",
                "html": "<p>HTML body</p>",
                "timestamp": 1234567890,
                "headers": {
                    "references": "<original@example.com>",
                    "in-reply-to": "<parent@example.com>"
                },
                "attachments": [{
                    "filename": "test.pdf",
                    "type": "application/pdf",
                    "size": 1024,
                    "url": "https://example.com/test.pdf"
                }]
            }]
        });

        let result = parse_email_webhook(payload).unwrap();
        assert_eq!(result.message_id, "12345@example.com");
        assert_eq!(result.from_email, "sender@example.com");
        assert_eq!(result.to_email, "recipient@example.com");
        assert_eq!(result.subject, "Test Email");
        assert_eq!(result.plain_text, Some("Plain text body".to_string()));
        assert_eq!(result.html_body, Some("<p>HTML body</p>".to_string()));
        assert_eq!(result.thread_id, Some("original@example.com".to_string()));
        assert_eq!(result.timestamp, 1234567890);
        assert_eq!(result.attachments.len(), 1);
        assert_eq!(result.attachments[0].filename, "test.pdf");
    }

    #[test]
    fn test_parse_mailgun_webhook() {
        let payload = json!({
            "event-data": {
                "message": {
                    "headers": {
                        "message-id": "67890@example.com"
                    },
                    "from": "sender@example.com",
                    "to": "recipient@example.com",
                    "subject": "Mailgun Test",
                    "body-plain": "Plain text",
                    "body-html": "<p>HTML</p>",
                    "timestamp": 1234567890.0,
                    "attachments": [{
                        "filename": "doc.pdf",
                        "content-type": "application/pdf",
                        "size": 2048,
                        "url": "https://example.com/doc.pdf"
                    }]
                }
            }
        });

        let result = parse_email_webhook(payload).unwrap();
        assert_eq!(result.message_id, "67890@example.com");
        assert_eq!(result.from_email, "sender@example.com");
        assert_eq!(result.to_email, "recipient@example.com");
        assert_eq!(result.subject, "Mailgun Test");
        assert_eq!(result.plain_text, Some("Plain text".to_string()));
        assert_eq!(result.html_body, Some("<p>HTML</p>".to_string()));
        assert_eq!(result.attachments.len(), 1);
    }

    #[test]
    fn test_parse_postmark_webhook() {
        let payload = json!({
            "MessageID": "ABCDE@example.com",
            "From": "sender@example.com",
            "To": "recipient@example.com",
            "Subject": "Postmark Test",
            "TextBody": "Plain text",
            "HtmlBody": "<p>HTML</p>",
            "Timestamp": "2023-01-01T00:00:00Z",
            "Attachments": [{
                "Name": "file.pdf",
                "ContentType": "application/pdf",
                "ContentLength": 4096,
                "URL": "https://example.com/file.pdf"
            }]
        });

        let result = parse_email_webhook(payload).unwrap();
        assert_eq!(result.message_id, "ABCDE@example.com");
        assert_eq!(result.from_email, "sender@example.com");
        assert_eq!(result.to_email, "recipient@example.com");
        assert_eq!(result.subject, "Postmark Test");
        assert_eq!(result.plain_text, Some("Plain text".to_string()));
        assert_eq!(result.html_body, Some("<p>HTML</p>".to_string()));
        assert_eq!(result.attachments.len(), 1);
    }

    #[test]
    fn test_extract_message_id() {
        let payload = json!({
            "events": [{
                "sg_message_id": "test@example.com"
            }]
        });

        let result = extract_message_id(payload).unwrap();
        assert_eq!(result, "test@example.com");
    }

    #[test]
    fn test_extract_thread_id_with_references() {
        let payload = json!({
            "events": [{
                "headers": {
                    "references": "<original@example.com> <parent@example.com>",
                    "in-reply-to": "<parent@example.com>"
                }
            }]
        });

        let result = extract_thread_id(payload).unwrap();
        assert_eq!(result, Some("original@example.com".to_string()));
    }

    #[test]
    fn test_extract_thread_id_fallback_to_in_reply_to() {
        let payload = json!({
            "events": [{
                "headers": {
                    "in-reply-to": "<parent@example.com>"
                }
            }]
        });

        let result = extract_thread_id(payload).unwrap();
        assert_eq!(result, Some("parent@example.com".to_string()));
    }

    #[test]
    fn test_is_email_webhook() {
        let sendgrid = json!({
            "events": [{"email": "test@example.com"}]
        });

        let mailgun = json!({
            "signature": {"token": "test"},
            "event-data": {"message": {}}
        });

        let postmark = json!({
            "From": "test@example.com",
            "Subject": "Test"
        });

        let invalid = json!({
            "foo": "bar"
        });

        assert!(is_email_webhook(&sendgrid));
        assert!(is_email_webhook(&mailgun));
        assert!(is_email_webhook(&postmark));
        assert!(!is_email_webhook(&invalid));
    }
}
