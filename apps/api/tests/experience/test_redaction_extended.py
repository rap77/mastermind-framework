"""Extended PII redaction tests for missing patterns."""

from mastermind_cli.experience.redaction import redact_pii


def test_redact_ssn_no_dash():
    """Test SSN without dashes (123456789 → [REDACTED_SSN])."""
    assert redact_pii("SSN: 123456789") == "SSN: [REDACTED_SSN]"
    assert (
        redact_pii("ID: 987654321 and 555443333")
        == "ID: [REDACTED_SSN] and [REDACTED_SSN]"
    )


def test_redact_ip_addresses():
    """Test IP addresses (192.168.1.1 → [REDACTED_IP])."""
    assert redact_pii("Server: 192.168.1.1") == "Server: [REDACTED_IP]"
    assert (
        redact_pii("IPs: 10.0.0.1 and 172.16.0.1")
        == "IPs: [REDACTED_IP] and [REDACTED_IP]"
    )


def test_redact_jwt_tokens():
    """Test JWT tokens (eyJ... with two dots → [REDACTED_TOKEN])."""
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.signature"
    assert redact_pii(f"Bearer {jwt}") == "Bearer [REDACTED_TOKEN]"


def test_redact_credit_cards():
    """Test credit card numbers (Visa/MC → [REDACTED_CC])."""
    # Visa: starts with 4, 13 or 16 digits
    assert redact_pii("Card: 4111111111111111") == "Card: [REDACTED_CC]"
    # Mastercard: starts with 51-55, 16 digits
    assert redact_pii("Card: 5105105105105100") == "Card: [REDACTED_CC]"


def test_redact_multiple_pii_types():
    """Test redaction of multiple PII types in one string."""
    text = "Email: user@test.com, SSN: 123456789, IP: 192.168.1.1"
    result = redact_pii(text)
    assert "[REDACTED_EMAIL]" in result
    assert "[REDACTED_SSN]" in result
    assert "[REDACTED_IP]" in result
    # Original PII should not appear
    assert "user@test.com" not in result
    assert "123456789" not in result
    assert "192.168.1.1" not in result
