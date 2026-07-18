use std::env;

use thiserror::Error;

const ENABLED_KEY: &str = "WHATSAPP_CANONICAL_INGEST_ENABLED";
const VERIFY_TOKEN_KEY: &str = "WHATSAPP_VERIFY_TOKEN";
const APP_SECRET_KEY: &str = "WHATSAPP_APP_SECRET";
const PHONE_NUMBER_ID_KEY: &str = "WHATSAPP_PHONE_NUMBER_ID";
const RETENTION_DAYS_KEY: &str = "MESSAGING_RETENTION_DAYS";

#[derive(Clone, Eq, PartialEq)]
pub struct WhatsAppIngressConfig {
    pub verify_token: String,
    pub app_secret: String,
    pub phone_number_id: String,
    pub retention_days: u32,
}

#[derive(Debug, Error, Eq, PartialEq)]
pub enum WhatsAppIngressConfigError {
    #[error("{ENABLED_KEY} must be true or false")]
    InvalidFeatureFlag,
    #[error("required environment variable {0} is missing or empty")]
    MissingValue(&'static str),
    #[error("{RETENTION_DAYS_KEY} must be a positive integer")]
    InvalidRetentionDays,
    #[error("{VERIFY_TOKEN_KEY} and {APP_SECRET_KEY} must be distinct")]
    SecretsMustDiffer,
}

impl WhatsAppIngressConfig {
    pub fn from_env() -> Result<Option<Self>, WhatsAppIngressConfigError> {
        Self::from_lookup(|key| env::var(key).ok())
    }

    fn from_lookup(
        mut lookup: impl FnMut(&str) -> Option<String>,
    ) -> Result<Option<Self>, WhatsAppIngressConfigError> {
        match lookup(ENABLED_KEY).as_deref().map(str::trim) {
            None | Some("") | Some("false") => return Ok(None),
            Some("true") => {}
            Some(_) => return Err(WhatsAppIngressConfigError::InvalidFeatureFlag),
        }

        let verify_token = required_value(&mut lookup, VERIFY_TOKEN_KEY)?;
        let app_secret = required_value(&mut lookup, APP_SECRET_KEY)?;
        let phone_number_id = required_value(&mut lookup, PHONE_NUMBER_ID_KEY)?;
        let retention_days = required_value(&mut lookup, RETENTION_DAYS_KEY)?
            .parse::<u32>()
            .ok()
            .filter(|days| *days > 0)
            .ok_or(WhatsAppIngressConfigError::InvalidRetentionDays)?;
        if chrono::Utc::now()
            .checked_add_days(chrono::Days::new(retention_days.into()))
            .is_none()
        {
            return Err(WhatsAppIngressConfigError::InvalidRetentionDays);
        }

        if verify_token == app_secret {
            return Err(WhatsAppIngressConfigError::SecretsMustDiffer);
        }

        Ok(Some(Self {
            verify_token,
            app_secret,
            phone_number_id,
            retention_days,
        }))
    }
}

fn required_value(
    lookup: &mut impl FnMut(&str) -> Option<String>,
    key: &'static str,
) -> Result<String, WhatsAppIngressConfigError> {
    lookup(key)
        .filter(|value| !value.trim().is_empty())
        .ok_or(WhatsAppIngressConfigError::MissingValue(key))
}

#[cfg(test)]
mod tests {
    use std::collections::HashMap;

    use super::*;

    fn load(
        values: &[(&str, &str)],
    ) -> Result<Option<WhatsAppIngressConfig>, WhatsAppIngressConfigError> {
        let values: HashMap<_, _> = values
            .iter()
            .map(|(key, value)| ((*key).to_owned(), (*value).to_owned()))
            .collect();
        WhatsAppIngressConfig::from_lookup(|key| values.get(key).cloned())
    }

    fn enabled_values() -> Vec<(&'static str, &'static str)> {
        vec![
            (ENABLED_KEY, "true"),
            (VERIFY_TOKEN_KEY, "verify-token"),
            (APP_SECRET_KEY, "app-secret"),
            (PHONE_NUMBER_ID_KEY, "phone-number-id"),
            (RETENTION_DAYS_KEY, "30"),
        ]
    }

    #[test]
    fn whatsapp_ingress_config_is_disabled_by_default() {
        assert!(load(&[]).unwrap().is_none());
        assert!(load(&[(ENABLED_KEY, "false")]).unwrap().is_none());
    }

    #[test]
    fn whatsapp_ingress_config_loads_enabled_values() {
        let config = load(&enabled_values()).unwrap().unwrap();

        assert_eq!(config.verify_token, "verify-token");
        assert_eq!(config.app_secret, "app-secret");
        assert_eq!(config.phone_number_id, "phone-number-id");
        assert_eq!(config.retention_days, 30);
    }

    #[test]
    fn whatsapp_ingress_config_rejects_missing_enabled_value() {
        let mut values = enabled_values();
        values.retain(|(key, _)| *key != PHONE_NUMBER_ID_KEY);

        assert!(matches!(
            load(&values),
            Err(WhatsAppIngressConfigError::MissingValue(
                PHONE_NUMBER_ID_KEY
            ))
        ));
    }

    #[test]
    fn whatsapp_ingress_config_rejects_invalid_retention() {
        for value in ["0", "-1", "not-a-number"] {
            let mut values = enabled_values();
            values.retain(|(key, _)| *key != RETENTION_DAYS_KEY);
            values.push((RETENTION_DAYS_KEY, value));

            assert!(matches!(
                load(&values),
                Err(WhatsAppIngressConfigError::InvalidRetentionDays)
            ));
        }
    }

    #[test]
    fn whatsapp_ingress_config_rejects_unrepresentable_retention() {
        let mut values = enabled_values();
        values.retain(|(key, _)| *key != RETENTION_DAYS_KEY);
        values.push((RETENTION_DAYS_KEY, "4294967295"));

        assert!(matches!(
            load(&values),
            Err(WhatsAppIngressConfigError::InvalidRetentionDays)
        ));
    }

    #[test]
    fn whatsapp_ingress_config_rejects_equal_secrets() {
        let mut values = enabled_values();
        values.retain(|(key, _)| *key != APP_SECRET_KEY);
        values.push((APP_SECRET_KEY, "verify-token"));

        assert!(matches!(
            load(&values),
            Err(WhatsAppIngressConfigError::SecretsMustDiffer)
        ));
    }

    #[test]
    fn whatsapp_ingress_config_rejects_unknown_flag_value() {
        assert!(matches!(
            load(&[(ENABLED_KEY, "yes")]),
            Err(WhatsAppIngressConfigError::InvalidFeatureFlag)
        ));
    }
}
