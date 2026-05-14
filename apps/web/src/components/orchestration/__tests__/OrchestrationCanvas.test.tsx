/**
 * OrchestrationCanvas.test.tsx — D1.08
 *
 * Tests that OrchestrationCanvas renders correctly with mocked brain data.
 * React Flow is mocked to avoid WebGL/canvas issues in jsdom.
 * brainStore is mocked to control node status.
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import type { Brain } from '@/lib/api'

// ─── Mocks — must be top-level ─────────────────────────────────────────────────

// React Flow: avoid WebGL/canvas in jsdom
vi.mock('@xyflow/react', () => ({
  ReactFlow: ({
    nodes,
    children,
  }: {
    nodes?: { id: string }[]
    children?: React.ReactNode
  }) => (
    <div data-testid="react-flow" data-node-count={nodes?.length ?? 0}>
      {children}
    </div>
  ),
  Background: () => <div data-testid="rf-background" />,
  Controls: () => <div data-testid="rf-controls" />,
  Handle: () => <div data-testid="rf-handle" />,
  Position: { Left: 'left', Right: 'right', Top: 'top', Bottom: 'bottom' },
}))

// dagre: return predictable positions
vi.mock('@dagrejs/dagre', () => ({
  default: {
    graphlib: {
      Graph: class {
        setDefaultEdgeLabel() {}
        setGraph() {}
        nodes() { return [] }
        edges() { return [] }
        removeNode() {}
        removeEdge() {}
        setNode() {}
        setEdge() {}
        node() { return { x: 100, y: 100, width: 220, height: 70 } }
      },
    },
    layout: vi.fn(),
  },
}))

// brainStore: all brains in idle state
vi.mock('@/stores/brainStore', () => ({
  useBrainState: vi.fn().mockReturnValue({ id: 'any', status: 'idle', lastUpdated: 0 }),
  useBrainStore: vi.fn().mockReturnValue({ sessionInvocationCounts: new Map() }),
}))

// HybridFlowEdge stub
vi.mock('@/components/nexus/HybridFlowEdge', () => ({
  HybridFlowEdge: () => <div data-testid="hybrid-flow-edge" />,
}))

// Import component AFTER mocks
import { OrchestrationCanvas } from '../OrchestrationCanvas'

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const MOCK_7_BRAINS: Brain[] = [
  { id: 'brain-01', name: 'Product Strategy', niche: 'software-development', status: 'idle', uptime: 0, last_called_at: null },
  { id: 'brain-02', name: 'UX Research', niche: 'software-development', status: 'idle', uptime: 0, last_called_at: null },
  { id: 'brain-03', name: 'UI Design', niche: 'software-development', status: 'idle', uptime: 0, last_called_at: null },
  { id: 'brain-04', name: 'Frontend', niche: 'software-development', status: 'idle', uptime: 0, last_called_at: null },
  { id: 'brain-05', name: 'Backend', niche: 'software-development', status: 'idle', uptime: 0, last_called_at: null },
  { id: 'brain-06', name: 'QA/DevOps', niche: 'software-development', status: 'idle', uptime: 0, last_called_at: null },
  { id: 'brain-07', name: 'Growth/Data', niche: 'universal', status: 'idle', uptime: 0, last_called_at: null },
]

// ─── Tests ─────────────────────────────────────────────────────────────────────

describe('OrchestrationCanvas (D1.08)', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the ReactFlow canvas wrapper', () => {
    render(
      <OrchestrationCanvas
        blueprintBrains={MOCK_7_BRAINS}
        selectedBrainId={null}
        onSelect={vi.fn()}
      />,
    )

    expect(screen.getByTestId('orchestration-canvas')).toBeInTheDocument()
    expect(screen.getByTestId('react-flow')).toBeInTheDocument()
  })

  it('passes all 7 brain nodes to ReactFlow', () => {
    render(
      <OrchestrationCanvas
        blueprintBrains={MOCK_7_BRAINS}
        selectedBrainId={null}
        onSelect={vi.fn()}
      />,
    )

    const rf = screen.getByTestId('react-flow')
    // All 7 brains become nodes
    expect(rf).toHaveAttribute('data-node-count', '7')
  })

  it('renders Background and Controls inside ReactFlow', () => {
    render(
      <OrchestrationCanvas
        blueprintBrains={MOCK_7_BRAINS}
        selectedBrainId={null}
        onSelect={vi.fn()}
      />,
    )

    expect(screen.getByTestId('rf-background')).toBeInTheDocument()
    expect(screen.getByTestId('rf-controls')).toBeInTheDocument()
  })

  it('handles empty brains array without crashing', () => {
    expect(() => {
      render(
        <OrchestrationCanvas
          blueprintBrains={[]}
          selectedBrainId={null}
          onSelect={vi.fn()}
        />,
      )
    }).not.toThrow()

    expect(screen.getByTestId('orchestration-canvas')).toBeInTheDocument()
  })

  it('accepts selectedBrainId prop without crashing', () => {
    render(
      <OrchestrationCanvas
        blueprintBrains={MOCK_7_BRAINS}
        selectedBrainId="brain-01"
        onSelect={vi.fn()}
      />,
    )

    expect(screen.getByTestId('orchestration-canvas')).toBeInTheDocument()
  })
})
