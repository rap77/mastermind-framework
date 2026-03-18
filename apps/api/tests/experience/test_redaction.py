"""PII redaction tests."""

from pydantic import SecretStr
from mastermind_cli.experience.redaction import (
    redact_pii,
    redact_dict,
    redact_for_storage,
)


def test_redact_api_keys():
    """Test 1: API keys redacted (sk-, mmsk_ patterns → [REDACTED_SECRET])."""
    # OpenAI key
    assert redact_pii("My key is sk-abc123def456") == "My key is [REDACTED_SECRET]"
    # MultiOn key
    assert redact_pii("Token: mmsk_xyz789abc123") == "Token: [REDACTED_SECRET]"
    # Multiple keys in one string (longer keys to match {10,} pattern)
    text = "sk-key123456789 and mmsk_key789012345"
    assert redact_pii(text) == "[REDACTED_SECRET] and [REDACTED_SECRET]"


def test_redact_emails():
    """Test 2: Emails redacted (user@example.com → [REDACTED_EMAIL])."""
    assert (
        redact_pii("Contact me at user@example.com") == "Contact me at [REDACTED_EMAIL]"
    )
    assert (
        redact_pii("Emails: admin@test.co and user@test.co.uk")
        == "Emails: [REDACTED_EMAIL] and [REDACTED_EMAIL]"
    )


def test_redact_ssn():
    """Test 3: SSN/DNI redacted (123-45-6789 → [REDACTED_SSN])."""
    assert redact_pii("SSN: 123-45-6789") == "SSN: [REDACTED_SSN]"
    assert (
        redact_pii("DNI: 987-65-4321 and 555-44-3333")
        == "DNI: [REDACTED_SSN] and [REDACTED_SSN]"
    )


def test_redact_nested_dicts():
    """Test 4: Recursive redaction in nested dicts."""
    data = {
        "user": "john@example.com",
        "api_key": "sk-secret123456",
        "profile": {
            "email": "jane@test.org",
            "ssn": "111-22-3333",
            "nested": {"token": "mmsk_token45678"},
        },
        "safe": "normal text",
    }
    redacted = redact_dict(data)
    assert redacted["user"] == "[REDACTED_EMAIL]"
    assert redacted["api_key"] == "[REDACTED_SECRET]"
    assert redacted["profile"]["email"] == "[REDACTED_EMAIL]"
    assert redacted["profile"]["ssn"] == "[REDACTED_SSN]"
    assert redacted["profile"]["nested"]["token"] == "[REDACTED_SECRET]"
    assert redacted["safe"] == "normal text"


def test_redact_list_of_dicts():
    """Test 5: Redaction works on lists containing dicts."""
    data = {
        "users": [
            {"email": "user1@example.com", "name": "User 1"},
            {"email": "user2@example.com", "name": "User 2"},
        ]
    }
    redacted = redact_dict(data)
    assert redacted["users"][0]["email"] == "[REDACTED_EMAIL]"
    assert redacted["users"][0]["name"] == "User 1"
    assert redacted["users"][1]["email"] == "[REDACTED_EMAIL]"


def test_redact_pydantic_secret_str():
    """Test 6: Pydantic SecretStr fields auto-redacted via model_dump(exclude_defaults=True)."""

    class TestModel:
        def __init__(self):
            self.password = SecretStr("sk-secret123456")
            self.email = "test@example.com"

        def model_dump(self, exclude_defaults=True, mode="json"):
            # SecretStr.get_secret_value() exposes the secret
            # In real Pydantic models, exclude_defaults would handle this
            return {"password": self.password.get_secret_value(), "email": self.email}

    obj = TestModel()
    result = redact_for_storage(obj)
    # Should redact both the password (exposed then regexed) and email (via regex)
    assert "[REDACTED_SECRET]" in result
    assert "[REDACTED_EMAIL]" in result
    # Secrets should not appear in output
    assert "sk-secret123456" not in result
    assert "test@example.com" not in result


def test_redact_for_storage_dict():
    """Test 7: redact_for_storage() handles dict input."""
    data = {"key": "sk-abc123456789", "email": "user@test.com"}
    result = redact_for_storage(data)
    # Returns JSON string
    assert isinstance(result, str)
    assert "[REDACTED_SECRET]" in result
    assert "[REDACTED_EMAIL]" in result


def test_redact_for_storage_string():
    """Test 8: redact_for_storage() handles string input."""
    result = redact_for_storage("Contact: user@example.com")
    assert isinstance(result, str)
    # String input is redacted but returned as JSON string
    assert "[REDACTED_EMAIL]" in result


def test_redact_preserves_non_pii():
    """Test 9: Non-PII data is preserved."""
    data = {
        "message": "Hello world",
        "count": 42,
        "active": True,
        "items": ["a", "b", "c"],
    }
    redacted = redact_dict(data)
    assert redacted["message"] == "Hello world"
    assert redacted["count"] == 42
    assert redacted["active"] is True
    assert redacted["items"] == ["a", "b", "c"]


def test_redact_circular_reference():
    """Test 10: Circular references handled gracefully."""
    data = {"key": "value"}
    data["self"] = data  # Circular reference
    # Should not crash
    redacted = redact_dict(data)
    assert "key" in redacted
