import { jwtVerify } from 'jose'
import 'server-only'

function getSecret(): Uint8Array {
  const secretKey = process.env.MM_SECRET_KEY
  if (!secretKey) {
    throw new Error('MM_SECRET_KEY environment variable is required')
  }
  return new TextEncoder().encode(secretKey)
}

export async function verifyToken(token: string): Promise<boolean> {
  try {
    const secret = getSecret()
    await jwtVerify(token, secret)
    return true
  } catch (error) {
    return false
  }
}
