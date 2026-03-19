import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { verifyToken } from '@/lib/auth'
import { WSBrainBridge } from '@/components/ws/WSBrainBridge'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import 'server-only'

/**
 * Authentication guard layout for protected routes.
 * Verifies JWT token from httpOnly cookie and redirects to login if invalid.
 * Also initializes WebSocket connection for real-time updates.
 * @param children - Protected page content to render if authenticated.
 */
export default async function AuthGuardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const cookieStore = await cookies()  // CRITICAL: await in Next.js 16 (Pitfall 5)
  const token = cookieStore.get('access_token')?.value

  if (!token) {
    redirect('/login')
  }

  const isValid = await verifyToken(token)

  if (!isValid) {
    redirect('/login')
  }

  // WSBrainBridge fetches token from /api/auth/token (server-side cookie read)
  // No need to pass token as prop — more secure (not in client bundle)
  return (
    <>
      <WSBrainBridge taskId={null} />
      <ErrorBoundary>
        {children}
      </ErrorBoundary>
    </>
  )
}
