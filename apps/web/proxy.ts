import { NextRequest, NextResponse } from 'next/server'
import { jwtVerify } from 'jose'

function getSecret(): Uint8Array {
  const secretKey = process.env.MM_SECRET_KEY
  if (!secretKey) {
    throw new Error('MM_SECRET_KEY environment variable is required')
  }
  return new TextEncoder().encode(secretKey)
}

export async function proxy(request: NextRequest): Promise<NextResponse> {
  const token = request.cookies.get('access_token')?.value

  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url))
  }

  try {
    const secret = getSecret()
    await jwtVerify(token, secret)
    return NextResponse.next()
  } catch (error) {
    return NextResponse.redirect(new URL('/login', request.url))
  }
}

export const config = {
  matcher: ['/((?!login|_next/static|_next/image|favicon.ico).*)'],
}
