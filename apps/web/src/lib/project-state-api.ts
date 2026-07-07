import 'server-only'

import { execFile } from 'node:child_process'
import { cookies } from 'next/headers'
import { readFile } from 'node:fs/promises'
import { join } from 'node:path'
import { promisify } from 'node:util'

const execFileAsync = promisify(execFile)

export interface ProjectStateProject {
  project_id: string
  name: string
  status: string
  adapter_id: string | null
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface ProjectStateOverview {
  project_id: string
  name: string
  status: string
  adapter_id: string | null
  total_tasks: number
  active_tasks: number
  blocked_tasks: number
  total_estimated_cost: number
  latest_checkpoint: {
    checkpoint_id: string
    task_id: string
    next_step_summary: string
    created_at: string
  } | null
  latest_decision: {
    decision_id: string
    title: string
    status: string
    created_at: string
  } | null
}

export interface ProjectStateTask {
  task_id: string
  project_id: string
  parent_task_id: string | null
  title: string
  status: string
  priority: string
  owner_type: string | null
  owner_id: string | null
  metadata: Record<string, unknown>
  constraints: Record<string, unknown>
  completion_criteria: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface TaskDependency {
  dependency_id: string
  task_id: string
  depends_on_task_id: string
  dependency_type: string
  created_at: string
}

export interface RunDetail {
  run_id: string
  project_id: string
  task_id: string
  task_title: string | null
  actor_type: string
  actor_id: string
  status: string
  started_at: string
  ended_at: string | null
  metadata: Record<string, unknown>
}

export interface DecisionDetail {
  decision_id: string
  project_id: string
  task_id: string | null
  title: string
  status: string
  rationale_markdown: string
  metadata: Record<string, unknown>
  created_at: string
}

export interface ActivityEvent {
  event_type: string
  occurred_at: string
  project_id: string
  task_id: string | null
  entity_id: string
  title: string
  summary: string
  metadata: Record<string, unknown>
}

export interface TokenUsageEvent {
  usage_event_id: string
  project_id: string
  task_id: string | null
  run_id: string | null
  provider: string
  model: string
  auth_mode: string
  prompt_tokens: number
  completion_tokens: number
  estimated_cost: number
  metadata: Record<string, unknown>
  created_at: string
}

export interface ProjectTimeSummary {
  project_id: string
  total_tasks: number
  completed_tasks: number
  remaining_tasks: number
  active_run_count: number
  explicit_estimate_task_count: number
  fallback_estimate_task_count: number
  remaining_explicit_estimate_task_count: number
  remaining_fallback_estimate_task_count: number
  estimated_total_minutes: number
  estimated_remaining_minutes: number
  active_run_elapsed_minutes: number
  project_age_minutes: number
  projected_completion_at: string | null
  confidence: string
  estimation_basis: string
}

export interface TaskContextProjection {
  project_id: string
  task_id: string
  generated_at: string
  objective: string
  status: string
  priority: string
  blockers: string[]
  dependencies: string[]
  constraints: Record<string, unknown>
  completion_criteria: Record<string, unknown>
  critical_decisions: Array<{
    decision_id: string
    title: string
    status: string
    created_at: string
  }>
  latest_checkpoint_id: string | null
  next_step: string | null
  relevant_artifacts: string[]
}

export interface DoctrineProjection {
  project_id: string
  task_id: string
  scope: string
  generated_at: string
  methodology: {
    active: string
    reason: string
    required_phases: string[]
  }
  policies: string[]
  mandatory_rules: Array<{
    rule_id: string
    summary: string
    severity: string
    check: string | null
  }>
  recommended_rules: Array<{
    rule_id: string
    summary: string
    severity: string
    check: string | null
  }>
  architecture_constraints: string[]
  quality_gates: string[]
  exception_policy: {
    human_approval_required_for_overrides: boolean
    pause_if_mandatory_rule_cannot_be_met: boolean
  }
}

export interface PolicyOption {
  capability_id: string
  label: string
  summary: string
  compatible_harnesses: string[]
}

export interface KnowledgeDistillationSystemHealth {
  record_count: number
  avg_quality_score: number
  rejection_rate: number
  p50_latency_ms: number
  p90_latency_ms: number
  t1_trend: Array<{
    day: string
    avg_t1_ms: number
  }>
}

export interface KnowledgeDistillationOutcomeMetrics {
  delta_velocity: number
  knowledge_yield: number
  planning_accuracy: number
}

export interface KnowledgeTemplateSummary {
  id: string
  brain_id: string
  template_name: string
  success_rate: number
  usage_count: number
  created_at: string
  last_used_at: string | null
}

export interface GapRegistryEntry {
  id: string
  title: string
  status: string
  detected_from: string
  objective_slug: string | null
  evidence: string[]
  impact: string
  urgency: string
  suggested_followup: string | null
  promotion_readiness: string
  promoted_objective_slug: string | null
  created_at_utc: string
  updated_at_utc: string
}

export interface GapDuplicateSuspect {
  gap_ids: string[]
  reasons: string[]
  shared_suggested_followup: string | null
  shared_normalized_title: string | null
}

export interface GapNextRecommendation {
  recommended_gap: GapRegistryEntry | null
  ranked_open_gaps: GapRegistryEntry[]
}

const DEFAULT_API_URL = 'http://localhost:8001'

async function readGapRegistryFile(): Promise<string | null> {
  const candidates = [
    join(process.cwd(), '.mm-flow', 'planning', 'gaps', 'gap-registry.json'),
    join(process.cwd(), '..', '.mm-flow', 'planning', 'gaps', 'gap-registry.json'),
  ]

  for (const candidate of candidates) {
    try {
      return await readFile(candidate, 'utf-8')
    } catch {
      continue
    }
  }

  return null
}

function gapRegistryHelperCandidates(): string[] {
  return [
    join(process.cwd(), '.mm-flow', 'commands', 'mm', 'gap-registry.py'),
    join(process.cwd(), '..', '.mm-flow', 'commands', 'mm', 'gap-registry.py'),
  ]
}

async function runGapRegistryCommand(
  args: string[]
): Promise<{ stdout: string; stderr: string } | null> {
  for (const helperPath of gapRegistryHelperCandidates()) {
    try {
      return await execFileAsync('python3', [helperPath, ...args], {
        cwd: process.cwd(),
      })
    } catch {
      continue
    }
  }

  return null
}

async function fetchProjectState<T>(path: string): Promise<T> {
  const apiUrl = process.env.AGENT_RUNTIME_URL || DEFAULT_API_URL
  const cookieStore = await cookies()
  const token = cookieStore.get('access_token')?.value

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`${apiUrl}${path}`, {
    method: 'GET',
    headers,
    next: { revalidate: 0 },
  })

