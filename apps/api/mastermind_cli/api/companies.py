"""
Companies API Router with Tenant Isolation.

This module provides API endpoints for managing companies (tenants).
All endpoints enforce tenant isolation via JWT validation.

Brain #5 Requirement: All endpoints must return 403 if X-Tenant-ID not in JWT tenants array.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from mastermind_cli.auth.jwt_handler import (
    JWTTokenData,
    TenantValidationResult,
    validate_tenant_access,
)

# ===== ROUTER =====

router = APIRouter(prefix="/api/companies", tags=["companies"])

# ===== MODELS =====


class Company(BaseModel):
    """Company model."""

    id: str = Field(..., description="Company ID")
    name: str = Field(..., min_length=1, max_length=100, description="Company name")
    slug: str = Field(..., min_length=1, max_length=50, description="URL-friendly slug")
    icon: str | None = Field(None, description="Company logo URL")
    status: str = Field(default="active", description="Company status")


class CompanyCreate(BaseModel):
    """Input model for creating a company."""

    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=50)
    icon: str | None = None


class CompanyUpdate(BaseModel):
    """Input model for updating a company."""

    name: str | None = Field(None, min_length=1, max_length=100)
    icon: str | None = None


class CompanyStatus(BaseModel):
    """Company status for UI indicators."""

    id: str
    status: str  # "active", "inactive", "error"
    live_agents_count: int = 0
    unread_count: int = 0


# ===== MOCK DATABASE =====
# TODO: Replace with actual database queries in Phase 18

_MOCK_COMPANIES: dict[str, list[Company]] = {
    "user@example.com": [
        Company(
            id="company-1",
            name="Acme Corporation",
            slug="acme-corp",
            icon=None,
            status="active",
        ),
        Company(
            id="company-2",
            name="Globex Inc",
            slug="globex-inc",
            icon=None,
            status="active",
        ),
    ]
}


# ===== ENDPOINTS =====


@router.get("", response_model=list[Company])
async def list_companies(
    current_user: JWTTokenData = Depends(validate_tenant_access),
) -> list[Company]:
    """
    List all companies for the current user.

    Tenant isolation: Returns only companies from user's tenant list.
    """
    # TODO: Replace with database query
    # For now, return mock data based on user's tenant memberships
    return _MOCK_COMPANIES.get(current_user.sub, [])


@router.get("/{company_id}", response_model=Company)
async def get_company(
    company_id: str,
    tenant: TenantValidationResult = Depends(validate_tenant_access),
) -> Company:
    """
    Get a specific company by ID.

    Tenant isolation: Only returns company if it belongs to user's tenant.
    """
    # TODO: Replace with database query
    user_companies = _MOCK_COMPANIES.get(tenant.user_id or "", [])
    company = next((c for c in user_companies if c.id == company_id), None)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    return company


@router.post("", response_model=Company, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user: JWTTokenData = Depends(validate_tenant_access),
) -> Company:
    """
    Create a new company.

    Tenant isolation: Company is created within user's tenant context.
    """
    # TODO: Replace with database insert
    new_company = Company(
        id=f"company-{len(_MOCK_COMPANIES.get(current_user.sub, [])) + 1}",
        name=company_data.name,
        slug=company_data.slug,
        icon=company_data.icon,
        status="active",
    )

    if current_user.sub not in _MOCK_COMPANIES:
        _MOCK_COMPANIES[current_user.sub] = []

    _MOCK_COMPANIES[current_user.sub].append(new_company)
    return new_company


@router.put("/{company_id}", response_model=Company)
async def update_company(
    company_id: str,
    company_data: CompanyUpdate,
    tenant: TenantValidationResult = Depends(validate_tenant_access),
) -> Company:
    """
    Update a company.

    Tenant isolation: Only updates company if it belongs to user's tenant.
    """
    # TODO: Replace with database update
    user_companies = _MOCK_COMPANIES.get(tenant.user_id or "", [])
    company = next((c for c in user_companies if c.id == company_id), None)

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    if company_data.name:
        company.name = company_data.name
    if company_data.icon:
        company.icon = company_data.icon

    return company


@router.get("/{company_id}/status", response_model=CompanyStatus)
async def get_company_status(
    company_id: str,
    tenant: TenantValidationResult = Depends(validate_tenant_access),
) -> CompanyStatus:
    """
    Get company status for UI indicators.

    Returns live agent count and unread count for status badges.
    """
    # TODO: Replace with actual data from brain_runs and inbox tables
    return CompanyStatus(
        id=company_id,
        status="active",
        live_agents_count=3,  # Mock data
        unread_count=5,  # Mock data
    )


# ===== EXPORTS =====

__all__ = ["router"]
