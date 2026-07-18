use rust_control_plane::messaging::{CanonicalChannel, CanonicalInboundEventV1};
use serde::Deserialize;
use serde_json::Value;

const VALID_FIXTURE: &str =
    include_str!("../../docs/contracts/messaging/fixtures/canonical-inbound-event-v1.valid.json");
const INVALID_FIXTURES: &str =
    include_str!("../../docs/contracts/messaging/fixtures/canonical-inbound-event-v1.invalid.json");

#[derive(Deserialize)]
struct InvalidFixture {
    name: String,
    event: Value,
}

#[test]
fn canonical_event_contract_accepts_shared_valid_fixture() {
    let event: CanonicalInboundEventV1 =
        serde_json::from_str(VALID_FIXTURE).expect("shared valid fixture must deserialize");
    let expected_wire_shape: Value =
        serde_json::from_str(VALID_FIXTURE).expect("shared valid fixture must be JSON");

    assert_eq!(event.channel, CanonicalChannel::WhatsApp);
    assert_eq!(
        serde_json::to_value(&event).expect("canonical event must serialize"),
        expected_wire_shape
    );
    assert_eq!(
        event.idempotency_key(),
        "whatsapp:test-phone-number-id:wamid.test-message-001"
    );
}

#[test]
fn canonical_event_contract_rejects_shared_invalid_fixtures() {
    let cases: Vec<InvalidFixture> =
        serde_json::from_str(INVALID_FIXTURES).expect("invalid fixture list must deserialize");

    for case in cases {
        assert!(
            serde_json::from_value::<CanonicalInboundEventV1>(case.event).is_err(),
            "fixture {} unexpectedly deserialized",
            case.name
        );
    }
}
