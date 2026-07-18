use std::sync::Arc;

use super::{InboundEventRepository, WhatsAppIngressConfig};

#[derive(Clone)]
pub struct WhatsAppIngressState {
    config: Option<Arc<WhatsAppIngressConfig>>,
    repository: Option<InboundEventRepository>,
}

impl WhatsAppIngressState {
    pub fn enabled(config: WhatsAppIngressConfig, repository: InboundEventRepository) -> Self {
        Self {
            config: Some(Arc::new(config)),
            repository: Some(repository),
        }
    }

    pub fn disabled() -> Self {
        Self {
            config: None,
            repository: None,
        }
    }

    pub fn config(&self) -> Option<&WhatsAppIngressConfig> {
        self.config.as_deref()
    }

    pub fn repository(&self) -> Option<&InboundEventRepository> {
        self.repository.as_ref()
    }
}
