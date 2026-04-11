//! Email end-to-end integration tests
//!
//! Tests cover:
//! - Webhook → parser → send flow
//! - Threading preservation (In-Reply-To, References)
//! - Attachment handling
//! - Multiple webhook providers (SendGrid, Mailgun, Postmark)
//!
//! NOTE: These tests require SQLx offline mode or DATABASE_URL to compile
//! Run with: SQLX_OFFLINE=true cargo test --test email_test

use mastermind_control_plane::channels::{
    parse_email_webhook, extract_message_id, extract_thread_id, is_email_webhook,
    EmailMessage, Attachment,
};
use serde_json::json;

#[test]
fn test_sendgrid_end_to_end_flow() {
    // Simulate incoming SendGrid webhook
    let webhook_payload = json!({
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

    // Step 1: Verify it's an email webhook
    assert!(is_email_webhook(&webhook_payload));

    // Step 2: Parse webhook into EmailMessage
    let parsed = parse_email_webhook(webhook_payload).unwrap();

    // Step 3: Verify parsed data
    assert_eq!(parsed.message_id, "12345@example.com");
    assert_eq!(parsed.from_email, "sender@example.com");
    assert_eq!(parsed.to_email, "recipient@example.com");
    assert_eq!(parsed.subject, "Test Email");
    assert_eq!(parsed.plain_text, Some("Plain text body".to_string()));
    assert_eq!(parsed.html_body, Some("<p>HTML body</p>".to_string()));

    // Step 4: Verify threading headers preserved
    assert_eq!(parsed.thread_id, Some("original@example.com".to_string()));

    // Step 5: Verify attachments
    assert_eq!(parsed.attachments.len(), 1);
    assert_eq!(parsed.attachments[0].filename, "test.pdf");
    assert_eq!(parsed.attachments[0].content_type, "application/pdf");
    assert_eq!(parsed.attachments[0].size, 1024);

    // Step 6: In real flow, worker would:
    // - Extract from_email, to_email, subject, plain_text, html_body from EmailMessage
    // - Call Python /api/channels/email/send endpoint
    // - Include thread_id, in_reply_to headers for threading
    // - Download attachment URLs to S3/local storage
    // - Update messages table status to 'sent'
}

#[test]
fn test_mailgun_end_to_end_flow() {
    // Simulate incoming Mailgun webhook
    let webhook_payload = json!({
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

    // Step 1: Verify it's an email webhook
    assert!(is_email_webhook(&webhook_payload));

    // Step 2: Parse webhook into EmailMessage
    let parsed = parse_email_webhook(webhook_payload).unwrap();

    // Step 3: Verify parsed data
    assert_eq!(parsed.message_id, "67890@example.com");
    assert_eq!(parsed.from_email, "sender@example.com");
    assert_eq!(parsed.to_email, "recipient@example.com");
    assert_eq!(parsed.subject, "Mailgun Test");
    assert_eq!(parsed.plain_text, Some("Plain text".to_string()));
    assert_eq!(parsed.html_body, Some("<p>HTML</p>".to_string()));

    // Step 4: Verify attachments
    assert_eq!(parsed.attachments.len(), 1);
    assert_eq!(parsed.attachments[0].filename, "doc.pdf");
}

#[test]
fn test_postmark_end_to_end_flow() {
    // Simulate incoming Postmark webhook
    let webhook_payload = json!({
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

    // Step 1: Verify it's an email webhook
    assert!(is_email_webhook(&webhook_payload));

    // Step 2: Parse webhook into EmailMessage
    let parsed = parse_email_webhook(webhook_payload).unwrap();

    // Step 3: Verify parsed data
    assert_eq!(parsed.message_id, "ABCDE@example.com");
    assert_eq!(parsed.from_email, "sender@example.com");
    assert_eq!(parsed.to_email, "recipient@example.com");
    assert_eq!(parsed.subject, "Postmark Test");
    assert_eq!(parsed.plain_text, Some("Plain text".to_string()));
    assert_eq!(parsed.html_body, Some("<p>HTML</p>".to_string()));

    // Step 4: Verify attachments
    assert_eq!(parsed.attachments.len(), 1);
    assert_eq!(parsed.attachments[0].filename, "file.pdf");
}

#[test]
fn test_email_threading_preservation() {
    // Simulate email reply with threading headers
    let webhook_payload = json!({
        "events": [{
            "sg_message_id": "reply123@example.com",
            "email": "sender@example.com",
            "to": "recipient@example.com",
            "subject": "Re: Original Thread",
            "text": "This is a reply",
            "timestamp": 1234567890,
            "headers": {
                "references": "<original@example.com> <parent@example.com>",
                "in-reply-to": "<parent@example.com>"
            }
        }]
    });

    // Parse webhook
    let parsed = parse_email_webhook(webhook_payload).unwrap();

    // Verify thread_id extracted from References header
    assert_eq!(parsed.thread_id, Some("original@example.com".to_string()));

    // Verify extract_thread_id function works
    let thread_id = extract_thread_id(webhook_payload).unwrap();
    assert_eq!(thread_id, "original@example.com");

    // In real flow, worker would:
    // - Pass thread_id to Python /api/channels/email/send
    // - Python would set References and In-Reply-To headers
    // - Frontend would group emails by thread_id in conversation view
}

#[test]
fn test_email_with_multiple_attachments() {
    // Simulate email with multiple attachments
    let webhook_payload = json!({
        "events": [{
            "sg_message_id": "multi-att@example.com",
            "email": "sender@example.com",
            "to": "recipient@example.com",
            "subject": "Multiple Attachments",
            "text": "See attached files",
            "attachments": [
                {
                    "filename": "document.pdf",
                    "type": "application/pdf",
                    "size": 1024,
                    "url": "https://example.com/doc.pdf"
                },
                {
                    "filename": "image.jpg",
                    "type": "image/jpeg",
                    "size": 2048,
                    "url": "https://example.com/image.jpg"
                },
                {
                    "filename": "data.csv",
                    "type": "text/csv",
                    "size": 512,
                    "url": "https://example.com/data.csv"
                }
            ]
        }]
    });

    // Parse webhook
    let parsed = parse_email_webhook(webhook_payload).unwrap();

    // Verify all attachments extracted
    assert_eq!(parsed.attachments.len(), 3);
    assert_eq!(parsed.attachments[0].filename, "document.pdf");
    assert_eq!(parsed.attachments[1].filename, "image.jpg");
    assert_eq!(parsed.attachments[2].filename, "data.csv");

    // In real flow, worker would:
    // - Download all attachment URLs to S3/local storage
    // - Store S3 paths in messages.attachments column
    // - Pass attachment metadata to frontend for display
}

#[test]
fn test_extract_message_id_from_multiple_providers() {
    // Test SendGrid
    let sendgrid = json!({
        "events": [{"sg_message_id": "sg@example.com"}]
    });
    assert_eq!(extract_message_id(sendgrid).unwrap(), "sg@example.com");

    // Test Mailgun
    let mailgun = json!({
        "event-data": {
            "message": {
                "headers": {"message-id": "mg@example.com"}
            }
        }
    });
    assert_eq!(extract_message_id(mailgun).unwrap(), "mg@example.com");

    // Test Postmark
    let postmark = json!({
        "MessageID": "pm@example.com"
    });
    assert_eq!(extract_message_id(postmark).unwrap(), "pm@example.com");
}

#[test]
fn test_html_email_without_plain_text() {
    // Simulate HTML-only email
    let webhook_payload = json!({
        "MessageID": "html-only@example.com",
        "From": "sender@example.com",
        "To": "recipient@example.com",
        "Subject": "HTML Only",
        "HtmlBody": "<h1>HTML Email</h1><p>No plain text</p>",
        "Timestamp": "2023-01-01T00:00:00Z"
    });

    // Parse webhook
    let parsed = parse_email_webhook(webhook_payload).unwrap();

    // Verify HTML body extracted
    assert_eq!(parsed.html_body, Some("<h1>HTML Email</h1><p>No plain text</p>".to_string()));
    assert!(parsed.plain_text.is_none());

    // In real flow, Python sender would:
    // - Set HTML content as primary body
    // - Frontend would render HTML (sanitized with DOMPurify)
}
