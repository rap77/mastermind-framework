import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'

import { ProjectStateDashboard } from '../ProjectStateDashboard'
import type { ProjectStateDashboardProps } from '../ProjectStateDashboard'

vi.mock('@/components/project-state/TaskGraphPanel', () => ({
  TaskGraphPanel: () => <div data-testid="task-graph-panel" />,
}))

vi.mock('@/components/project-state/ProjectStateWritePanel', () => ({
  ProjectStateWritePanel: () => <div data-testid="project-state-write-panel" />,
}))

vi.mock('@/components/ws/BrainStatusFeed', () => ({
  BrainStatusFeed: () => <div data-testid="brain-status-feed" />,
}))

const baseProps: ProjectStateDashboardProps = {
  projects: [
    {
      project_id: 'project-1',
      name: 'MasterMind',
      status: 'active',
      updated_at: '2026-06-06T12:00:00Z',
    },
  ],
  selectedProjectId: 'project-1',
  selectedTaskId: 'task-1',
  overview: {
    project_id: 'project-1',
    name: 'MasterMind',
    status: 'active',
    total_tasks: 8,
    active_tasks: 2,
    blocked_tasks: 1,
    total_estimated_cost: 12.5,
    latest_checkpoint: {
      checkpoint_id: 'checkpoint-1',
      task_id: 'task-1',
      next_step_summary: 'Keep going',
      created_at: '2026-06-06T12:00:00Z',
    },
    latest_decision: {
      decision_id: 'decision-1',
      title: 'Ship the slice',
      status: 'approved',
      created_at: '2026-06-06T12:00:00Z',
    },
  },
  timeSummary: {
    project_id: 'project-1',
    total_tasks: 8,
    completed_tasks: 4,
    remaining_tasks: 4,
    active_run_count: 1,
    explicit_estimate_task_count: 5,
    fallback_estimate_task_count: 3,
    remaining_explicit_estimate_task_count: 2,
    remaining_fallback_estimate_task_count: 2,
    estimated_total_minutes: 240,
    estimated_remaining_minutes: 120,
    project_age_minutes: 360,
    active_run_elapsed_minutes: 45,
    confidence: 'medium',
    estimation_basis: 'heuristic',
    projected_completion_at: '2026-06-06T15:00:00Z',
  },
  tasks: [
    {
      task_id: 'task-1',
      title: 'Observability panel',
      status: 'in_progress',
    },
  ],
  dependencies: [],
  runs: [],
  decisions: [],
  activity: [],
  tokenUsage: [],
  gapRegistryEntries: [
    {
      id: 'gap-0001',
      title: 'Gap registry dedupe and prioritization',
      status: 'resolved',
      detected_from: 'mm-harness-gap-registry-and-promotion',
      objective_slug: 'mm-harness-gap-registry-and-promotion',
      evidence: ['Phase 1 did not yet rank or dedupe gaps.'],
      impact: 'high',
      urgency: 'medium',
      suggested_followup: 'mm-harness-gap-dedupe-and-priority',
      promotion_readiness: 'ready',
      promoted_objective_slug: 'mm-harness-gap-dedupe-and-priority',
      created_at_utc: '2026-06-08T12:00:00Z',
      updated_at_utc: '2026-06-08T12:10:00Z',
    },
  ],
  gapDuplicateSuspects: [
    {
      gap_ids: ['gap-0001', 'gap-0002'],
      reasons: ['same_suggested_followup'],
      shared_suggested_followup: 'mm-harness-gap-dedupe-and-priority',
      shared_normalized_title: null,
    },
  ],
  gapNextRecommendation: {
    id: 'gap-0001',
    title: 'Gap registry dedupe and prioritization',
    status: 'open',
    detected_from: 'mm-harness-gap-registry-and-promotion',
    objective_slug: 'mm-harness-gap-registry-and-promotion',
    evidence: ['Phase 1 did not yet rank or dedupe gaps.'],
    impact: 'high',
    urgency: 'medium',
    suggested_followup: 'mm-harness-gap-dedupe-and-priority',
    promotion_readiness: 'ready',
    promoted_objective_slug: null,
    created_at_utc: '2026-06-08T12:00:00Z',
    updated_at_utc: '2026-06-08T12:10:00Z',
  },
  kdSystemHealth: {
    record_count: 12,
    avg_quality_score: 0.81,
    rejection_rate: 0.08,
    p50_latency_ms: 140,
    p90_latency_ms: 260,
    t1_trend: [],
  },
  kdOutcomeMetrics: {
    delta_velocity: 180,
    knowledge_yield: 0.42,
    planning_accuracy: 0.79,
  },
  kdTemplates: [
    {
      id: 'template-1',
      brain_id: 'brain-01-product',
      template_name: 'Discovery brief synthesis',
      success_rate: 0.91,
      usage_count: 4,
      created_at: '2026-06-06T12:00:00Z',
      last_used_at: '2026-06-06T12:10:00Z',
    },
  ],
  contextProjection: null,
  doctrineProjection: null,
}

describe('ProjectStateDashboard', () => {
  it('renders the live brain feed panel in the project-state sidebar', () => {
    render(<ProjectStateDashboard {...baseProps} />)

    expect(screen.getByText('Live brain feed')).toBeInTheDocument()
    expect(screen.getByText(/Rust real-time hub/i)).toBeInTheDocument()
    expect(screen.getByTestId('brain-status-feed')).toBeInTheDocument()
  })

  it('renders knowledge distillation metrics and top templates', () => {
    render(<ProjectStateDashboard {...baseProps} />)

    expect(screen.getByText('Knowledge distillation')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText('42.0%')).toBeInTheDocument()
    expect(screen.getByText('Discovery brief synthesis')).toBeInTheDocument()
  })

  it('renders estimate coverage diagnostics for the current ETA', () => {
    render(<ProjectStateDashboard {...baseProps} />)

    expect(screen.getByText('Estimate coverage')).toBeInTheDocument()
    expect(screen.getByText('5/8 tasks have explicit estimates')).toBeInTheDocument()
    expect(screen.getByText(/Remaining explicit:\s*2\/4/i)).toBeInTheDocument()
    expect(screen.getByText(/Fallback remaining:\s*2/i)).toBeInTheDocument()
  })

  it('renders gap registry entries and lifecycle metadata', () => {
    render(<ProjectStateDashboard {...baseProps} />)

    expect(screen.getByText('Gap registry')).toBeInTheDocument()
    expect(screen.getByText('Next recommended gap')).toBeInTheDocument()
    expect(screen.getAllByText('Gap registry dedupe and prioritization').length).toBe(2)
    expect(screen.getByText('gap-0001')).toBeInTheDocument()
    expect(screen.getAllByText(/resolved|open/).length).toBeGreaterThan(0)
    expect(
      screen.getAllByText(/follow-up:\s*mm-harness-gap-dedupe-and-priority/i).length
    ).toBeGreaterThan(0)
    expect(screen.getByText('Duplicate suspects')).toBeInTheDocument()
    expect(screen.getByText('gap-0001 ↔ gap-0002')).toBeInTheDocument()
  })

  it('renders an explicit empty state when no gap registry entries exist', () => {
    render(
      <ProjectStateDashboard
        {...baseProps}
        gapRegistryEntries={[]}
        gapDuplicateSuspects={[]}
        gapNextRecommendation={null}
      />
    )

    expect(screen.getByText(/No gap registry entries recorded yet/i)).toBeInTheDocument()
    expect(screen.getByText(/No duplicate suspects detected right now/i)).toBeInTheDocument()
  })
})
