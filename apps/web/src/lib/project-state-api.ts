import 'server-only'

import { cookies } from 'next/headers'

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

const DEFAULT_API_URL = 'http://localhost:8001'

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

export async function fetchProjectList(): Promise<ProjectStateProject[]> {
  const data = await fetchProjectState<{ projects: ProjectStateProject[] }>('/api/projects')
  return data.projects
}

export async function fetchProjectOverview(projectId: string): Promise<ProjectStateOverview> {
  return fetchProjectState<ProjectStateOverview>(`/api/projects/${projectId}/overview`)
}

export async function fetchProjectTasks(projectId: string): Promise<ProjectStateTask[]> {
  const data = await fetchProjectState<{ tasks: ProjectStateTask[] }>(
    `/api/projects/${projectId}/tasks`
  )
  return data.tasks
}

export async function fetchTaskDependencies(
  projectId: string,
  taskId: string
): Promise<TaskDependency[]> {
  const data = await fetchProjectState<{ dependencies: TaskDependency[] }>(
    `/api/projects/${projectId}/tasks/${taskId}/dependencies`
  )
  return data.dependencies
}

export async function fetchActiveRuns(projectId: string): Promise<RunDetail[]> {
  const data = await fetchProjectState<{ runs: RunDetail[] }>(
    `/api/projects/${projectId}/runs/active`
  )
  return data.runs
}

export async function fetchProjectDecisions(projectId: string): Promise<DecisionDetail[]> {
  const data = await fetchProjectState<{ decisions: DecisionDetail[] }>(
    `/api/projects/${projectId}/decisions`
  )
  return data.decisions
}

export async function fetchProjectActivity(projectId: string): Promise<ActivityEvent[]> {
  const data = await fetchProjectState<{ events: ActivityEvent[] }>(
    `/api/projects/${projectId}/activity`
  )
  return data.events
}

export async function fetchProjectTokenUsage(projectId: string): Promise<TokenUsageEvent[]> {
  const data = await fetchProjectState<{ events: TokenUsageEvent[] }>(
    `/api/projects/${projectId}/token-usage`
  )
  return data.events
}

export async function fetchProjectTimeSummary(projectId: string): Promise<ProjectTimeSummary> {
  return fetchProjectState<ProjectTimeSummary>(`/api/projects/${projectId}/time-summary`)
}

export async function fetchTaskContextProjection(
  projectId: string,
  taskId: string
): Promise<TaskContextProjection> {
  return fetchProjectState<TaskContextProjection>(
    `/api/projects/${projectId}/tasks/${taskId}/context-projection`
  )
}

export async function fetchTaskDoctrineProjection(
  projectId: string,
  taskId: string
): Promise<DoctrineProjection> {
  return fetchProjectState<DoctrineProjection>(
    `/api/projects/${projectId}/tasks/${taskId}/doctrine-projection`
  )
}
