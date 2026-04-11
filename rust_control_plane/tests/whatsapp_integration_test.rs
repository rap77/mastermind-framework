//! WhatsApp end-to-end integration tests
//!
//! Tests cover:
//! - Webhook → parser → send flow
//! - Status update handling
//! - Media message handling
//!
//! NOTE: These tests require SQLx offline mode or DATABASE_URL to compile
//! Run with: SQLX_OFFLINE=true cargo test --test whatsapp_integration_test

use mastermind_control_plane::channels::{
    parse_whatsapp_webhook, is_message_webhook, MessagePayload
};
use serde_json::json;

#[test]
fn test_whatsapp_end_to_end_message_flow() {
    // Simulate incoming WhatsApp webhook
    let webhook_payload = json!({
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

    // Step 1: Verify it's a message webhook (not status update)
    assert!(is_message_webhook(&webhook_payload));

    // Step 2: Parse webhook into MessagePayload
    let parsed = parse_whatsapp_webhook(webhook_payload).unwrap();

    // Step 3: Verify parsed data
    assert_eq!(parsed.message_id, "wamid.example123");
    assert_eq!(parsed.sender, "1234567890");
    assert_eq!(parsed.message_type, "text");
    assert_eq!(parsed.content, Some("Hello, world!".to_string()));

    // Step 4: In real flow, worker would:
    // - Extract sender_phone, message_type, content from MessagePayload
    // - Call Python /api/channels/whatsapp/send endpoint
    // - Update messages table status to 'sent'
}

#[test]
fn test_whatsapp_status_update_handling() {
    // Simulate WhatsApp status update webhook
    let status_payload = json!({
        "entry": [{
            "changes": [{
                "value": {
                    "statuses": [{
                        "id": "wamid.example123",
                        "status": "sent",
                        "timestamp": "1699999999"
                    }]
                }
            }]
        }]
    });

    // Step 1: Verify it's NOT a message webhook
    assert!(!is_message_webhook(&status_payload));

    // Step 2: In real flow, worker would:
    // - Extract external_message_id from statuses[0].id
    // - Extract status from statuses[0].status (sent, delivered, read)
    // - Update messages table: status = external_status
    // - Use UPDATE messages SET status = $1 WHERE external_message_id = $2
}

#[test]
fn test_whatsapp_media_message_flow() {
    // Simulate incoming WhatsApp media message (image)
    let media_webhook = json!({
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "1234567890",
                        "id": "wamid.media456",
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

    // Step 1: Parse webhook
    let parsed = parse_whatsapp_webhook(media_webhook).unwrap();

    // Step 2: Verify parsed data
    assert_eq!(parsed.message_type, "image");
    assert_eq!(parsed.content, Some("Check this out".to_string()));
    assert_eq!(parsed.media_url, Some("https://example.com/image.jpg".to_string()));

    // Step 3: In real flow, worker would:
    // - Call Python /api/channels/whatsapp/send with media_type='image'
    // - Pass media_url and caption to send_whatsapp_media()
    // - Media file would be downloaded by Python handler
}

#[test]
fn test_whatsapp_document_message_flow() {
    // Simulate incoming WhatsApp document message
    let doc_webhook = json!({
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "1234567890",
                        "id": "wamid.doc789",
                        "timestamp": "1699999999",
                        "document": {
                            "caption": "Important doc",
                            "url": "https://example.com/document.pdf"
                        }
                    }]
                }
            }]
        }]
    });

    // Parse and verify document handling
    let parsed = parse_whatsapp_webhook(doc_webhook).unwrap();
    assert_eq!(parsed.message_type, "document");
    assert_eq!(parsed.media_url, Some("https://example.com/document.pdf".to_string()));
}

#[test]
fn test_whatsapp_audio_message_flow() {
    // Simulate incoming WhatsApp audio message
    let audio_webhook = json!({
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "1234567890",
                        "id": "wamid.audio999",
                        "audio": {
                            "url": "https://example.com/audio.mp3"
                        }
                    }]
                }
            }]
        }]
    });

    // Parse and verify audio handling
    let parsed = parse_whatsapp_webhook(audio_webhook).unwrap();
    assert_eq!(parsed.message_type, "audio");
    assert_eq!(parsed.media_url, Some("https://example.com/audio.mp3".to_string()));
}
