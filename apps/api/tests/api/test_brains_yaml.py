"""Tests for GET /api/brains/{id}/yaml endpoint.

Requirements: ER-03 (Engine Room — brain YAML config display)
"""

import yaml
import pytest


@pytest.mark.asyncio
async def test_get_brain_yaml_valid_id(client, auth_headers) -> None:
    """GET /api/brains/brain-01/yaml returns valid YAML for brain 1."""
    response = await client.get("/api/brains/brain-01/yaml", headers=auth_headers)
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

    # Content should be valid YAML
    content = response.text
    parsed = yaml.safe_load(content)
    assert parsed is not None
    assert isinstance(parsed, dict)


@pytest.mark.asyncio
async def test_get_brain_yaml_contains_required_fields(client, auth_headers) -> None:
    """Brain YAML includes required fields: brain_id, name, niche, version."""
    response = await client.get("/api/brains/brain-01/yaml", headers=auth_headers)
    assert response.status_code == 200

    parsed = yaml.safe_load(response.text)
    assert "brain_id" in parsed
    assert "name" in parsed
    assert "niche" in parsed
    assert "version" in parsed


@pytest.mark.asyncio
async def test_get_brain_yaml_starts_with_document_marker(client, auth_headers) -> None:
    """Brain YAML starts with --- document marker."""
    response = await client.get("/api/brains/brain-01/yaml", headers=auth_headers)
    assert response.status_code == 200
    assert response.text.startswith("---")


@pytest.mark.asyncio
async def test_get_brain_yaml_content_type_plain(client, auth_headers) -> None:
    """Response Content-Type is text/plain."""
    response = await client.get("/api/brains/brain-01/yaml", headers=auth_headers)
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")


@pytest.mark.asyncio
async def test_get_brain_yaml_numeric_id(client, auth_headers) -> None:
    """GET /api/brains/1/yaml also works (numeric ID format)."""
    response = await client.get("/api/brains/1/yaml", headers=auth_headers)
    assert response.status_code == 200
    parsed = yaml.safe_load(response.text)
    assert parsed["brain_id"] == "brain-01"


@pytest.mark.asyncio
async def test_get_brain_yaml_not_found(client, auth_headers) -> None:
    """GET /api/brains/brain-99/yaml returns 404 for nonexistent brain."""
    response = await client.get("/api/brains/brain-99/yaml", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_brain_yaml_invalid_id(client, auth_headers) -> None:
    """GET /api/brains/invalid/yaml returns 404 for non-numeric brain ID."""
    response = await client.get(
        "/api/brains/invalid-brain-name/yaml", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_brain_yaml_auth_required(client) -> None:
    """GET /api/brains/{id}/yaml requires JWT authentication."""
    response = await client.get("/api/brains/brain-01/yaml")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_brain_yaml_brain_id_format(client, auth_headers) -> None:
    """brain_id in YAML uses 'brain-XX' format (zero-padded)."""
    response = await client.get("/api/brains/brain-01/yaml", headers=auth_headers)
    assert response.status_code == 200
    parsed = yaml.safe_load(response.text)
    # brain_id should be in "brain-01" format
    assert parsed["brain_id"].startswith("brain-")
