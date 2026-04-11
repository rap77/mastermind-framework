//! WhatsApp webhook parser tests
//!
//! Tests cover:
//! - Message ID extraction
//! - Sender phone extraction
//! - Text message parsing
//! - Media message parsing (image, audio, document)
//! - Status update filtering
//! - Missing field handling

use mastermind_control_plane::channels::{
    parse_whatsapp_webhook, extract_message_id, extract_sender_phone, is_message_webhook, MessagePayload
};
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
fn test_extract_message_id_missing() {
    let payload = json!({
        "entry": [{
            "changes": [{
                "value": {}
            }]
        }]
    });

    assert!(extract_message_id(&payload).is_err());
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
fn test_extract_sender_phone_missing() {
    let payload = json!({
        "entry": [{
            "changes": [{
                "value": {}
            }]
        }]
    });

    assert!(extract_sender_phone(&payload).is_err());
}

#[test]
fn test_is_message_webhook() {
    // Message webhook (has messages array)
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

    // Status update webhook (has statuses array)
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
                            "mime_type": "image/jpeg",
                            "sha256": "abc123",
                            "id": "media_id",
                            "url": "https://example.com/image.jpg"
                        }
                    }]
                }
            }]
        }]
    });

    let parsed = parse_whatsapp_webhook(payload).unwrap();
    assert_eq!(parsed.message_id, "wamid.example456");
    assert_eq!(parsed.sender, "1234567890");
    assert_eq!(parsed.message_type, "image");
    assert_eq!(parsed.content, Some("Check this out".to_string()));
    assert_eq!(parsed.media_url, Some("https://example.com/image.jpg".to_string()));
}

#[test]
fn test_parse_audio_message() {
    let payload = json!({
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "1234567890",
                        "id": "wamid.example789",
                        "timestamp": "1699999999",
                        "audio": {
                            "mime_type": "audio/mpeg",
                            "sha256": "def456",
                            "id": "audio_id",
                            "url": "https://example.com/audio.mp3"
                        }
                    }]
                }
            }]
        }]
    });

    let parsed = parse_whatsapp_webhook(payload).unwrap();
    assert_eq!(parsed.message_id, "wamid.example789");
    assert_eq!(parsed.sender, "1234567890");
    assert_eq!(parsed.message_type, "audio");
    assert_eq!(parsed.content, None);
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
                        "timestamp": "1699999999",
                        "document": {
                            "caption": "Important doc",
                            "filename": "report.pdf",
                            "mime_type": "application/pdf",
                            "sha256": "ghi789",
                            "id": "doc_id",
                            "url": "https://example.com/document.pdf"
                        }
                    }]
                }
            }]
        }]
    });

    let parsed = parse_whatsapp_webhook(payload).unwrap();
    assert_eq!(parsed.message_id, "wamid.example999");
    assert_eq!(parsed.sender, "1234567890");
    assert_eq!(parsed.message_type, "document");
    assert_eq!(parsed.content, Some("Important doc".to_string()));
    assert_eq!(parsed.media_url, Some("https://example.com/document.pdf".to_string()));
}

#[test]
fn test_parse_message_missing_fields() {
    let payload = json!({
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "1234567890"
                    }]
                }
            }]
        }]
    });

    assert!(parse_whatsapp_webhook(payload).is_err());
}

#[test]
fn test_parse_message_empty_entry() {
    let payload = json!({
        "entry": []
    });

    assert!(parse_whatsapp_webhook(payload).is_err());
}

#[test]
fn test_parse_message_no_changes() {
    let payload = json!({
        "entry": [{
            "changes": []
        }]
    });

    assert!(parse_whatsapp_webhook(payload).is_err());
}
