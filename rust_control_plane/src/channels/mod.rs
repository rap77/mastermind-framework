//! Channel-specific webhook parsers
//!
//! Each channel (WhatsApp, Instagram, Email) has its own webhook format.
//! This module provides parsers that normalize webhooks into a common MessagePayload struct.

pub mod email;
pub mod whatsapp;
pub mod instagram;

pub use email::{
    Attachment, EmailMessage, extract_message_id as extract_email_message_id,
    extract_thread_id, is_email_webhook, parse_email_webhook,
};
pub use whatsapp::{MessagePayload, parse_whatsapp_webhook, extract_message_id, extract_sender_phone, is_message_webhook};
pub use instagram::{InstagramComment, parse_instagram_webhook, extract_comment_id, extract_media_url, is_comment_webhook};
