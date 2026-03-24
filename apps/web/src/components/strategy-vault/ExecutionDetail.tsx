'use client'

import React, { memo, useEffect, useCallback } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import { ChevronDown, Copy, Download, XCircle, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import { SmartMarkdown } from './SmartMarkdown'
import { SnapshotScrubber } from './SnapshotScrubber'
import { useReplayStore } from '@/stores/replayStore'
import type { SnapshotMilestone } from '@/stores/replayStore'

// ─── Types ────────────────────────────────────────────────────────────────────

export interface BrainOutput {
  brain_id: string
  status: 'idle' | 'running' | 'complete' | 'error'
  output: string // Markdown formatted
  duration_ms: number
  timestamp: number
}

export interface GraphNode {
  id: string
  type?: string
  data: Record<string, unknown>
  position?: { x: number; y: number }
}

export interface GraphEdge {
  id: string
  source: string
  target: string
  type?: string
}

export interface ExecutionDetail {
  id: string
  task_id: string
  brief: string
  status: 'success' | 'error' | 'running'
  duration_ms: number
  brain_count: number
  created_at: string
  milestones: SnapshotMilestone[]
  brain_outputs: Record<string, BrainOutput>
  graph_snapshot: { nodes: GraphNode[]; edges: GraphEdge[] }
}

// ─── Props ────────────────────────────────────────────────────────────────────

export interface ExecutionDetailProps {
  executionId: string
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

async function fetchExecution(id: string): Promise<ExecutionDetail> {
  const res = await fetch(`/api/executions/${id}`, {
    headers: { 'Content-Type': 'application/json' },
  })
  if (res.status === 404) {
    throw new NotFoundError(`Execution ${id} not found`)
  }
  if (!res.ok) {
    throw new Error(`Failed to fetch execution: ${res.status}`)
  }
  return res.json() as Promise<ExecutionDetail>
}

class NotFoundError extends Error {
  readonly isNotFound = true
  constructor(message: string) {
    super(message)
    this.name = 'NotFoundError'
  }
}

function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`
  const seconds = Math.floor(ms / 1000)
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  if (minutes === 0) return `${seconds}s`
  return `${minutes}m ${remainingSeconds}s`
}

// ─── CopyButton ───────────────────────────────────────────────────────────────

interface CopyButtonProps {
  text: string
  label?: string
  className?: string
}

function CopyButton({ text, label = 'Copy', className }: CopyButtonProps) {
  const [copied, setCopied] = React.useState(false)

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // Clipboard API may not be available in some environments
    }
  }, [text])

  return (
    <button
      type="button"
      onClick={handleCopy}
      className={cn(
        'inline-flex items-center gap-1 text-xs px-2 py-1 rounded',
        'bg-secondary hover:bg-secondary/80 text-secondary-foreground transition-colors',
        className
      )}
      data-testid="copy-button"
    >
      <Copy className="w-3 h-3" />
      {copied ? 'Copied!' : label}
    </button>
  )
}

// ─── ReplayNexus ─────────────────────────────────────────────────────────────

interface ReplayNexusProps {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

/**
 * ReplayNexus — read-only DAG view for execution replay.
 * Shows graph_snapshot in a simplified layout with "REPLAY MODE" banner.
 * Reuses React Flow concepts from NexusCanvas but without live WS updates.
 */
const ReplayNexus = memo(function ReplayNexus({ nodes, edges }: ReplayNexusProps) {
  return (
    <div
      className="relative border border-border rounded-lg bg-muted/30 overflow-hidden h-[280px]"
      data-testid="replay-nexus"
    >
      {/* REPLAY MODE banner */}
      <div
        className="absolute top-2 left-2 z-10 px-2 py-0.5 bg-amber-500/20 text-amber-700 dark:text-amber-400 text-xs font-medium rounded border border-amber-500/30"
        data-testid="replay-mode-banner"
      >
        REPLAY MODE
      </div>

      {/* Simplified DAG visualization (React Flow omitted for SSR safety in detail view) */}
      <div className="flex items-center justify-center h-full flex-col gap-2 text-muted-foreground text-sm">
        <div className="text-xs font-medium">
          {nodes.length} nodes · {edges.length} edges
        </div>
        <div className="flex flex-wrap gap-1 justify-center max-w-[80%]">
          {nodes.slice(0, 8).map((node) => (
            <div
              key={node.id}
              className="px-2 py-0.5 bg-secondary rounded text-xs text-secondary-foreground"
              data-testid={`replay-node-${node.id}`}
            >
              {String(node.data?.name ?? node.id)}
            </div>
          ))}
          {nodes.length > 8 && (
            <div className="px-2 py-0.5 bg-secondary rounded text-xs text-muted-foreground">
              +{nodes.length - 8} more
            </div>
          )}
        </div>
      </div>
    </div>
  )
})

// ─── BrainAccordionItem ───────────────────────────────────────────────────────

interface BrainAccordionItemProps {
  brainOutput: BrainOutput
  isOpen: boolean
  onToggle: () => void
}

function BrainAccordionItem({ brainOutput, isOpen, onToggle }: BrainAccordionItemProps) {
  return (
    <div
      className="border border-border rounded-lg overflow-hidden"
      data-testid={`accordion-item-${brainOutput.brain_id}`}
    >
      {/* Header */}
      <button
        type="button"
        className="w-full flex items-center justify-between px-4 py-3 bg-muted/50 hover:bg-muted/80 transition-colors text-sm"
        onClick={onToggle}
        aria-expanded={isOpen}
        data-testid={`accordion-header-${brainOutput.brain_id}`}
      >
        <div className="flex items-center gap-3">
          <span
            className={cn(
              'w-2 h-2 rounded-full flex-shrink-0',
              brainOutput.status === 'complete' && 'bg-green-500',
              brainOutput.status === 'error' && 'bg-red-500',
              brainOutput.status === 'running' && 'bg-yellow-500 animate-pulse',
              brainOutput.status === 'idle' && 'bg-secondary'
            )}
          />
          <span className="font-medium">{brainOutput.brain_id}</span>
          <span className="text-muted-foreground text-xs">
            {formatDuration(brainOutput.duration_ms)}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <CopyButton text={brainOutput.output} label="Copy" />
          <ChevronDown
            className={cn(
              'w-4 h-4 text-muted-foreground transition-transform duration-200',
              isOpen && 'rotate-180'
            )}
          />
        </div>
      </button>

      {/* Content */}
      {isOpen && (
        <div
          className="px-4 py-3 border-t border-border bg-background"
          data-testid={`accordion-content-${brainOutput.brain_id}`}
        >
          <SmartMarkdown markdown={brainOutput.output} compact />
        </div>
      )}
    </div>
  )
}

// ─── LogsPanel ───────────────────────────────────────────────────────────────

interface LogsPanelProps {
  brainOutputs: Record<string, BrainOutput>
  milestones: SnapshotMilestone[]
  currentSnapshotIndex: number
}

/**
 * LogsPanel — static log list synced to scrubber position.
 * Shows brain outputs sorted by timestamp, scrolls to current milestone.
 */
function LogsPanel({ brainOutputs, milestones, currentSnapshotIndex }: LogsPanelProps) {
  const panelRef = React.useRef<HTMLDivElement>(null)

  // Get current milestone timestamp for sync
  const currentMilestone = milestones[currentSnapshotIndex]
  const currentTimestamp = currentMilestone?.timestamp ?? 0

  // Sort outputs by timestamp
  const sortedOutputs = Object.values(brainOutputs).sort(
    (a, b) => a.timestamp - b.timestamp
  )

  // Filter outputs up to current timestamp (scrubber sync)
  // When at index 0 (start) or no milestones yet, show ALL outputs (full history view)
  // Only apply filter when user has actively scrubbed to a specific point
  const isAtStart = currentSnapshotIndex === 0
  const visibleOutputs = (!isAtStart && currentTimestamp > 0)
    ? sortedOutputs.filter((o) => o.timestamp <= currentTimestamp)
    : sortedOutputs

  // Auto-scroll to bottom when milestone changes
  useEffect(() => {
    if (panelRef.current) {
      panelRef.current.scrollTop = panelRef.current.scrollHeight
    }
  }, [currentSnapshotIndex])

  return (
    <div
      ref={panelRef}
      className="flex flex-col gap-1 overflow-y-auto max-h-[320px] pr-1"
      data-testid="logs-panel"
    >
      {visibleOutputs.length === 0 ? (
        <div className="text-xs text-muted-foreground text-center py-6">
          No activity at this point in the timeline
        </div>
      ) : (
        visibleOutputs.map((output) => (
          <div
            key={output.brain_id}
            className={cn(
              'flex items-start gap-2 text-xs p-2 rounded',
              output.status === 'complete' && 'bg-green-50 dark:bg-green-900/10',
              output.status === 'error' && 'bg-red-50 dark:bg-red-900/10',
              output.status === 'running' && 'bg-yellow-50 dark:bg-yellow-900/10',
              output.status === 'idle' && 'bg-muted/30'
            )}
            data-testid={`log-entry-${output.brain_id}`}
          >
            <span
              className={cn(
                'font-mono shrink-0',
                output.status === 'complete' && 'text-green-700 dark:text-green-400',
                output.status === 'error' && 'text-red-700 dark:text-red-400',
                output.status === 'running' && 'text-yellow-700 dark:text-yellow-400',
                output.status === 'idle' && 'text-muted-foreground'
              )}
            >
              [{output.status.toUpperCase()}]
            </span>
            <span className="text-muted-foreground flex-1">
              {output.brain_id}
            </span>
            <span className="text-muted-foreground font-mono shrink-0">
              {formatDuration(output.duration_ms)}
            </span>
          </div>
        ))
      )}
    </div>
  )
}

// ─── ExecutionDetail ─────────────────────────────────────────────────────────

/**
 * ExecutionDetail — full execution audit view with DAG replay, accordion, and scrubber.
 *
 * **Layout:** 3-section layout:
 * 1. ReplayNexus (DAG snapshot, read-only, REPLAY MODE banner)
 * 2. Brain outputs accordion (SmartMarkdown per brain, copy-to-clipboard)
 * 3. SnapshotScrubber + LogsPanel (synced timeline navigation)
 *
 * **Data flow:**
 * 1. GET /api/executions/{id} via TanStack Query
 * 2. replayStore.setSnapshots — milestones computed
 * 3. SnapshotScrubber.onScrub → jumpToMilestone → LogsPanel syncs
 *
 * @example
 * ```tsx
 * <ExecutionDetail executionId="exec-001" />
 * ```
 */
export function ExecutionDetail({ executionId }: ExecutionDetailProps) {
  const router = useRouter()
  const { milestones, currentSnapshotIndex, jumpToMilestone, setSnapshots } = useReplayStore()
  const [openAccordions, setOpenAccordions] = React.useState<Set<string>>(new Set())

  const { data: execution, isLoading, isError, error } = useQuery({
    queryKey: ['execution', executionId],
    queryFn: () => fetchExecution(executionId),
    staleTime: 60_000, // 1 min — execution data doesn't change
    retry: (_failureCount, err) => {
      // Don't retry any errors — let QueryClient default handle retries
      if (err instanceof NotFoundError) return false
      return false
    },
  })

  // Load milestones into replay store when data arrives
  useEffect(() => {
    if (execution?.milestones?.length) {
      // Convert execution milestones (from API) to Snapshot format for store
      // The milestones from the API serve as navigation points directly
      const snapshots = execution.milestones.map((m) => ({
        timestamp: m.timestamp,
        snapshot: new Map<string, import('@/stores/replayStore').BrainStateReplay>(),
      }))
      setSnapshots(snapshots)
    }
  }, [execution, setSnapshots])

  // Redirect on 404
  useEffect(() => {
    if (isError && error instanceof NotFoundError) {
      router.push('/strategy-vault')
    }
  }, [isError, error, router])

  // ── Accordion handlers ────────────────────────────────────────────────────

  const toggleAccordion = useCallback((brainId: string) => {
    setOpenAccordions((prev) => {
      const next = new Set(prev)
      if (next.has(brainId)) {
        next.delete(brainId)
      } else {
        next.add(brainId)
      }
      return next
    })
  }, [])

  // ── Download handler ──────────────────────────────────────────────────────

  const handleDownload = useCallback(() => {
    if (!execution) return
    const content = Object.entries(execution.brain_outputs)
      .map(([id, output]) => `## ${id}\n\n${output.output}\n\n---`)
      .join('\n\n')

    const blob = new Blob([`# Execution ${execution.id}\n\n${content}`], {
      type: 'text/plain',
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `execution-${execution.id.slice(0, 8)}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }, [execution])

  // ── Loading state ─────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div className="flex flex-col gap-6 animate-pulse" data-testid="execution-detail-loading">
        <div className="h-[280px] bg-muted rounded-lg" />
        <div className="h-8 bg-muted rounded w-1/3" />
        <div className="h-48 bg-muted rounded" />
      </div>
    )
  }

  // ── Error state ───────────────────────────────────────────────────────────

  if (isError && !(error instanceof NotFoundError)) {
    return (
      <div
        className="flex flex-col items-center justify-center py-12 gap-4"
        data-testid="execution-detail-error"
      >
        <AlertCircle className="w-8 h-8 text-red-500" />
        <p className="text-muted-foreground text-sm">
          {error instanceof Error ? error.message : 'Failed to load execution'}
        </p>
      </div>
    )
  }

  if (!execution) return null

  const brainOutputsList = Object.values(execution.brain_outputs)

  // ── Main render ───────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col gap-6" data-testid="execution-detail">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-xl font-semibold">{execution.brief}</h2>
          <p className="text-sm text-muted-foreground mt-1">
            {execution.brain_count} brains · {formatDuration(execution.duration_ms)} ·{' '}
            {new Date(execution.created_at).toLocaleString()}
          </p>
        </div>
        <button
          type="button"
          onClick={handleDownload}
          className="inline-flex items-center gap-1.5 text-sm px-3 py-1.5 border border-border rounded hover:bg-muted transition-colors"
          data-testid="download-button"
        >
          <Download className="w-4 h-4" />
          Download .txt
        </button>
      </div>

      {/* ReplayNexus + Logs (2-column) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Left: DAG snapshot */}
        <ReplayNexus
          nodes={execution.graph_snapshot.nodes}
          edges={execution.graph_snapshot.edges}
        />

        {/* Right: Logs panel */}
        <div className="border border-border rounded-lg p-4" data-testid="logs-container">
          <h3 className="text-sm font-medium mb-3">Brain Activity Log</h3>
          <LogsPanel
            brainOutputs={execution.brain_outputs}
            milestones={milestones}
            currentSnapshotIndex={currentSnapshotIndex}
          />
        </div>
      </div>

      {/* Scrubber */}
      {milestones.length > 0 && (
        <div>
          <h3 className="text-sm font-medium mb-2">Execution Timeline</h3>
          <SnapshotScrubber
            milestones={milestones}
            currentIndex={currentSnapshotIndex}
            onScrub={jumpToMilestone}
            data-testid="execution-scrubber"
          />
        </div>
      )}

      {/* Brain outputs accordion */}
      <div className="flex flex-col gap-2" data-testid="brain-outputs-accordion">
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-sm font-medium">Brain Outputs ({brainOutputsList.length})</h3>
        </div>
        {brainOutputsList.map((brainOutput) => (
          <BrainAccordionItem
            key={brainOutput.brain_id}
            brainOutput={brainOutput}
            isOpen={openAccordions.has(brainOutput.brain_id)}
            onToggle={() => toggleAccordion(brainOutput.brain_id)}
          />
        ))}
        {brainOutputsList.length === 0 && (
          <p className="text-muted-foreground text-sm text-center py-6">
            No brain outputs available for this execution.
          </p>
        )}
      </div>
    </div>
  )
}
