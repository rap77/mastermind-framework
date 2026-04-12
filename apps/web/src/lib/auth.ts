import 'server-only'

/**
 * Verifies a JWT token by calling the backend /api/auth/verify endpoint.
 *
 * This avoids library incompatibility between python-jose (backend) and jose (frontend).
 * The backend uses python-jose to generate tokens, so it should also verify them.
 *
 * @param token - The JWT string to verify (unused but kept for backward compatibility).
 * @returns True if token is valid, false otherwise.
 */
export async function verifyToken(token: string): Promise<boolean> {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
    const response = await fetch(`${apiUrl}/api/auth/verify`, {
      method: 'GET',
      credentials: 'include', // Send httpOnly cookies
      cache: 'no-store', // Don't cache verification results
    })

    if (!response.ok) {
      if (process.env.NODE_ENV === 'development') {
        console.error('[verifyToken] Backend verification failed:', response.status)
      }
      return false
    }

    const data = await response.json()
    return data.valid === true
  } catch (error) {
    // Log in development for debugging
    if (process.env.NODE_ENV === 'development') {
      console.error('[verifyToken] Verification request failed:', error)
    }
    return false
  }
}
