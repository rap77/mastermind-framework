'use client'

import { useMemo, useState, useTransition } from 'react'
import { useRouter } from 'next/navigation'
import { CheckCircle2, ClipboardPenLine, Loader2, Save, RefreshCw } from 'lucide-react'

import {
  createProjectCheckpoint,
  createProjectDecision,
  updateProjectDoctrine,
  updateProjectTaskStatus,
} from '@/app/actions/project-state'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { toastError, toastSuccess } from '@/lib/toast'
import type {
  DoctrineProjection,
  PolicyOption,
  RunDetail,
  TaskContextProjection,
} from '@/lib/project-state-api'

const DEFAULT_DECISION_STATUS = 'proposed'

const BASE_METHODLOGY_OPTIONS = [
  {
    value: 'Discovery',
    label: 'Discovery',
    description: 'Interview the problem space before committing to implementation work.',
    requiredPhases: ['discover', 'plan', 'verify'],
  },
  {
    value: 'Onboarding',
    label: 'Onboarding',
    description: 'Prepare the repo and runtime so the selected workflow can run safely.',
    requiredPhases: ['discover', 'plan', 'verify'],
  },
  {
    value: 'AI-DLC',
    label: 'AI-DLC',
    description: 'Use the discovery-to-delivery loop for structured product and delivery work.',
    requiredPhases: ['discover', 'plan', 'verify'],
  },
  {
    value: 'SDD',
    label: 'SDD',
    description: 'Start from spec, then drive implementation from explicit requirements.',
    requiredPhases: ['discover', 'plan', 'verify'],
  },
  {
    value: 'TDD',
    label: 'TDD',
    description: 'Let tests define behavior before implementation.',
    requiredPhases: ['spec', 'implementation', 'review'],
  },
] as const

type MethodologyOption = (typeof BASE_METHODLOGY_OPTIONS)[number]

const METHODOLOGY_ALLOWED_HARNESSES: Record<string, string[]> = {
  Discovery: ['execution-default'],
  Onboarding: ['execution-default'],
  'AI-DLC': ['execution-default', 'verification-default'],
  SDD: ['execution-default', 'verification-default'],
  TDD: ['execution-default', 'verification-default', 'review-default'],
}

function buildMethodologyOptions(
  currentMethodology: string,
  currentReason: string,
  currentRequiredPhases: string[]
): MethodologyOption[] {
  if (!currentMethodology) return [...BASE_METHODLOGY_OPTIONS]

  if (BASE_METHODLOGY_OPTIONS.some((option) => option.value === currentMethodology)) {
    return [...BASE_METHODLOGY_OPTIONS]
  }

  return [
    {
      value: currentMethodology,
      label: currentMethodology,
      description:
        currentReason || 'Custom methodology preserved from the current doctrine projection.',
      requiredPhases: currentRequiredPhases,
    },
    ...BASE_METHODLOGY_OPTIONS,
  ]
}

function buildSelectedPolicies(
  projection: DoctrineProjection | null,
  policyOptions: PolicyOption[]
): string[] {
  if (projection?.policies.length) return projection.policies

  const knownPolicyRuleIds = new Set(policyOptions.map((option) => option.capability_id))
  return (projection?.mandatory_rules ?? [])
    .map((rule) => rule.rule_id)
    .filter((ruleId) => knownPolicyRuleIds.has(ruleId))
}

function isPolicyCompatibleWithMethodology(
  policy: PolicyOption,
  methodology: string,
  policyOptions: PolicyOption[]
): boolean {
  const allowedHarnesses = new Set(
    METHODOLOGY_ALLOWED_HARNESSES[methodology] ??
      policyOptions.flatMap((option) => option.compatible_harnesses)
  )

  return policy.compatible_harnesses.some((harnessId) => allowedHarnesses.has(harnessId))
}

function allowedHarnessesForMethodology(
  methodology: string,
  policyOptions: PolicyOption[]
): string[] {
  return (
    METHODOLOGY_ALLOWED_HARNESSES[methodology] ??
    Array.from(new Set(policyOptions.flatMap((option) => option.compatible_harnesses)))
  )
}

