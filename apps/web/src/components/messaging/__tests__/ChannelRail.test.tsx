import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import ChannelRail from '../ChannelRail'

describe('ChannelRail', () => {
  it('should render channel icons', () => {
    const onChannelSelect = vi.fn()
    render(<ChannelRail selectedChannel="all" onChannelSelect={onChannelSelect} />)

    expect(screen.getByRole('button', { name: /whatsapp/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /instagram/i })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /email/i })).toBeInTheDocument()
  })

  it('should show unread badges per channel', () => {
    const onChannelSelect = vi.fn()
    render(
      <ChannelRail
        selectedChannel="all"
        onChannelSelect={onChannelSelect}
        unreadCounts={{ whatsapp: 5, instagram: 2, email: 0 }}
      />
    )

    expect(screen.getByText('5')).toBeInTheDocument()
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('should highlight selected channel', () => {
    const onChannelSelect = vi.fn()
    render(<ChannelRail selectedChannel="whatsapp" onChannelSelect={onChannelSelect} />)

    const whatsappButton = screen.getByRole('button', { name: /whatsapp/i })
    expect(whatsappButton).toHaveClass('active')
  })

  it('should call onChannelSelect when channel clicked', () => {
    const onChannelSelect = vi.fn()
    render(<ChannelRail selectedChannel="all" onChannelSelect={onChannelSelect} />)

    const instagramButton = screen.getByRole('button', { name: /instagram/i })
    fireEvent.click(instagramButton)

    expect(onChannelSelect).toHaveBeenCalledWith('instagram')
  })
})
