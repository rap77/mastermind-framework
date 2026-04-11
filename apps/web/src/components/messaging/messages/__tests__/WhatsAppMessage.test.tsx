import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import WhatsAppMessage from '../WhatsAppMessage'
import { MessageState } from '@/stores/messageStore'

describe('WhatsAppMessage', () => {
  const mockMessage: MessageState = {
    id: 'msg-1',
    channel: 'whatsapp',
    sender: 'John Doe',
    content: 'Hello from WhatsApp!',
    status: 'sent',
    timestamp: Date.now(),
    thread_id: 'thread-1',
  }

  it('should render green bubble', () => {
    render(<WhatsAppMessage message={mockMessage} />)

    const bubble = screen.getByTestId('whatsapp-message')
    expect(bubble).toHaveClass('whatsapp-bubble')
  })

  it('should show single checkmark for sent status', () => {
    render(<WhatsAppMessage message={mockMessage} />)

    expect(screen.getByText('✓')).toBeInTheDocument()
  })

  it('should show double checkmark for delivered status', () => {
    const message = { ...mockMessage, status: 'delivered' as const }
    render(<WhatsAppMessage message={message} />)

    expect(screen.getByText('✓✓')).toBeInTheDocument()
  })

  it('should show triple checkmark for read status', () => {
    const message = { ...mockMessage, status: 'read' as const }
    render(<WhatsAppMessage message={message} />)

    expect(screen.getByText('✓✓✓')).toBeInTheDocument()
  })

  it('should render text content', () => {
    render(<WhatsAppMessage message={mockMessage} />)

    expect(screen.getByText('Hello from WhatsApp!')).toBeInTheDocument()
  })

  it('should render media attachments', () => {
    const message = { ...mockMessage, media_url: 'https://example.com/image.jpg' }
    render(<WhatsAppMessage message={message} />)

    const image = screen.getByRole('img')
    expect(image).toHaveAttribute('src', 'https://example.com/image.jpg')
  })

  it('should show timestamp', () => {
    render(<WhatsAppMessage message={mockMessage} />)

    const timestamp = screen.getByTestId('message-timestamp')
    expect(timestamp).toBeInTheDocument()
  })
})
