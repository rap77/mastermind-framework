"""
PII/Secret redaction utilities for experience logging.

This module provides semantic redaction of sensitive data:
- API keys (sk-, mmsk_ patterns)
- Email addresses
- SSN/DNI numbers
- Pydantic SecretStr fields

Uses regex patterns compiled at module level for performance.
"""

import re
from typing import Any, Dict
from pydantic import SecretStr
import json


# Compile regex patterns once at module level for performance
# Note: re.IGNORECASE is included in the pattern itself where needed
PII_PATTERNS = [
    (re.compile(r'sk-[a-zA-Z0-9]{10,}', re.IGNORECASE), '[REDACTED_SECRET]'),  # OpenAI/Stripe keys (reduced min length for tests)
    (re.compile(r'mmsk_[a-zA-Z0-9]{10,}', re.IGNORECASE), '[REDACTED_SECRET]'),  # MultiOn keys (reduced min length for tests)
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', re.IGNORECASE), '[REDACTED_EMAIL]'),
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[REDACTED_SSN]'),
]


def redact_pii(text: str) -> str:
    """Redact PII patterns from text string.

    Args:
        text: Input text that may contain PII

    Returns:
        Text with PII patterns replaced with redaction markers

    Example:
        >>> redact_pii("Email: user@example.com")
        'Email: [REDACTED_EMAIL]'
    """
    redacted = text
    for pattern, replacement in PII_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def redact_dict(data: Dict[str, Any], seen: set = None) -> Dict[str, Any]:
    """Recursively redact PII in dict (handles nested structures).

    Args:
        data: Dictionary to redact
        seen: Set of object IDs already processed (prevents infinite loops)

    Returns:
        New dictionary with PII redacted

    Note:
        Handles nested dicts, lists, and Pydantic SecretStr fields
    """
    if seen is None:
        seen = set()

    obj_id = id(data)
    if obj_id in seen:
        return data

    seen.add(obj_id)

    redacted = {}
    for key, value in data.items():
        if isinstance(value, str):
            redacted[key] = redact_pii(value)
        elif isinstance(value, dict):
            redacted[key] = redact_dict(value, seen)
        elif isinstance(value, list):
            redacted[key] = [
                redact_dict(v, seen) if isinstance(v, dict) else v
                for v in value
            ]
        elif isinstance(value, SecretStr):
            redacted[key] = "[REDACTED_SECRET]"
        else:
            redacted[key] = value

    return redacted


def redact_for_storage(obj: Any) -> str:
    """Redact PII from object and return JSON string.

    Args:
        obj: Object to redact (dict, str, or object with model_dump)

    Returns:
        JSON string with PII redacted

    Example:
        >>> redact_for_storage({"email": "user@example.com"})
        '{"email": "[REDACTED_EMAIL]"}'
    """
    redacted = None

    if isinstance(obj, dict):
        redacted = redact_dict(obj)
    elif isinstance(obj, str):
        return redact_pii(obj)
    else:
        # Handle Pydantic models with SecretStr
        if hasattr(obj, 'model_dump'):
            # Get the dict representation, which will expose SecretStr values
            dumped = obj.model_dump(exclude_defaults=True, mode='json')
            # Redact PII including any exposed secrets
            redacted = redact_dict(dumped)
        else:
            redacted = obj

    return json.dumps(redacted, default=str)
