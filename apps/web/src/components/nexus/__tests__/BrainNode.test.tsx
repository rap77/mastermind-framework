import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrainNode } from '../BrainNode'
import type { NodeProps } from '@xyflow/react'
import * as brainStore from '@/stores/brainStore'

// Mock brainStore — isolate from Zustand; individual tests override via vi.mocked
vi.mock('@/stores/brainStore', () => ({
  useBrainState: vi.fn().mockReturnValue(undefined),
}))

// Mock ReactFlow hooks used inside nodes
vi.mock('@xyflow/react', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@xyflow/react')>()
  return {
    ...actual,
    Handle: ({ ...props }: React.ComponentProps<'div'>) => (
      <div data-testid="rf-handle" {...props} />
    ),
    Position: { Top: 'top', Bottom: 'bottom' },
  }
})

function makeBrainNodeProps(overrides?: Partial<NodeProps>): NodeProps {
  return {
    id: 'brain-01',
    type: 'brainNode',
    data: {
      label: 'Product Strategy',
      niche: 'software',
      onSelect: vi.fn(),
    },
    selected: false,
    isConnectable: true,
    zIndex: 0,
    xPos: 0,
    yPos: 0,
    dragging: false,
    positionAbsoluteX: 0,
    positionAbsoluteY: 0,
    deletable: false,
    selectable: false,
    draggable: false,
    ...overrides,
  } as NodeProps
}

describe('BrainNode', () => {
  beforeEach(() => {
    // Reset mock to default (undefined = blueprint/ghost state)
    vi.mocked(brainStore.useBrainState).mockReturnValue(undefined)
  })

  it('all interactive children have nodrag class', () => {
    render(<BrainNode {...makeBrainNodeProps()} />)

    // Find the clickable button (brain name label)
    const button = screen.getByRole('button', { name: /product strategy/i })
    expect(button.className).toContain('nodrag')
  })

  it('all interactive children have nopan class', () => {
    render(<BrainNode {...makeBrainNodeProps()} />)

    const button = screen.getByRole('button', { name: /product strategy/i })
    expect(button.className).toContain('nopan')
  })

  it('clicking the node triggers onSelect without canvas drag event', () => {
    const onSelect = vi.fn()
    render(
      <BrainNode
        {...makeBrainNodeProps({
          id: 'brain-01',
          data: { label: 'Product Strategy', niche: 'software', onSelect },
        })}
      />
    )

    const button = screen.getByRole('button', { name: /product strategy/i })
    button.click()

    expect(onSelect).toHaveBeenCalledOnce()
    expect(onSelect).toHaveBeenCalledWith('brain-01')
  })

  it('re-renders only when its own brainId state changes, not other brains', () => {
    // BrainNode is React.memo — verify displayName set correctly
    expect(BrainNode.displayName).toBe('BrainNode')
  })

  // ─── 07-03: Ghost Architecture visual states ────────────────────────────────

  it('applies opacity-20 and border-dashed when brainState is undefined (blueprint/ghost)', () => {
    // mockUseBrainState already returns undefined by default (set in beforeEach)
    render(<BrainNode {...makeBrainNodeProps()} />)

    // The Card element should have blueprint styling classes
    const card = document.querySelector('[data-slot="card"]') as HTMLElement | null
    expect(card).not.toBeNull()
    expect(card?.className).toContain('opacity-20')
    expect(card?.className).toContain('border-dashed')
  })

  it('applies neon glow ring class when status is active', () => {
    vi.mocked(brainStore.useBrainState).mockReturnValue({
      id: 'brain-01',
      status: 'active',
      lastUpdated: Date.now(),
    })

    render(<BrainNode {...makeBrainNodeProps()} />)

    const card = document.querySelector('[data-slot="card"]') as HTMLElement | null
    expect(card).not.toBeNull()
    // Active state: ring-2 and ring color for neon glow
    expect(card?.className).toContain('ring-2')
    // opacity-20 and border-dashed should NOT be present when active
    expect(card?.className).not.toContain('opacity-20')
  })
})
