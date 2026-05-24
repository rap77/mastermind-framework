'use client'

import { useMemo, useState, useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { CheckCircle2, ClipboardPenLine, Loader2, Save, RefreshCw } from 'lucide-react'

import {
  createProjectCheckpoint,
  createProjectDecision,
  updateProjectTaskStatus,
} from '@/app/actions/project-state'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { toastError, toastSuccess } from '@/lib/toast'
import type { RunDetail, TaskContextProjection } from '@/lib/project-state-api'

const DEFAULT_DECISION_STATUS = 'proposed'

interface ProjectStateWritePanelProps {
  selectedProjectId: string | null
  selectedTaskId: string | null
  runs: RunDetail[]
  contextProjection: TaskContextProjection | null
}

function safeJsonParse(input: string, fallback: Record<string, unknown>): Record<string, unknown> {
  const trimmed = input.trim()
  if (!trimmed) return fallback

  try {
    const parsed = JSON.parse(trimmed) as unknown
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      return parsed as Record<string, unknown>
    }
    return fallback
  } catch {
    return fallback
  }
}

function ProjectStateWritePanelContent({
  selectedProjectId,
  selectedTaskId,
  runs,
  contextProjection,
}: ProjectStateWritePanelProps) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [nextStepSummary, setNextStepSummary] = useState(contextProjection?.next_step ?? '')
  const [runId, setRunId] = useState('')
  const [contextSummaryJson, setContextSummaryJson] = useState(
    JSON.stringify(
      {
        objective: contextProjection?.objective ?? '',
        blockers: contextProjection?.blockers ?? [],
        dependencies: contextProjection?.dependencies ?? [],
      },
      null,
      2
    )
  )
  const [resumeStateJson, setResumeStateJson] = useState(
    JSON.stringify(
      {
        selected_task_id: selectedTaskId,
        latest_checkpoint_id: contextProjection?.latest_checkpoint_id,
      },
      null,
      2
    )
  )
  const [decisionTitle, setDecisionTitle] = useState(
    selectedTaskId ? `Decision for ${selectedTaskId}` : ''
  )
  const [decisionStatus, setDecisionStatus] = useState(DEFAULT_DECISION_STATUS)
  const [decisionRationale, setDecisionRationale] = useState('')
  const [decisionMetadataJson, setDecisionMetadataJson] = useState(
    JSON.stringify(
      {
        source: 'project-state-console',
        selected_task_id: selectedTaskId,
      },
      null,
      2
    )
  )

  const [statusValue, setStatusValue] = useState('')
  const [statusReason, setStatusReason] = useState('')

  const taskRuns = useMemo(
    () => runs.filter((run) => run.task_id === selectedTaskId),
    [runs, selectedTaskId]
  )

  const disableCheckpoint = !selectedProjectId || !selectedTaskId || !nextStepSummary.trim() || isPending
  const disableDecision = !selectedProjectId || !decisionTitle.trim() || !decisionRationale.trim() || isPending
  const disableStatusUpdate = !selectedProjectId || !selectedTaskId || !statusValue.trim() || isPending

  const handleCheckpointSubmit = (): void => {
    if (!selectedProjectId || !selectedTaskId) {
      toastError('Select a project task before creating a checkpoint')
      return
    }

    startTransition(async () => {
      const result = await createProjectCheckpoint({
        projectId: selectedProjectId,
        taskId: selectedTaskId,
        runId: runId || null,
        nextStepSummary,
        contextSummary: safeJsonParse(contextSummaryJson, {}),
        resumeState: safeJsonParse(resumeStateJson, {}),
      })

      if (!result.success) {
        toastError(result.error || 'Failed to create checkpoint')
        return
      }

      toastSuccess('Checkpoint created')
      router.refresh()
    })
  }

  const handleStatusUpdateSubmit = (): void => {
    if (!selectedProjectId || !selectedTaskId) {
      toastError('Select a project task before updating status')
      return
    }

    startTransition(async () => {
      const result = await updateProjectTaskStatus({
        projectId: selectedProjectId,
        taskId: selectedTaskId,
        status: statusValue,
        reason: statusReason || null,
      })

      if (!result.success) {
        toastError(result.error || 'Failed to update task status')
        return
      }

      toastSuccess('Task status updated')
      router.refresh()
    })
  }

  const handleDecisionSubmit = (): void => {
    if (!selectedProjectId) {
      toastError('Select a project before recording a decision')
      return
    }

    startTransition(async () => {
      const result = await createProjectDecision({
        projectId: selectedProjectId,
        taskId: selectedTaskId,
        title: decisionTitle,
        status: decisionStatus,
        rationaleMarkdown: decisionRationale,
        metadata: safeJsonParse(decisionMetadataJson, {
          source: 'project-state-console',
        }),
      })

      if (!result.success) {
        toastError(result.error || 'Failed to record decision')
        return
      }

      toastSuccess('Decision recorded')
      router.refresh()
    })
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Write-side controls</CardTitle>
        <CardDescription>
          Capture resumable checkpoints and expert decisions without leaving the operational console.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <section className="space-y-4 rounded-xl border border-border/60 p-4">
          <div className="flex items-center gap-2">
            <Save className="h-4 w-4 text-muted-foreground" />
            <div>
              <h3 className="text-sm font-medium">Create checkpoint</h3>
              <p className="text-xs text-muted-foreground">
                Persist next-step continuity for the selected task.
              </p>
            </div>
          </div>

          <div className="grid gap-3">
            <label className="grid gap-1.5">
              <span className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">
                Run
              </span>
              <select
                className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                value={runId}
                onChange={(event) => setRunId(event.target.value)}
                disabled={isPending}
              >
                <option value="">No active run</option>
                {taskRuns.map((run) => (
                  <option key={run.run_id} value={run.run_id}>
                    {run.actor_type}:{run.actor_id} · {run.run_id}
                  </option>
                ))}
              </select>
            </label>

            <Input
              label="Next step summary"
              value={nextStepSummary}
              onChange={(event) => setNextStepSummary(event.target.value)}
              disabled={isPending}
              placeholder="Resume by validating execution assumptions against current checkpoint"
            />

            <label className="grid gap-1.5">
              <span className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">
                Context summary JSON
              </span>
              <textarea
                value={contextSummaryJson}
                onChange={(event) => setContextSummaryJson(event.target.value)}
                disabled={isPending}
                className="min-h-[120px] w-full resize-y rounded-lg border border-input bg-transparent p-3 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              />
            </label>

            <label className="grid gap-1.5">
              <span className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">
                Resume state JSON
              </span>
              <textarea
                value={resumeStateJson}
                onChange={(event) => setResumeStateJson(event.target.value)}
                disabled={isPending}
                className="min-h-[100px] w-full resize-y rounded-lg border border-input bg-transparent p-3 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              />
            </label>

            <Button type="button" onClick={handleCheckpointSubmit} disabled={disableCheckpoint}>
              {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
              Create checkpoint
            </Button>
          </div>
        </section>

        <section className="space-y-4 rounded-xl border border-border/60 p-4">
          <div className="flex items-center gap-2">
            <RefreshCw className="h-4 w-4 text-muted-foreground" />
            <div>
              <h3 className="text-sm font-medium">Update task status</h3>
              <p className="text-xs text-muted-foreground">
                Transition the selected task to a new status with an optional reason.
              </p>
            </div>
          </div>

          <div className="grid gap-3">
            <label className="grid gap-1.5">
              <span className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">
                New status
              </span>
              <select
                className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                value={statusValue}
                onChange={(event) => setStatusValue(event.target.value)}
                disabled={isPending}
              >
                <option value="">Select a status…</option>
                <option value="pending">pending</option>
                <option value="in_progress">in_progress</option>
                <option value="blocked">blocked</option>
                <option value="done">done</option>
                <option value="cancelled">cancelled</option>
              </select>
            </label>

            <Input
              label="Reason (optional)"
              value={statusReason}
              onChange={(event) => setStatusReason(event.target.value)}
              disabled={isPending}
              placeholder="Brief explanation for the status change"
            />

            <Button
              type="button"
              onClick={handleStatusUpdateSubmit}
              disabled={disableStatusUpdate}
            >
              {isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
              Update status
            </Button>
          </div>
        </section>

        <section className="space-y-4 rounded-xl border border-border/60 p-4">
          <div className="flex items-center gap-2">
            <ClipboardPenLine className="h-4 w-4 text-muted-foreground" />
            <div>
              <h3 className="text-sm font-medium">Record decision</h3>
              <p className="text-xs text-muted-foreground">
                Persist an auditable decision trail for the current project and task.
              </p>
            </div>
          </div>

          <div className="grid gap-3">
            <Input
              label="Decision title"
              value={decisionTitle}
              onChange={(event) => setDecisionTitle(event.target.value)}
              disabled={isPending}
              placeholder="Adopt hybrid execution mode for overnight automation"
            />

            <label className="grid gap-1.5">
              <span className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">
                Status
              </span>
              <select
                className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                value={decisionStatus}
                onChange={(event) => setDecisionStatus(event.target.value)}
                disabled={isPending}
              >
                <option value="proposed">proposed</option>
                <option value="approved">approved</option>
                <option value="rejected">rejected</option>
                <option value="needs_more_evidence">needs_more_evidence</option>
              </select>
            </label>

            <label className="grid gap-1.5">
              <span className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">
                Rationale
              </span>
              <textarea
                value={decisionRationale}
                onChange={(event) => setDecisionRationale(event.target.value)}
                disabled={isPending}
                placeholder="Explain why this decision was made, what evidence supports it, and what tradeoffs remain."
                className="min-h-[140px] w-full resize-y rounded-lg border border-input bg-transparent p-3 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              />
            </label>

            <label className="grid gap-1.5">
              <span className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">
                Decision metadata JSON
              </span>
              <textarea
                value={decisionMetadataJson}
                onChange={(event) => setDecisionMetadataJson(event.target.value)}
                disabled={isPending}
                className="min-h-[100px] w-full resize-y rounded-lg border border-input bg-transparent p-3 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              />
            </label>

            <Button type="button" onClick={handleDecisionSubmit} disabled={disableDecision}>
              {isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle2 className="h-4 w-4" />
              )}
              Record decision
            </Button>
          </div>
        </section>
      </CardContent>
    </Card>
  )
}

export function ProjectStateWritePanel(props: ProjectStateWritePanelProps) {
  const formKey = `${props.selectedProjectId ?? 'no-project'}:${props.selectedTaskId ?? 'no-task'}:${props.contextProjection?.latest_checkpoint_id ?? 'no-checkpoint'}`

  return <ProjectStateWritePanelContent key={formKey} {...props} />
}
