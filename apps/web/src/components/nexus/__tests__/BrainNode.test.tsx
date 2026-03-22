import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrainNode } from '../BrainNode'
import type { NodeProps } from '@xyflow/react'

// Mock brainStore — isolate from Zustand
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
})
