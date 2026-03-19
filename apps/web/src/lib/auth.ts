import { jwtVerify } from 'jose'
import 'server-only'

/**
 * Retrieves the JWT secret key from environment.
 * @returns The secret key as a Uint8Array.
 * @throws Error if MM_SECRET_KEY is not set.
 */
function getSecret(): Uint8Array {
  const secretKey = process.env.MM_SECRET_KEY
  if (!secretKey) {
    throw new Error('MM_SECRET_KEY environment variable is required')
  }
  return new TextEncoder().encode(secretKey)
}

/**
 * Verifies a JWT token using the MM_SECRET_KEY.
 * @param token - The JWT string to verify.
 * @returns True if token is valid, false otherwise.
 */
export async function verifyToken(token: string): Promise<boolean> {
  try {
    const secret = getSecret()
    await jwtVerify(token, secret)
    return true
  } catch (error) {
    // Log in development for debugging
    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console -- Development-only error logging
      console.error('[verifyToken] JWT verification failed:', error)
    }
    return false
  }
}
