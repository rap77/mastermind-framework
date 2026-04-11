'use client'

import React from 'react'

interface ChannelRailProps {
  selectedChannel: string
  onChannelSelect: (channel: string) => void
  unreadCounts?: {
    whatsapp: number
    instagram: number
    email: number
  }
}

export default function ChannelRail({
  selectedChannel,
  onChannelSelect,
  unreadCounts = { whatsapp: 0, instagram: 0, email: 0 },
}: ChannelRailProps) {
  const channels = [
    { id: 'all', label: 'All', icon: '📬' },
    { id: 'whatsapp', label: 'WhatsApp', icon: '💬' },
    { id: 'instagram', label: 'Instagram', icon: '📷' },
    { id: 'email', label: 'Email', icon: '📧' },
  ]

  return (
    <div className="channel-rail" data-testid="channel-rail">
      {channels.map((channel) => (
        <button
          key={channel.id}
          className={`channel-button ${selectedChannel === channel.id ? 'active' : ''}`}
          onClick={() => onChannelSelect(channel.id)}
          aria-label={channel.label}
          title={channel.label}
        >
          <span className="channel-icon">{channel.icon}</span>
          {channel.id !== 'all' && unreadCounts[channel.id as keyof typeof unreadCounts] > 0 && (
            <span className="unread-badge">
              {unreadCounts[channel.id as keyof typeof unreadCounts]}
            </span>
          )}
        </button>
      ))}
      <style jsx>{`
        .channel-rail {
          width: 60px;
          height: 100%;
          display: flex;
          flex-direction: column;
          gap: 8px;
          padding: 16px 8px;
          background: #f5f5f5;
          border-right: 1px solid #e0e0e0;
        }

        .channel-button {
          position: relative;
          width: 44px;
          height: 44px;
          border: none;
          border-radius: 8px;
          background: white;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
        }

        .channel-button:hover {
          background: #e8e8e8;
        }

        .channel-button.active {
          background: #007bff;
          color: white;
        }

        .channel-icon {
          font-size: 20px;
        }

        .unread-badge {
          position: absolute;
          top: 4px;
          right: 4px;
          min-width: 16px;
          height: 16px;
          padding: 0 4px;
          background: #ff4444;
          color: white;
          font-size: 10px;
          font-weight: bold;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      `}</style>
    </div>
  )
}