interface ProjectStateWritePanelProps {
  selectedProjectId: string | null
  selectedTaskId: string | null
  runs: RunDetail[]
  contextProjection: TaskContextProjection | null
  doctrineProjection: DoctrineProjection | null
  policyOptions: PolicyOption[]
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
  doctrineProjection,
  policyOptions,
}: ProjectStateWritePanelProps) {
  const router = useRouter()
  const [isPending, startTransition] = useTransition()
  const [nextStepSummary, setNextStepSummary] = useState(contextProjection?.next_step ?? '')
  const [methodologyValue, setMethodologyValue] = useState(doctrineProjection?.methodology.active ?? '')
  const [methodologyReason, setMethodologyReason] = useState(doctrineProjection?.methodology.reason ?? '')
  const [selectedPolicyIds, setSelectedPolicyIds] = useState(
    buildSelectedPolicies(doctrineProjection, policyOptions)
  )
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
  const methodologyOptions = useMemo(
    () =>
      buildMethodologyOptions(
        doctrineProjection?.methodology.active ?? '',
        doctrineProjection?.methodology.reason ?? '',
        doctrineProjection?.methodology.required_phases ?? []
      ),
    [
      doctrineProjection?.methodology.active,
      doctrineProjection?.methodology.reason,
      doctrineProjection?.methodology.required_phases,
    ]
  )
  const disableCheckpoint = !selectedProjectId || !selectedTaskId || !nextStepSummary.trim() || isPending
  const disableDecision = !selectedProjectId || !decisionTitle.trim() || !decisionRationale.trim() || isPending
  const disableStatusUpdate = !selectedProjectId || !selectedTaskId || !statusValue.trim() || isPending
  const disableDoctrineUpdate = !selectedProjectId || !methodologyValue.trim() || isPending

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

  const handleDoctrineSubmit = (): void => {
    if (!selectedProjectId) {
      toastError('Select a project before updating the methodology')
      return
    }

    const selectedOption = methodologyOptions.find((option) => option.value === methodologyValue)
    const reason = methodologyReason.trim() || selectedOption?.description || ''

    startTransition(async () => {
      const result = await updateProjectDoctrine({
        projectId: selectedProjectId,
        methodology: methodologyValue,
        methodologyReason: reason,
        requiredPhases: selectedOption?.requiredPhases ?? [],
        policies: selectedPolicyIds,
      })

      if (!result.success) {
        toastError(result.error || 'Failed to update methodology')
        return
      }

      toastSuccess('Methodology updated')
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
            <ClipboardPenLine className="h-4 w-4 text-muted-foreground" />
            <div>
              <h3 className="text-sm font-medium">Policies</h3>
              <p className="text-xs text-muted-foreground">
                Apply transversal doctrine rules without changing the selected methodology.
              </p>
            </div>
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <div className="md:col-span-2 rounded-lg border border-dashed border-border/60 px-3 py-2 text-xs text-muted-foreground">
              Active methodology:{' '}
              <span className="font-medium text-foreground">
                {methodologyValue || 'none selected'}
              </span>
              {methodologyValue ? (
                <span>
                  {' '}
                  permits:{' '}
                  <span className="font-medium text-foreground">
                    {allowedHarnessesForMethodology(methodologyValue, policyOptions).join(', ')}
                  </span>
                </span>
              ) : null}
            </div>

            {policyOptions.map((policy) => {
              const compatibleWithMethodology = isPolicyCompatibleWithMethodology(
                policy,
                methodologyValue,
                policyOptions
              )
              const isSelected = selectedPolicyIds.includes(policy.capability_id)

              return (
                <label
                  key={policy.capability_id}
                  className="flex items-start gap-3 rounded-lg border border-border/60 p-3"
                >
                  <input
                    type="checkbox"
                    className="mt-1 h-4 w-4 rounded border-input"
                    checked={isSelected}
                    onChange={(event) => {
                      setSelectedPolicyIds((current) =>
                        event.target.checked
                          ? [...current, policy.capability_id]
                          : current.filter((ruleId) => ruleId !== policy.capability_id)
                      )
                    }}
                    disabled={isPending || (!isSelected && !compatibleWithMethodology)}
                  />
                  <div className="space-y-1">
                    <p className="text-sm font-medium">{policy.label}</p>
                    <p className="text-xs text-muted-foreground">{policy.summary}</p>
                    <p className="text-[11px] uppercase tracking-[0.14em] text-muted-foreground">
                      Compatible: {policy.compatible_harnesses.join(', ')}
                    </p>
                    {!compatibleWithMethodology ? (
                      <p className="text-[11px] text-amber-600">
                        No disponible en {methodologyValue || 'la metodología seleccionada'}.
                      </p>
                    ) : null}
                  </div>
                </label>
              )
            })}
          </div>
        </section>

        <section className="space-y-4 rounded-xl border border-border/60 p-4">
          <div className="flex items-center gap-2">
            <ClipboardPenLine className="h-4 w-4 text-muted-foreground" />
            <div>
              <h3 className="text-sm font-medium">Select methodology</h3>
              <p className="text-xs text-muted-foreground">
                Choose the top-level harness for the current project doctrine.
              </p>
            </div>
          </div>

          <div className="grid gap-3">
            <label className="grid gap-1.5">
              <span className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">
                Methodology
              </span>
              <select
                className="h-8 rounded-lg border border-input bg-transparent px-2.5 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                value={methodologyValue}
                onChange={(event) => {
                  const nextValue = event.target.value
                  setMethodologyValue(nextValue)
                  if (!methodologyReason.trim()) {
                    const nextOption = methodologyOptions.find((option) => option.value === nextValue)
                    setMethodologyReason(nextOption?.description ?? '')
                  }
                }}
                disabled={isPending}
              >
                <option value="">Select a methodology…</option>
                {methodologyOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <label className="grid gap-1.5">
              <span className="text-xs font-medium uppercase tracking-[0.16em] text-muted-foreground">
                Reason
              </span>
              <textarea
                value={methodologyReason}
                onChange={(event) => setMethodologyReason(event.target.value)}
                disabled={isPending}
                placeholder="Explain why this methodology fits the current project and constraints."
                className="min-h-[96px] w-full resize-y rounded-lg border border-input bg-transparent p-3 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              />
            </label>

            <Button type="button" onClick={handleDoctrineSubmit} disabled={disableDoctrineUpdate}>
              {isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <ClipboardPenLine className="h-4 w-4" />}
              Update methodology
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
  const formKey = `${props.selectedProjectId ?? 'no-project'}:${props.selectedTaskId ?? 'no-task'}:${props.contextProjection?.latest_checkpoint_id ?? 'no-checkpoint'}:${props.doctrineProjection?.methodology.active ?? 'no-methodology'}:${props.doctrineProjection?.methodology.reason ?? 'no-reason'}:${(props.doctrineProjection?.policies ?? []).join('|') || 'no-policy-rules'}`

  return <ProjectStateWritePanelContent key={formKey} {...props} />
}
