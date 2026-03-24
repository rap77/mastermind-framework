'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { useQuery } from '@tanstack/react-query'
import { CheckCircle, XCircle, Loader2, Clock, Brain, ArrowRight } from 'lucide-react'
import { cn } from '@/lib/utils'

// ─── Types ────────────────────────────────────────────────────────────────────

export interface ExecutionSummary {
  id: string
  status: 'success' | 'error' | 'running'
  brief: string
  duration_ms: number
  brain_count: number
  created_at: string
}

export interface ExecutionHistoryResponse {
  executions: ExecutionSummary[]
  next_cursor: string | null
  has_more: boolean
}

// ─── Props ────────────────────────────────────────────────────────────────────

export interface ExecutionListProps {
  /** Optional: initial cursor for pagination (deep linking) */
  initialCursor?: string
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

/**
 * Format duration from milliseconds to human-readable string.
 * e.g., 154234 → "2m 34s"
 */
function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  if (minutes === 0) return `${seconds}s`
  return `${minutes}m ${remainingSeconds}s`
}

/**
 * Format ISO datetime as relative time.
 * e.g., "2 hours ago", "3 days ago"
 */
function formatRelativeTime(isoString: string): string {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffSeconds = Math.floor(diffMs / 1000)
  const diffMinutes = Math.floor(diffSeconds / 60)
  const diffHours = Math.floor(diffMinutes / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffDays > 0) return `${diffDays}d ago`
  if (diffHours > 0) return `${diffHours}h ago`
  if (diffMinutes > 0) return `${diffMinutes}m ago`
  return 'just now'
}

/**
 * Truncate brief text to 100 chars with ellipsis
 */
function truncateBrief(brief: string, maxLength = 100): string {
  if (brief.length <= maxLength) return brief
  return `${brief.slice(0, maxLength)}…`
}

// ─── Status Badge ─────────────────────────────────────────────────────────────

interface StatusBadgeProps {
  status: ExecutionSummary['status']
}

function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
        status === 'success' && 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
        status === 'error' && 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400',
        status === 'running' && 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400'
      )}
      data-testid={`status-badge-${status}`}
    >
      {status === 'success' && <CheckCircle className="w-3 h-3" />}
      {status === 'error' && <XCircle className="w-3 h-3" />}
      {status === 'running' && <Loader2 className="w-3 h-3 animate-spin" />}
      {status}
    </span>
  )
}

// ─── Skeleton ─────────────────────────────────────────────────────────────────

function SkeletonRow() {
  return (
    <tr className="border-b border-border">
      {[1, 2, 3, 4, 5].map((i) => (
        <td key={i} className="px-4 py-3">
          <div className="h-4 bg-muted animate-pulse rounded" style={{ width: `${60 + i * 10}%` }} />
        </td>
      ))}
    </tr>
  )
}

// ─── Data Fetching ────────────────────────────────────────────────────────────

async function fetchExecutionHistory(cursor?: string): Promise<ExecutionHistoryResponse> {
  const params = new URLSearchParams()
  if (cursor) params.append('cursor', cursor)

  const res = await fetch(`/api/executions/history?${params.toString()}`, {
    headers: { 'Content-Type': 'application/json' },
  })

  if (!res.ok) {
    throw new Error(`Failed to fetch executions: ${res.status}`)
  }

  return res.json() as Promise<ExecutionHistoryResponse>
}

// ─── Component ────────────────────────────────────────────────────────────────

/**
 * ExecutionList — paginated table of past task executions.
 *
 * **Features:**
 * - Cursor-based pagination with Prev/Next controls
 * - Status badges with icons (success=green, error=red, running=yellow+spinner)
 * - Brief text truncated at 100 chars
 * - Relative timestamps ("2h ago")
 * - Loading skeletons, error state, empty state
 * - TanStack Query with 30s staleTime cache
 *
 * @example
 * ```tsx
 * <ExecutionList />
 * ```
 */
