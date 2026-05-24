import Link from 'next/link'
import {
  Activity,
  ArrowRight,
  Bot,
  CheckCircle2,
  Clock3,
  FileCode2,
  GitBranch,
  ShieldCheck,
  Wallet,
} from 'lucide-react'

import type {
  ActivityEvent,
  DecisionDetail,
  DoctrineProjection,
  ProjectStateOverview,
  ProjectStateProject,
  ProjectStateTask,
  ProjectTimeSummary,
  RunDetail,
  TaskContextProjection,
  TaskDependency,
  TokenUsageEvent,
} from '@/lib/project-state-api'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { cn } from '@/lib/utils'
import { TaskGraphPanel } from '@/components/project-state/TaskGraphPanel'
import { ProjectStateWritePanel } from '@/components/project-state/ProjectStateWritePanel'

export interface ProjectStateDashboardProps {
  projects: ProjectStateProject[]
  selectedProjectId: string | null
  selectedTaskId: string | null
  overview: ProjectStateOverview | null
  timeSummary: ProjectTimeSummary | null
  tasks: ProjectStateTask[]
  dependencies: TaskDependency[]
  runs: RunDetail[]
  decisions: DecisionDetail[]
  activity: ActivityEvent[]
  tokenUsage: TokenUsageEvent[]
  contextProjection: TaskContextProjection | null
  doctrineProjection: DoctrineProjection | null
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 2,
  }).format(value)
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  }).format(new Date(value))
}

function formatMinutes(totalMinutes: number): string {
  if (totalMinutes <= 0) return '0m'
  const hours = Math.floor(totalMinutes / 60)
  const minutes = totalMinutes % 60

  if (hours === 0) return `${minutes}m`
  if (minutes === 0) return `${hours}h`
  return `${hours}h ${minutes}m`
}

function statusVariant(status: string): 'default' | 'secondary' | 'warning' | 'success' | 'destructive' {
  switch (status) {
    case 'active':
    case 'in_progress':
    case 'running':
    case 'approved':
      return 'success'
    case 'blocked':
    case 'warning':
      return 'warning'
    case 'error':
    case 'failed':
    case 'rejected':
      return 'destructive'
    default:
      return 'secondary'
  }
}

function MetricCard({
  label,
  value,
  hint,
  icon: Icon,
}: {
  label: string
  value: string | number
  hint: string
  icon: React.ComponentType<{ className?: string }>
}) {
  return (
    <Card size="sm" className="bg-background/70 backdrop-blur">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardDescription>{label}</CardDescription>
          <Icon className="h-4 w-4 text-muted-foreground" />
        </div>
        <CardTitle className="text-2xl">{value}</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground">{hint}</p>
      </CardContent>
    </Card>
  )
}

