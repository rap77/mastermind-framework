import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import { verifyToken } from '@/lib/auth'
import 'server-only'

export default async function AuthGuardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const cookieStore = await cookies()  // CRITICAL: await in Next.js 16 (Pitfall 5)
  const token = cookieStore.get('access_token')?.value

  if (!token) redirect('/login')

  const isValid = await verifyToken(token)
  if (!isValid) redirect('/login')

  return (
    <>
      {/* WSBrainBridge will mount here in Plan 05-03 */}
      {children}
    </>
  )
}
