/**
 * LiveLogPanel Component
 *
 * **Purpose:** Virtual scrolled log viewer with WS subscription, filtering, and brain isolation
 * **Context:** Phase 08-03 — Engine Room live log panel
 */

'use client'

import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { Virtuoso, type VirtuosoHandle } from 'react-virtuoso'
import { useWSStore } from '@/stores/wsStore'
import { useLogFilterStore } from '@/stores/logFilterStore'
import {
  parseLogLine,
  filterLogsByLevel,
  filterLogsByBrain,
  formatTimestamp,
  type LogLine,
  type WS_LogEvent,
} from '@/lib/log-parser'
import { FilterBar } from './FilterBar'
import { LogBadge } from './LogBadge'

// ─── Types ──────────────────────────────────────────────────────────────────

interface LiveLogPanelProps {
  taskId?: string // if provided, logs from WS for this task
  logs?: LogLine[] // optional: static logs (for ExecutionDetail read-only view)
}

// ─── Log line row ────────────────────────────────────────────────────────────

function LogLineRow({ log }: { log: LogLine }) {
  const { isolatedBrainId, setIsolatedBrain } = useLogFilterStore()

  const handleBadgeClick = useCallback(() => {
    setIsolatedBrain(isolatedBrainId === log.brainId ? null : log.brainId)
  }, [isolatedBrainId, log.brainId, setIsolatedBrain])

  return (
    <div className="flex gap-2 px-3 py-1 text-xs font-mono hover:bg-slate-800 border-b border-slate-900">
      {/* Timestamp */}
      <span className="text-slate-500 w-[5.5rem] shrink-0">
        {formatTimestamp(log.timestamp)}
      </span>

      {/* Brain badge (clickable for isolation) */}
      <LogBadge
        brainId={log.brainId}
        brainName={log.brainName}
        level={log.level}
        onClick={handleBadgeClick}
      />

      {/* Message */}
      <span className="flex-1 text-slate-300 break-all">{log.message}</span>
    </div>
  )
}

// ─── Component ──────────────────────────────────────────────────────────────

/**
 * Virtual scrolled log viewer with WS subscription, level filtering, and brain isolation.
 * Uses react-virtuoso for O(1) memory usage regardless of log count.
 *
 * Two modes:
 * - Live (taskId provided or no taskId): subscribes to WS 'log:line' events
 * - Static (logs prop): read-only display, no WS subscription
 */
export function LiveLogPanel({ taskId: _taskId, logs: staticLogs }: LiveLogPanelProps) {
  const [liveLogs, setLiveLogs] = useState<LogLine[]>([])
  const rafRef = useRef<number | null>(null)
  const pendingRef = useRef<LogLine[]>([])
  const virtuosoRef = useRef<VirtuosoHandle>(null)

  const { subscribe, connected } = useWSStore()
  const { filterLevels, autoFollow, isolatedBrainId } = useLogFilterStore()

  const isStatic = Array.isArray(staticLogs)
  const rawLogs = isStatic ? staticLogs : liveLogs

  // ─── WS subscription with RAF batching ───────────────────────────────────

  useEffect(() => {
    if (isStatic) return // no WS subscription for static logs

    const unsubscribe = subscribe('log:line', (data: unknown) => {
      const parsed = parseLogLine(data as WS_LogEvent)
      if (!parsed) return

      pendingRef.current.push(parsed)

      if (rafRef.current) return // already scheduled
      rafRef.current = requestAnimationFrame(() => {
        const batch = pendingRef.current.splice(0)
        if (batch.length > 0) {
          setLiveLogs((prev) => [...prev, ...batch])
        }
        rafRef.current = null
      })
    })

    return () => {
      unsubscribe()
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current)
        rafRef.current = null
      }
    }
  }, [isStatic, subscribe])

  // ─── Filtered logs (memoized) ─────────────────────────────────────────────

  const filteredLogs = useMemo(() => {
    let result = rawLogs
    // filterLevels.size === 0 means user toggled all levels off → show nothing
    if (filterLevels.size === 0) return []
    // If not all 3 levels active, apply filter for performance
    if (filterLevels.size < 3) {
      result = filterLogsByLevel(result, filterLevels)
    }
    if (isolatedBrainId) {
      result = filterLogsByBrain(result, isolatedBrainId)
    }
    return result
  }, [rawLogs, filterLevels, isolatedBrainId])

  // ─── Auto-follow ──────────────────────────────────────────────────────────

  useEffect(() => {
    if (autoFollow && filteredLogs.length > 0) {
      virtuosoRef.current?.scrollToIndex({
        index: filteredLogs.length - 1,
        behavior: 'auto',
      })
    }
  }, [autoFollow, filteredLogs.length])

  // ─── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col h-full bg-slate-950 text-slate-100">
      {/* Filter bar */}
      <FilterBar />

      {/* WS disconnection banner */}
      {!isStatic && !connected && (
        <div
          className="px-4 py-2 bg-yellow-900/50 text-yellow-300 text-xs border-b border-yellow-800"
          role="status"
          aria-live="polite"
        >
          Logs paused (WS disconnected) — logs will resume when reconnected
        </div>
      )}

      {/* Empty state */}
      {filteredLogs.length === 0 && (
        <div className="flex-1 flex items-center justify-center text-slate-500 text-sm">
          {rawLogs.length === 0 ? 'No logs yet' : 'No logs match current filters'}
        </div>
      )}

      {/* Virtual log list */}
      {filteredLogs.length > 0 && (
        <Virtuoso
          ref={virtuosoRef}
          className="flex-1"
          data={filteredLogs}
          overscan={10}
          itemContent={(_index, log) => <LogLineRow key={log.id} log={log} />}
          aria-label="Live log output"
        />
      )}
    </div>
  )
}
