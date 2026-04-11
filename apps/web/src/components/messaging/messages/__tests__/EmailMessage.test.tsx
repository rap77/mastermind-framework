import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import EmailMessage from '../EmailMessage'
import { MessageState } from '@/stores/messageStore'

describe('EmailMessage', () => {
  const mockMessage: MessageState = {
    id: 'msg-1',
    channel: 'email',
    sender: 'sender@example.com',
    content: '<p>Hello from <strong>email</strong>!</p>',
    status: 'sent',
    timestamp: Date.now(),
    thread_id: 'thread-1',
  }

  it('should render blue bubble for outgoing', () => {
    render(<EmailMessage message={mockMessage} outgoing={true} />)

    const bubble = screen.getByTestId('email-message')
    expect(bubble).toHaveClass('email-outgoing')
  })

  it('should render gray bubble for incoming', () => {
    render(<EmailMessage message={mockMessage} outgoing={false} />)

    const bubble = screen.getByTestId('email-message')
    expect(bubble).toHaveClass('email-incoming')
  })

  it('should show subject line', () => {
    render(<EmailMessage message={mockMessage} outgoing={true} subject="Test Subject" />)

    expect(screen.getByText('Test Subject')).toBeInTheDocument()
  })

  it('should render HTML body (sanitized)', () => {
    render(<EmailMessage message={mockMessage} outgoing={true} />)

    // DOMPurify sanitizes HTML, so <strong> should be rendered
    expect(screen.getByText('email')).toBeInTheDocument()
  })

  it('should show threading info', () => {
    render(
      <EmailMessage
        message={mockMessage}
        outgoing={true}
        inReplyTo="<previous@example.com>"
      />
    )

    const threading = screen.getByTestId('email-threading')
    expect(threading).toBeInTheDocument()
  })

  it('should show attachments', () => {
    render(
      <EmailMessage
        message={mockMessage}
        outgoing={true}
        attachments={[{ filename: 'document.pdf', url: 'https://example.com/doc.pdf' }]}
      />
    )

    // Attachment link includes the emoji and filename
    const attachmentLink = screen.getByText(/document\.pdf/)
    expect(attachmentLink).toBeInTheDocument()
    expect(attachmentLink.tagName).toBe('A')
  })

  it('should show timestamp', () => {
    render(<EmailMessage message={mockMessage} outgoing={true} />)

    const timestamp = screen.getByTestId('message-timestamp')
    expect(timestamp).toBeInTheDocument()
  })
})