  if (!response.ok) {
    throw new Error(`Project state fetch failed: ${response.status} ${response.statusText}`)
  }

  return (await response.json()) as T
}

function encodePathSegment(value: string): string {
  return encodeURIComponent(value)
}

export async function fetchProjectList(): Promise<ProjectStateProject[]> {
  const data = await fetchProjectState<{ projects: ProjectStateProject[] }>('/api/projects')
  return data.projects
}

export async function fetchProjectOverview(projectId: string): Promise<ProjectStateOverview> {
  return fetchProjectState<ProjectStateOverview>(
    `/api/projects/${encodePathSegment(projectId)}/overview`
  )
}

export async function fetchProjectTasks(projectId: string): Promise<ProjectStateTask[]> {
  const data = await fetchProjectState<{ tasks: ProjectStateTask[] }>(
    `/api/projects/${encodePathSegment(projectId)}/tasks`
  )
  return data.tasks
}

export async function fetchTaskDependencies(
  projectId: string,
  taskId: string
): Promise<TaskDependency[]> {
  const data = await fetchProjectState<{ dependencies: TaskDependency[] }>(
    `/api/projects/${encodePathSegment(projectId)}/tasks/${encodePathSegment(taskId)}/dependencies`
  )
  return data.dependencies
}

export async function fetchActiveRuns(projectId: string): Promise<RunDetail[]> {
  const data = await fetchProjectState<{ runs: RunDetail[] }>(
    `/api/projects/${encodePathSegment(projectId)}/runs/active`
  )
  return data.runs
}

export async function fetchProjectDecisions(projectId: string): Promise<DecisionDetail[]> {
  const data = await fetchProjectState<{ decisions: DecisionDetail[] }>(
    `/api/projects/${encodePathSegment(projectId)}/decisions`
  )
  return data.decisions
}

export async function fetchProjectActivity(projectId: string): Promise<ActivityEvent[]> {
  const data = await fetchProjectState<{ events: ActivityEvent[] }>(
    `/api/projects/${encodePathSegment(projectId)}/activity`
  )
  return data.events
}

export async function fetchProjectTokenUsage(projectId: string): Promise<TokenUsageEvent[]> {
  const data = await fetchProjectState<{ events: TokenUsageEvent[] }>(
    `/api/projects/${encodePathSegment(projectId)}/token-usage`
  )
  return data.events
}

export async function fetchProjectTimeSummary(projectId: string): Promise<ProjectTimeSummary> {
  return fetchProjectState<ProjectTimeSummary>(
    `/api/projects/${encodePathSegment(projectId)}/time-summary`
  )
}

export async function fetchTaskContextProjection(
  projectId: string,
  taskId: string
): Promise<TaskContextProjection> {
  return fetchProjectState<TaskContextProjection>(
    `/api/projects/${encodePathSegment(projectId)}/tasks/${encodePathSegment(taskId)}/context-projection`
  )
}

export async function fetchTaskDoctrineProjection(
  projectId: string,
  taskId: string
): Promise<DoctrineProjection> {
  return fetchProjectState<DoctrineProjection>(
    `/api/projects/${encodePathSegment(projectId)}/tasks/${encodePathSegment(taskId)}/doctrine-projection`
  )
}

export async function fetchPolicyOptions(): Promise<PolicyOption[]> {
  const data = await fetchProjectState<{ policies: PolicyOption[] }>('/api/policies')
  return data.policies
}

export async function fetchKnowledgeDistillationSystemHealth(): Promise<KnowledgeDistillationSystemHealth> {
  return fetchProjectState<KnowledgeDistillationSystemHealth>('/api/analytics/system-health')
}

export async function fetchKnowledgeDistillationOutcomeMetrics(): Promise<KnowledgeDistillationOutcomeMetrics> {
  return fetchProjectState<KnowledgeDistillationOutcomeMetrics>('/api/analytics/outcome-metrics')
}

export async function fetchKnowledgeTemplates(
  limit = 5
): Promise<KnowledgeTemplateSummary[]> {
  return fetchProjectState<KnowledgeTemplateSummary[]>(`/api/analytics/templates?limit=${limit}`)
}

export async function fetchGapRegistryEntries(): Promise<GapRegistryEntry[]> {
  const content = await readGapRegistryFile()
  if (!content) return []

  try {
    const data = JSON.parse(content) as { gaps?: GapRegistryEntry[] }
    return Array.isArray(data.gaps) ? data.gaps : []
  } catch {
    return []
  }
}

export async function fetchGapDuplicateSuspects(): Promise<GapDuplicateSuspect[]> {
  const result = await runGapRegistryCommand(['duplicates'])
  if (!result) return []

  try {
    const data = JSON.parse(result.stdout) as { suspects?: GapDuplicateSuspect[] }
    return Array.isArray(data.suspects) ? data.suspects : []
  } catch {
    return []
  }
}

export async function fetchGapNextRecommendation(): Promise<GapNextRecommendation> {
  const result = await runGapRegistryCommand(['next'])
  if (!result) {
    return {
      recommended_gap: null,
      ranked_open_gaps: [],
    }
  }

  try {
    const data = JSON.parse(result.stdout) as GapNextRecommendation
    return {
      recommended_gap: data.recommended_gap ?? null,
      ranked_open_gaps: Array.isArray(data.ranked_open_gaps) ? data.ranked_open_gaps : [],
    }
  } catch {
    return {
      recommended_gap: null,
      ranked_open_gaps: [],
    }
  }
}
