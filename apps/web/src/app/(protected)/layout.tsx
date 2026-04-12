import { AuthGuard } from '@/components/auth/AuthGuard'

/**
 * Authentication guard layout for protected routes.
 * Uses Client Component to verify JWT token and redirect if invalid.
 * @param children - Protected page content to render if authenticated.
 */
export default function AuthGuardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <AuthGuard>{children}</AuthGuard>
}
