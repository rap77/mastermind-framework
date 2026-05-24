'use client'

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { RefreshCcw, Radio, TimerReset } from 'lucide-react'

import { ProjectStateDashboard, type ProjectStateDashboardProps } from '@/components/project-state/ProjectStateDashboard'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const REFRESH_INTERVAL_MS = 15_000

/** How long to debounce rapid SSE events before triggering a refresh (ms). */
const SSE_DEBOUNCE_MS = 800

function formatLastRefresh(date: Date | null): string {
  if (!date) return 'Not refreshed yet'
  return new Intl.DateTimeFormat('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
  }).format(date)
}

/**
 * Resolve the backend API base URL for SSE subscriptions.
 * Falls back to localhost:8001 when the env var is not exposed to the browser.
 */
function resolveApiBase(): string {
  // NEXT_PUBLIC_ prefix is required for client-side access.
  const fromEnv =
    typeof window !== 'undefined'
      ? (window as typeof window & { __AGENT_RUNTIME_URL__?: string }).__AGENT_RUNTIME_URL__
      : undefined
  return fromEnv ?? 'http://localhost:8001'
}

interface ProjectStateLiveShellWithIdProps extends ProjectStateDashboardProps {
  /** Project ID used to subscribe to the realtime SSE stream for this project. */
  projectId?: string
}

export function ProjectStateLiveShell(props: ProjectStateLiveShellWithIdProps) {
  const { projectId, ...dashboardProps } = props
  const router = useRouter()
  const [autoRefreshEnabled, setAutoRefreshEnabled] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [lastRefreshAt, setLastRefreshAt] = useState<Date | null>(new Date())
  const [sseConnected, setSseConnected] = useState(false)
  const sseDebounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const sseRef = useRef<EventSource | null>(null)

  const refreshNow = useCallback(() => {
    setIsRefreshing(true)
    router.refresh()
    setLastRefreshAt(new Date())
    window.setTimeout(() => setIsRefreshing(false), 500)
  }, [router])

  // Polling fallback — fires when SSE is not connected or when auto-refresh
  // is explicitly enabled by the user.
  useEffect(() => {
    if (!autoRefreshEnabled || sseConnected) return

    const timer = window.setInterval(() => {
      if (document.visibilityState !== 'visible') return
      refreshNow()
    }, REFRESH_INTERVAL_MS)

    return () => window.clearInterval(timer)
  }, [autoRefreshEnabled, sseConnected, refreshNow])

  // SSE subscription — triggers a debounced refresh on any non-heartbeat event.
  useEffect(() => {
    if (!autoRefreshEnabled || !projectId || typeof EventSource === 'undefined') return

    const apiBase = resolveApiBase()
    const url = `${apiBase}/api/projects/${encodeURIComponent(projectId)}/events`

    const es = new EventSource(url, { withCredentials: true })
    sseRef.current = es

    es.addEventListener('open', () => {
      setSseConnected(true)
    })

    es.addEventListener('project_state_event', () => {
      // Debounce: multiple rapid events only cause one refresh.
      if (sseDebounceRef.current) clearTimeout(sseDebounceRef.current)
      sseDebounceRef.current = setTimeout(() => {
        if (document.visibilityState === 'visible') {
          refreshNow()
        }
      }, SSE_DEBOUNCE_MS)
    })

    es.addEventListener('error', () => {
      // Browser will automatically reconnect; mark as disconnected so the
      // polling fallback resumes in the meantime.
      setSseConnected(false)
    })

    return () => {
      es.close()
      sseRef.current = null
      setSseConnected(false)
      if (sseDebounceRef.current) clearTimeout(sseDebounceRef.current)
    }
  }, [autoRefreshEnabled, projectId, refreshNow])

  const refreshStatusLabel = useMemo(() => {
    if (isRefreshing) return 'Refreshing…'
    if (!autoRefreshEnabled) return 'Auto refresh paused'
    if (sseConnected) return 'Live (realtime)'
    return `Auto refresh every ${REFRESH_INTERVAL_MS / 1000}s`
  }, [autoRefreshEnabled, isRefreshing, sseConnected])

  return (
    <div className="relative">
      <div className="sticky top-0 z-20 border-b border-border/60 bg-background/85 backdrop-blur">
        <div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-3 px-6 py-3">
          <div className="flex items-center gap-2">
            <Badge
              variant={autoRefreshEnabled ? (sseConnected ? 'success' : 'secondary') : 'secondary'}
              className="gap-1.5"
            >
              <Radio className="h-3 w-3" />
              {refreshStatusLabel}
            </Badge>
            <span className="text-xs text-muted-foreground">
              Last sync: {formatLastRefresh(lastRefreshAt)}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setAutoRefreshEnabled((current) => !current)}
            >
              <TimerReset className="h-4 w-4" />
              {autoRefreshEnabled ? 'Pause live' : 'Resume live'}
            </Button>
            <Button variant="default" size="sm" onClick={refreshNow} disabled={isRefreshing}>
              <RefreshCcw className="h-4 w-4" />
              Refresh now
            </Button>
          </div>
        </div>
      </div>

      <ProjectStateDashboard {...dashboardProps} />
    </div>
  )
}
