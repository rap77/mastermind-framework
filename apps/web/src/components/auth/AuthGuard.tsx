'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { WSBrainBridge } from '@/components/ws/WSBrainBridge'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { ThreeColumnLayout } from '@/components/layout/ThreeColumnLayout'

interface AuthGuardProps {
  children: React.ReactNode
}

/**
 * Client-side authentication guard.
 * Verifies JWT token by calling backend /api/auth/verify endpoint.
 * Redirects to login if token is invalid or missing.
 */
export function AuthGuard({ children }: AuthGuardProps) {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    async function verifyToken() {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/auth/verify`, {
          method: 'GET',
          credentials: 'include',
          cache: 'no-store',
        })

        if (!response.ok) {
          console.error('[AuthGuard] Backend verification failed:', response.status)
          router.push('/login')
          return
        }

        const data = await response.json()
        if (data.valid === true) {
          setIsAuthenticated(true)
        } else {
          router.push('/login')
        }
      } catch (error) {
        console.error('[AuthGuard] Verification request failed:', error)
        router.push('/login')
      } finally {
        setIsLoading(false)
      }
    }

    verifyToken()
  }, [router])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-muted-foreground">Verifying authentication...</div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return null // Router will redirect
  }

  return (
    <>
      <WSBrainBridge taskId={null} />
      <ErrorBoundary>
        <ThreeColumnLayout showPropertiesPanel={false}>
          {children}
        </ThreeColumnLayout>
      </ErrorBoundary>
    </>
  )
}