export function ExecutionList({ initialCursor }: ExecutionListProps) {
  const [cursor, setCursor] = useState<string | undefined>(initialCursor)
  const [cursorStack, setCursorStack] = useState<string[]>([])

  const { data, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['executions', cursor],
    queryFn: () => fetchExecutionHistory(cursor),
    staleTime: 30_000,
  })

  // ── Pagination ────────────────────────────────────────────────────────────

  const handleNext = () => {
    if (data?.next_cursor) {
      // Push current cursor to stack for going back
      setCursorStack((stack) => [...stack, cursor ?? ''])
      setCursor(data.next_cursor)
    }
  }

  const handlePrev = () => {
    const stack = [...cursorStack]
    const previous = stack.pop()
    setCursorStack(stack)
    setCursor(previous === '' ? undefined : previous)
  }

  const isFirstPage = cursorStack.length === 0

  // ── Render states ─────────────────────────────────────────────────────────

  if (isError) {
    return (
      <div
        className="flex flex-col items-center justify-center py-12 gap-4"
        data-testid="execution-list-error"
      >
        <XCircle className="w-8 h-8 text-red-500" />
        <p className="text-muted-foreground text-sm">
          {error instanceof Error ? error.message : 'Failed to load executions'}
        </p>
        <button
          onClick={() => refetch()}
          className="text-xs px-3 py-1.5 bg-primary text-primary-foreground rounded hover:bg-primary/90 transition-colors"
        >
          Retry
        </button>
      </div>
    )
  }

  // ── Table ─────────────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col gap-4" data-testid="execution-list">
      <div className="border border-border rounded-lg overflow-hidden">
        <table className="w-full text-sm" data-testid="executions-table">
          <thead className="bg-muted">
            <tr>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">Status</th>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">Brief</th>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">
                <Clock className="w-3.5 h-3.5 inline mr-1" />
                Duration
              </th>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">
                <Brain className="w-3.5 h-3.5 inline mr-1" />
                Brains
              </th>
              <th className="px-4 py-3 text-left font-medium text-muted-foreground">When</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              // Skeleton rows while loading
              Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
            ) : data?.executions.length === 0 ? (
              // Empty state
              <tr>
                <td
                  colSpan={5}
                  className="px-4 py-12 text-center text-muted-foreground"
                  data-testid="empty-state"
                >
                  No executions yet. Run a task to see its history here.
                </td>
              </tr>
            ) : (
              // Execution rows
              data?.executions.map((execution) => (
                <tr
                  key={execution.id}
                  className="border-t border-border hover:bg-muted/50 transition-colors cursor-pointer group"
                  data-testid={`execution-row-${execution.id}`}
                >
                  <td className="px-4 py-3">
                    <StatusBadge status={execution.status} />
                  </td>
                  <td className="px-4 py-3 max-w-xs">
                    <span className="text-sm" title={execution.brief}>
                      {truncateBrief(execution.brief)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-muted-foreground tabular-nums">
                    {formatDuration(execution.duration_ms)}
                  </td>
                  <td className="px-4 py-3 text-muted-foreground tabular-nums">
                    {execution.brain_count}
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-between">
                      <span
                        className="text-muted-foreground text-xs"
                        title={new Date(execution.created_at).toLocaleString()}
                      >
                        {formatRelativeTime(execution.created_at)}
                      </span>
                      <Link
                        href={`/strategy-vault/${execution.id}`}
                        className="inline-flex items-center gap-1 text-xs text-primary opacity-0 group-hover:opacity-100 transition-opacity"
                        data-testid={`view-link-${execution.id}`}
                      >
                        View
                        <ArrowRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination controls */}
      {(data?.executions && data.executions.length > 0) && (
        <div className="flex items-center justify-between text-sm" data-testid="pagination-controls">
          <button
            onClick={handlePrev}
            disabled={isFirstPage}
            className={cn(
              'px-3 py-1.5 rounded border border-border transition-colors',
              isFirstPage
                ? 'opacity-40 cursor-not-allowed'
                : 'hover:bg-muted cursor-pointer'
            )}
            data-testid="pagination-prev"
          >
            ← Previous
          </button>

          <span className="text-muted-foreground text-xs" data-testid="pagination-info">
            {isFirstPage ? 'First page' : `Page ${cursorStack.length + 1}`}
          </span>

          <button
            onClick={handleNext}
            disabled={!data?.has_more}
            className={cn(
              'px-3 py-1.5 rounded border border-border transition-colors',
              !data?.has_more
                ? 'opacity-40 cursor-not-allowed'
                : 'hover:bg-muted cursor-pointer'
            )}
            data-testid="pagination-next"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}
