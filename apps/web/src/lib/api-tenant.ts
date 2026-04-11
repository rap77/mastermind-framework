/**
 * Tenant-Aware API Client Functions
 *
 * **Purpose:** Centralized API calls with tenant isolation (X-Tenant-ID header)
 * **Context:** Phase 17-02 - Multi-tenant Company Switcher
 *
 * **Architecture:**
 * - All API requests include X-Tenant-ID header from companyStore
 * - Backend validates tenant_id against JWT tenants array (Brain #5 CRITICAL)
 * - Returns 403 if tenant_id not in user's accessible list
 *
 * **Security:**
 * - X-Tenant-ID header is spoofable without JWT claim binding
 * - Backend must validate tenant_id belongs to user (JWT sub claim)
 * - This is CRITICAL for multi-tenancy security
 */

import 'server-only'
import { cookies } from 'next/headers'

/**
 * Fetch wrapper with tenant isolation
 *
 * **CRITICAL:** All API requests must include X-Tenant-ID header
 * Backend validates tenant_id against JWT tenants array
 *
 * @param endpoint - API endpoint path (e.g., '/api/companies')
 * @param tenantId - Tenant ID from companyStore
 * @param options - Fetch options (method, body, etc.)
 * @returns Fetch response
 * @throws Error if fetch fails or returns non-OK status
 */
export async function fetchWithTenant(
  endpoint: string,
  tenantId: string,
  options: RequestInit = {}
): Promise<Response> {
  const apiUrl = process.env.AGENT_RUNTIME_URL || 'http://localhost:8001'
  const url = `${apiUrl}${endpoint}`

  // Get JWT token from httpOnly cookie
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // CRITICAL: Include X-Tenant-ID header for tenant isolation
  headers['X-Tenant-ID'] = tenantId

  const response = await fetch(url, {
    ...options,
    headers,
    next: { revalidate: 0 }, // Disable caching for tenant-specific data
  })

  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Unauthorized - Please login first')
    }
    if (response.status === 403) {
      const error = await response.json()
      throw new Error(`Tenant access denied: ${error.detail?.message || error.detail || 'Unknown error'}`)
    }
    throw new Error(`Request failed: ${response.status} ${response.statusText}`)
  }

  return response
}

/**
 * Fetch companies for current user
 *
 * **Tenant isolation:** Returns only companies from user's tenant list
 *
 * @param tenantId - Active tenant ID
 * @returns Array of companies
 */
export async function fetchCompanies(tenantId: string) {
  const response = await fetchWithTenant('/api/companies', tenantId, {
    method: 'GET',
  })

  const data = await response.json()
  return data
}

/**
 * Fetch company status for UI indicators
 *
 * **Tenant isolation:** Returns status only if tenant is accessible
 *
 * @param companyId - Company ID
 * @param tenantId - Active tenant ID
 * @returns Company status (live_agents_count, unread_count)
 */
export async function fetchCompanyStatus(companyId: string, tenantId: string) {
  const response = await fetchWithTenant(`/api/companies/${companyId}/status`, tenantId, {
    method: 'GET',
  })

  const data = await response.json()
  return data
}

/**
 * Create a new company
 *
 * **Tenant isolation:** Company is created within user's tenant context
 *
 * @param companyData - Company creation data
 * @param tenantId - Active tenant ID
 * @returns Created company
 */
export async function createCompany(
  companyData: { name: string; slug: string; icon?: string | null },
  tenantId: string
) {
  const response = await fetchWithTenant('/api/companies', tenantId, {
    method: 'POST',
    body: JSON.stringify(companyData),
  })

  const data = await response.json()
  return data
}

/**
 * Update a company
 *
 * **Tenant isolation:** Only updates company if it belongs to user's tenant
 *
 * @param companyId - Company ID
 * @param companyData - Company update data
 * @param tenantId - Active tenant ID
 * @returns Updated company
 */
export async function updateCompany(
  companyId: string,
  companyData: { name?: string; icon?: string | null },
  tenantId: string
) {
  const response = await fetchWithTenant(`/api/companies/${companyId}`, tenantId, {
    method: 'PUT',
    body: JSON.stringify(companyData),
  })

  const data = await response.json()
  return data
}