export function ProjectStateDashboard({
  projects,
  selectedProjectId,
  selectedTaskId,
  overview,
  timeSummary,
  tasks,
  dependencies,
  runs,
  decisions,
  activity,
  tokenUsage,
  contextProjection,
  doctrineProjection,
}: ProjectStateDashboardProps) {
  if (projects.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center p-6">
        <Card className="max-w-lg">
          <CardHeader>
            <CardTitle>No project state data yet</CardTitle>
            <CardDescription>
              The backend read-side is ready, but no projects have been persisted into
              <code className="mx-1 rounded bg-muted px-1.5 py-0.5 text-xs">project_state</code>
              yet.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_rgba(99,102,241,0.08),_transparent_35%),linear-gradient(to_bottom,_transparent,_rgba(15,23,42,0.04))]">
      <div className="border-b border-border/60 bg-background/85 backdrop-blur">
        <div className="mx-auto flex max-w-[1600px] items-end justify-between gap-4 px-6 py-6">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.22em] text-muted-foreground">
              MasterMind Harness
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight">Project State Console</h1>
            <p className="mt-1 max-w-3xl text-sm text-muted-foreground">
              Live operational memory for projects: tasks, runs, decisions, checkpoints, cost,
              context and doctrine projections.
            </p>
          </div>
          {overview ? (
            <div className="text-right">
              <p className="text-xs uppercase tracking-[0.18em] text-muted-foreground">
                Selected project
              </p>
              <div className="mt-2 flex items-center justify-end gap-2">
                <span className="text-lg font-medium">{overview.name}</span>
                <Badge variant={statusVariant(overview.status)}>{overview.status}</Badge>
              </div>
            </div>
          ) : null}
        </div>
      </div>

      <div className="mx-auto grid max-w-[1600px] gap-6 px-6 py-6 xl:grid-cols-[280px_minmax(0,1fr)_380px]">
        <aside className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Projects</CardTitle>
              <CardDescription>Choose a project persisted in the new project_state read model.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {projects.map((project) => {
                const isActive = project.project_id === selectedProjectId
                return (
                  <Link
                    key={project.project_id}
                    href={`/project-state?project=${project.project_id}`}
                    className={cn(
                      'block rounded-xl border p-3 transition-colors',
                      isActive
                        ? 'border-primary bg-primary/5'
                        : 'border-border/70 bg-background hover:bg-muted/50'
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <p className="font-medium">{project.name}</p>
                      <Badge variant={statusVariant(project.status)}>{project.status}</Badge>
                    </div>
                    <p className="mt-1 text-xs text-muted-foreground">{project.project_id}</p>
                    <p className="mt-2 text-xs text-muted-foreground">
                      Updated {formatDate(project.updated_at)}
                    </p>
                  </Link>
                )
              })}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Task graph</CardTitle>
              <CardDescription>Fast drill-down into tasks and dependency edges.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              {tasks.slice(0, 8).map((task) => {
                const isSelected = task.task_id === selectedTaskId
                return (
                  <Link
                    key={task.task_id}
                    href={`/project-state?project=${selectedProjectId}&task=${task.task_id}`}
                    className={cn(
                      'block rounded-lg border p-3 transition-colors',
                      isSelected
                        ? 'border-primary bg-primary/5'
                        : 'border-border/60 hover:bg-muted/50'
                    )}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0">
                        <p className="truncate text-sm font-medium">{task.title}</p>
                        <p className="mt-1 text-xs text-muted-foreground">{task.task_id}</p>
                      </div>
                      <Badge variant={statusVariant(task.status)}>{task.status}</Badge>
                    </div>
                  </Link>
                )
              })}
            </CardContent>
          </Card>
        </aside>

        <main className="space-y-6">
          {overview ? (
            <>
              <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <MetricCard
                  label="Total tasks"
                  value={overview.total_tasks}
                  hint="Tracked in the structured task graph."
                  icon={GitBranch}
                />
                <MetricCard
                  label="Active tasks"
                  value={overview.active_tasks}
                  hint="Currently progressing tasks."
                  icon={Activity}
                />
                <MetricCard
                  label="Blocked tasks"
                  value={overview.blocked_tasks}
                  hint="Needs intervention or dependency clearance."
                  icon={ShieldCheck}
                />
                <MetricCard
                  label="Estimated cost"
                  value={formatCurrency(overview.total_estimated_cost)}
                  hint="Aggregated from token usage telemetry."
                  icon={Wallet}
                />
              </section>

              {timeSummary ? (
                <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                  <MetricCard
                    label="Remaining ETA"
                    value={formatMinutes(timeSummary.estimated_remaining_minutes)}
                    hint={`Confidence: ${timeSummary.confidence}`}
                    icon={Clock3}
                  />
                  <MetricCard
                    label="Completed tasks"
                    value={`${timeSummary.completed_tasks}/${timeSummary.total_tasks}`}
                    hint="Completed vs total project tasks."
                    icon={CheckCircle2}
                  />
                  <MetricCard
                    label="Project age"
                    value={formatMinutes(timeSummary.project_age_minutes)}
                    hint="Elapsed wall-clock time since project creation."
                    icon={Activity}
                  />
                  <MetricCard
                    label="Active run time"
                    value={formatMinutes(timeSummary.active_run_elapsed_minutes)}
                    hint="Accumulated wall-clock time across current active runs."
                    icon={Bot}
                  />
                </section>
              ) : null}

              <section className="grid gap-6 2xl:grid-cols-[1.3fr_0.9fr]">
                <Card className="2xl:col-span-2">
                  <CardHeader>
                    <CardTitle>Task graph</CardTitle>
                    <CardDescription>
                      Visual dependency map for the selected project. Click a node to inspect its context and doctrine.
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <TaskGraphPanel
                      projectId={selectedProjectId || ''}
                      selectedTaskId={selectedTaskId}
                      tasks={tasks}
                      dependencies={dependencies}
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Execution overview</CardTitle>
                    <CardDescription>Tasks, active runs and the next resumable checkpoint.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {timeSummary?.projected_completion_at ? (
                      <div className="rounded-xl border border-border/70 bg-primary/5 p-4">
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <p className="text-sm font-medium">Projected completion</p>
                            <p className="mt-1 text-sm text-muted-foreground">
                              {formatDate(timeSummary.projected_completion_at)}
                            </p>
                          </div>
                          <Badge variant="outline">{timeSummary.confidence}</Badge>
                        </div>
                        <p className="mt-2 text-xs text-muted-foreground">
                          {timeSummary.estimation_basis}
                        </p>
                      </div>
                    ) : null}

                    <div className="grid gap-3 md:grid-cols-2">
                      <div className="rounded-xl border border-border/70 bg-muted/25 p-4">
                        <div className="flex items-center gap-2 text-sm font-medium">
                          <Clock3 className="h-4 w-4 text-muted-foreground" />
                          Latest checkpoint
                        </div>
                        {overview.latest_checkpoint ? (
                          <div className="mt-3 space-y-1">
                            <p className="text-sm font-medium">{overview.latest_checkpoint.task_id}</p>
                            <p className="text-sm text-muted-foreground">
                              {overview.latest_checkpoint.next_step_summary}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {formatDate(overview.latest_checkpoint.created_at)}
                            </p>
                          </div>
                        ) : (
                          <p className="mt-3 text-sm text-muted-foreground">No checkpoint yet.</p>
                        )}
                      </div>

                      <div className="rounded-xl border border-border/70 bg-muted/25 p-4">
                        <div className="flex items-center gap-2 text-sm font-medium">
                          <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
                          Latest decision
                        </div>
                        {overview.latest_decision ? (
                          <div className="mt-3 space-y-1">
                            <p className="text-sm font-medium">{overview.latest_decision.title}</p>
                            <Badge variant={statusVariant(overview.latest_decision.status)}>
                              {overview.latest_decision.status}
                            </Badge>
                            <p className="text-xs text-muted-foreground">
                              {formatDate(overview.latest_decision.created_at)}
                            </p>
                          </div>
                        ) : (
                          <p className="mt-3 text-sm text-muted-foreground">No decision recorded yet.</p>
                        )}
                      </div>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-medium">Active runs</h3>
                        <Badge variant="secondary">{runs.length}</Badge>
                      </div>
                      {runs.length > 0 ? (
                        <div className="space-y-2">
                          {runs.slice(0, 5).map((run) => (
                            <div
                              key={run.run_id}
                              className="flex items-center justify-between rounded-xl border border-border/60 px-3 py-2"
                            >
                              <div className="min-w-0">
                                <p className="truncate text-sm font-medium">{run.task_title || run.task_id}</p>
                                <p className="text-xs text-muted-foreground">
                                  {run.actor_type}:{run.actor_id} • {formatDate(run.started_at)}
                                </p>
                              </div>
                              <Badge variant={statusVariant(run.status)}>{run.status}</Badge>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground">No active runs right now.</p>
                      )}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Cost telemetry</CardTitle>
                    <CardDescription>Recent usage events grouped by provider and model.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {tokenUsage.slice(0, 6).map((event) => (
                      <div
                        key={event.usage_event_id}
                        className="rounded-xl border border-border/60 bg-muted/20 p-3"
                      >
                        <div className="flex items-center justify-between gap-3">
                          <div>
                            <p className="text-sm font-medium">
                              {event.provider} · {event.model}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {event.prompt_tokens} prompt / {event.completion_tokens} completion
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-sm font-medium">{formatCurrency(event.estimated_cost)}</p>
                            <p className="text-xs text-muted-foreground">{formatDate(event.created_at)}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                    {tokenUsage.length === 0 ? (
                      <p className="text-sm text-muted-foreground">No token usage captured yet.</p>
                    ) : null}
                  </CardContent>
                </Card>
              </section>

              <section className="grid gap-6 xl:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Decision trail</CardTitle>
                    <CardDescription>Recent expert decisions recorded for this project.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {decisions.slice(0, 5).map((decision) => (
                      <div key={decision.decision_id} className="rounded-xl border border-border/60 p-4">
                        <div className="flex items-center justify-between gap-3">
                          <p className="font-medium">{decision.title}</p>
                          <Badge variant={statusVariant(decision.status)}>{decision.status}</Badge>
                        </div>
                        <p className="mt-2 line-clamp-3 text-sm text-muted-foreground">
                          {decision.rationale_markdown}
                        </p>
                      </div>
                    ))}
                    {decisions.length === 0 ? (
                      <p className="text-sm text-muted-foreground">No decisions recorded yet.</p>
                    ) : null}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Activity feed</CardTitle>
                    <CardDescription>Recent operational events from the read-side timeline.</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {activity.slice(0, 6).map((event) => (
                      <div key={`${event.event_type}-${event.entity_id}`} className="flex gap-3">
                        <div className="mt-1 rounded-full border border-border p-1.5">
                          <Activity className="h-3.5 w-3.5 text-muted-foreground" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium">{event.title}</p>
                          <p className="text-sm text-muted-foreground">{event.summary}</p>
                          <p className="mt-1 text-xs text-muted-foreground">
                            {event.event_type} • {formatDate(event.occurred_at)}
                          </p>
                        </div>
                      </div>
                    ))}
                    {activity.length === 0 ? (
                      <p className="text-sm text-muted-foreground">No activity recorded yet.</p>
                    ) : null}
                  </CardContent>
                </Card>
              </section>
            </>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Project not found</CardTitle>
                <CardDescription>Select a valid project from the left rail.</CardDescription>
              </CardHeader>
            </Card>
          )}
        </main>

        <aside className="space-y-6">
          <ProjectStateWritePanel
            selectedProjectId={selectedProjectId}
            selectedTaskId={selectedTaskId}
            runs={runs}
            contextProjection={contextProjection}
          />

          <Card>
            <CardHeader>
              <CardTitle>Task context projection</CardTitle>
              <CardDescription>High-signal context for the selected task.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {contextProjection ? (
                <>
                  <div>
                    <p className="text-sm font-medium">{contextProjection.objective}</p>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      <Badge variant={statusVariant(contextProjection.status)}>
                        {contextProjection.status}
                      </Badge>
                      <Badge variant="outline">{contextProjection.priority}</Badge>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      Next step
                    </p>
                    <p className="text-sm">{contextProjection.next_step || 'No next step captured yet.'}</p>
                  </div>

                  <div className="space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      Blockers
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {contextProjection.blockers.length > 0 ? (
                        contextProjection.blockers.map((blocker) => (
                          <Badge key={blocker} variant="warning">
                            {blocker}
                          </Badge>
                        ))
                      ) : (
                        <span className="text-sm text-muted-foreground">No blockers recorded.</span>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      Dependencies
                    </p>
                    <div className="space-y-2">
                      {dependencies.length > 0 ? (
                        dependencies.map((dependency) => (
                          <div
                            key={dependency.dependency_id}
                            className="flex items-center justify-between rounded-lg border border-border/60 px-3 py-2"
                          >
                            <span className="text-sm">{dependency.depends_on_task_id}</span>
                            <Badge variant="outline">{dependency.dependency_type}</Badge>
                          </div>
                        ))
                      ) : (
                        <span className="text-sm text-muted-foreground">No dependency edges for this task.</span>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      Critical decisions
                    </p>
                    <div className="space-y-2">
                      {contextProjection.critical_decisions.length > 0 ? (
                        contextProjection.critical_decisions.map((decision) => (
                          <div key={decision.decision_id} className="rounded-lg border border-border/60 p-3">
                            <p className="text-sm font-medium">{decision.title}</p>
                            <p className="mt-1 text-xs text-muted-foreground">
                              {decision.status} • {formatDate(decision.created_at)}
                            </p>
                          </div>
                        ))
                      ) : (
                        <span className="text-sm text-muted-foreground">No task-scoped decisions yet.</span>
                      )}
                    </div>
                  </div>
                </>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Select a task from the left rail to inspect its context projection.
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Doctrine projection</CardTitle>
              <CardDescription>Methodology, rules and quality gates for execution.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {doctrineProjection ? (
                <>
                  <div className="rounded-xl border border-border/60 bg-muted/25 p-4">
                    <div className="flex items-center gap-2">
                      <Bot className="h-4 w-4 text-muted-foreground" />
                      <p className="text-sm font-medium">{doctrineProjection.methodology.active}</p>
                    </div>
                    <p className="mt-2 text-sm text-muted-foreground">
                      {doctrineProjection.methodology.reason}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {doctrineProjection.methodology.required_phases.map((phase) => (
                        <Badge key={phase} variant="outline">
                          {phase}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      Mandatory rules
                    </p>
                    {doctrineProjection.mandatory_rules.map((rule) => (
                      <div key={rule.rule_id} className="rounded-lg border border-border/60 p-3">
                        <div className="flex items-start gap-2">
                          <ShieldCheck className="mt-0.5 h-4 w-4 text-muted-foreground" />
                          <div>
                            <p className="text-sm font-medium">{rule.summary}</p>
                            {rule.check ? (
                              <p className="mt-1 text-xs text-muted-foreground">{rule.check}</p>
                            ) : null}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      Quality gates
                    </p>
                    {doctrineProjection.quality_gates.map((gate) => (
                      <div key={gate} className="flex items-start gap-2 rounded-lg border border-border/60 p-3">
                        <ArrowRight className="mt-0.5 h-4 w-4 text-muted-foreground" />
                        <p className="text-sm">{gate}</p>
                      </div>
                    ))}
                  </div>

                  <div className="space-y-2">
                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                      Architecture constraints
                    </p>
                    {doctrineProjection.architecture_constraints.map((constraint) => (
                      <div
                        key={constraint}
                        className="flex items-start gap-2 rounded-lg border border-border/60 p-3"
                      >
                        <FileCode2 className="mt-0.5 h-4 w-4 text-muted-foreground" />
                        <p className="text-sm">{constraint}</p>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Select a task to inspect the projected methodology and mandatory rules.
                </p>
              )}
            </CardContent>
          </Card>
        </aside>
      </div>
    </div>
  )
}
