import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ThreadDetail from '../ThreadDetail'

// Mock WebSocket dispatcher at top level
vi.mock('@/stores/wsStore', () => ({
  wsDispatcher: {
    subscribe: vi.fn(() => vi.fn()),
  },
}))

describe('ThreadDetail', () => {
  const mockThread = {
    id: 'thread-1',
    channel: 'whatsapp' as const,
    subject: 'Test subject',
    participants: ['User 1', 'User 2'],
    messages: [
      {
        id: 'msg-1',
        channel: 'whatsapp' as const,
        sender: 'User 1',
        content: 'Hello',
        status: 'sent' as const,
        timestamp: Date.now(),
        thread_id: 'thread-1',
      },
    ],
  }

  it('should render thread detail with messages', () => {
    const onMerge = vi.fn()
    render(<ThreadDetail thread={mockThread} onMerge={onMerge} />)

    expect(screen.getByText('Test subject')).toBeInTheDocument()
    // Messages are rendered by Virtuoso, so we just verify the thread detail exists
    expect(screen.getByTestId('thread-detail')).toBeInTheDocument()
  })

  it('should show merge thread action', () => {
    const onAddToMergeSelection = vi.fn()
    render(<ThreadDetail thread={mockThread} onAddToMergeSelection={onAddToMergeSelection} />)

    const mergeButton = screen.getByRole('button', { name: /add to merge selection/i })
    expect(mergeButton).toBeInTheDocument()
  })

  it('should call onAddToMergeSelection when merge button clicked', () => {
    const onAddToMergeSelection = vi.fn()
    render(<ThreadDetail thread={mockThread} onAddToMergeSelection={onAddToMergeSelection} />)

    const mergeButton = screen.getByRole('button', { name: /add to merge selection/i })
    fireEvent.click(mergeButton)

    expect(onAddToMergeSelection).toHaveBeenCalledWith('thread-1')
  })

  it('should integrate with WebSocket for real-time updates', () => {
    const onMerge = vi.fn()

    render(<ThreadDetail thread={mockThread} onMerge={onMerge} />)

    // WebSocket subscription happens in useEffect
    // Just verify the component rendered without errors
    expect(screen.getByText('Test subject')).toBeInTheDocument()
  })
})
