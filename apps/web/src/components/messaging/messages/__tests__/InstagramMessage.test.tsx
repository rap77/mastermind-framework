import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import InstagramMessage from '../InstagramMessage'
import { MessageState } from '@/stores/messageStore'

describe('InstagramMessage', () => {
  const mockMessage: MessageState = {
    id: 'msg-1',
    channel: 'instagram',
    sender: 'jane_doe',
    content: 'Amazing photo! 🔥',
    status: 'sent',
    timestamp: Date.now(),
    thread_id: 'thread-1',
  }

  it('should render gradient border', () => {
    render(<InstagramMessage message={mockMessage} />)

    const bubble = screen.getByTestId('instagram-message')
    expect(bubble).toHaveClass('instagram-gradient')
  })

  it('should show username', () => {
    render(<InstagramMessage message={mockMessage} />)

    expect(screen.getByText('@jane_doe')).toBeInTheDocument()
  })

  it('should render comment text', () => {
    render(<InstagramMessage message={mockMessage} />)

    expect(screen.getByText('Amazing photo! 🔥')).toBeInTheDocument()
  })

  it('should render media grid for images', () => {
    const message = { ...mockMessage, media_url: 'https://example.com/photo.jpg' }
    render(<InstagramMessage message={message} />)

    const image = screen.getByRole('img')
    expect(image).toHaveAttribute('src', 'https://example.com/photo.jpg')
  })

  it('should show timestamp', () => {
    render(<InstagramMessage message={mockMessage} />)

    const timestamp = screen.getByTestId('message-timestamp')
    expect(timestamp).toBeInTheDocument()
  })
})
