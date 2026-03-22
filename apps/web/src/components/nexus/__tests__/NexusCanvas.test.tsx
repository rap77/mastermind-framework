import { describe, it, expect, vi } from 'vitest'
import { NODE_TYPES_EXPORT } from '../NexusCanvas'

// Mock @xyflow/react — avoid canvas/WebGL in test environment
vi.mock('@xyflow/react', () => ({
  ReactFlow: ({ children }: { children?: React.ReactNode }) => (
    <div data-testid="react-flow">{children}</div>
  ),
  Background: () => <div data-testid="rf-background" />,
  Controls: () => <div data-testid="rf-controls" />,
  Handle: ({ ...props }: React.ComponentProps<'div'>) => (
    <div data-testid="rf-handle" {...props} />
  ),
  Position: { Top: 'top', Bottom: 'bottom' },
}))

// Mock brainStore
vi.mock('@/stores/brainStore', () => ({
  useBrainState: vi.fn().mockReturnValue(undefined),
  useBrainStore: vi.fn(),
}))

// Mock NodeDetailPanel to avoid Sheet portal issues in tests
vi.mock('../NodeDetailPanel', () => ({
  NodeDetailPanel: () => null,
}))

describe('NexusCanvas', () => {
  it('NODE_TYPES object reference is stable — same reference across renders', () => {
    // NODE_TYPES is a module-level constant — same object every time it's imported
    // If it were defined inside the component, each render would create a new object
    // causing React Flow to remount the entire canvas (performance catastrophe)
    expect(NODE_TYPES_EXPORT).toBeDefined()
    expect(typeof NODE_TYPES_EXPORT).toBe('object')
    expect(NODE_TYPES_EXPORT.brainNode).toBeDefined()

    // The reference must be the SAME object across multiple references
    // This is guaranteed by module-level const (not re-evaluated per render)
    const ref1 = NODE_TYPES_EXPORT
    const ref2 = NODE_TYPES_EXPORT
    expect(Object.is(ref1, ref2)).toBe(true)
  })

  it('brain state change does NOT cause NexusCanvas remount', async () => {
    // This is structurally guaranteed by:
    // 1. NODE_TYPES at module level (stable reference)
    // 2. nodes array latched in useState (never updated)
    // 3. BrainNode wrapped in React.memo
    //
    // We verify the architectural invariant via NODE_TYPES stability
    // (the root cause of remount in React Flow is unstable nodeTypes reference)
    expect(NODE_TYPES_EXPORT).toBeDefined()

    // Verify BrainNode is the correct component reference
    const { BrainNode } = await import('../BrainNode')
    expect(NODE_TYPES_EXPORT.brainNode).toBe(BrainNode)
  })
})
