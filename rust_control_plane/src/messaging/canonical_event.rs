use chrono::{DateTime, Utc};
use serde::{de, Deserialize, Deserializer, Serialize};
use uuid::Uuid;

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum CanonicalSchemaVersion {
    #[serde(rename = "messaging.inbound.v1")]
    V1,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum CanonicalChannel {
    #[serde(rename = "whatsapp")]
    WhatsApp,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum CanonicalDirection {
    #[serde(rename = "inbound")]
    Inbound,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum CanonicalMessageType {
    #[serde(rename = "text")]
    Text,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq, Serialize, Deserialize)]
pub enum CanonicalProcessingStatus {
    #[serde(rename = "accepted")]
    Accepted,
}

#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct CanonicalInboundEventV1 {
    pub schema_version: CanonicalSchemaVersion,
    pub event_id: Uuid,
    pub channel: CanonicalChannel,
    #[serde(deserialize_with = "deserialize_non_empty")]
    pub account_external_id: String,
    #[serde(deserialize_with = "deserialize_non_empty")]
    pub external_message_id: String,
    pub direction: CanonicalDirection,
    #[serde(deserialize_with = "deserialize_non_empty")]
    pub sender_external_id: String,
    #[serde(deserialize_with = "deserialize_non_empty")]
    pub recipient_external_id: String,
    pub message_type: CanonicalMessageType,
    #[serde(deserialize_with = "deserialize_content_text")]
    pub content_text: String,
    pub occurred_at: DateTime<Utc>,
    pub received_at: DateTime<Utc>,
    #[serde(deserialize_with = "deserialize_sha256")]
    pub payload_sha256: String,
    pub processing_status: CanonicalProcessingStatus,
    pub retention_expires_at: DateTime<Utc>,
}

impl CanonicalInboundEventV1 {
    pub fn idempotency_key(&self) -> String {
        format!(
            "whatsapp:{}:{}",
            self.account_external_id, self.external_message_id
        )
    }
}

fn deserialize_non_empty<'de, D>(deserializer: D) -> Result<String, D::Error>
where
    D: Deserializer<'de>,
{
    let value = String::deserialize(deserializer)?;
    if value.is_empty() {
        return Err(de::Error::custom("value must not be empty"));
    }
    Ok(value)
}

fn deserialize_content_text<'de, D>(deserializer: D) -> Result<String, D::Error>
where
    D: Deserializer<'de>,
{
    let value = String::deserialize(deserializer)?;
    let length = value.chars().count();
    if !(1..=4096).contains(&length) {
        return Err(de::Error::custom(
            "content_text must contain between 1 and 4096 characters",
        ));
    }
    Ok(value)
}

fn deserialize_sha256<'de, D>(deserializer: D) -> Result<String, D::Error>
where
    D: Deserializer<'de>,
{
    let value = String::deserialize(deserializer)?;
    if value.len() != 64
        || !value
            .bytes()
            .all(|byte| byte.is_ascii_digit() || (b'a'..=b'f').contains(&byte))
    {
        return Err(de::Error::custom(
            "payload_sha256 must contain 64 lowercase hexadecimal characters",
        ));
    }
    Ok(value)
}
