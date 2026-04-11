import React from 'react'
import { MessageState } from '@/stores/messageStore'

interface WhatsAppMessageProps {
  message: MessageState
}

export default function WhatsAppMessage({ message }: WhatsAppMessageProps) {
  const getCheckmarks = () => {
    switch (message.status) {
      case 'sent':
        return '✓'
      case 'delivered':
        return '✓✓'
      case 'read':
        return '✓✓✓'
      default:
        return ''
    }
  }

  return (
    <div className="whatsapp-message whatsapp-bubble" data-testid="whatsapp-message">
      <div className="message-sender">{message.sender}</div>
      <div className="message-content">{message.content}</div>
      {message.media_url && (
        <div className="message-media">
          <img src={message.media_url} alt="Attachment" />
        </div>
      )}
      <div className="message-footer">
        <span className="message-time" data-testid="message-timestamp">
          {new Date(message.timestamp).toLocaleTimeString()}
        </span>
        <span className="message-status">{getCheckmarks()}</span>
      </div>
      <style jsx>{`
        .whatsapp-message {
          max-width: 300px;
          padding: 8px 12px;
          border-radius: 8px;
          background: #dcf8c6;
          margin-bottom: 8px;
        }

        .message-sender {
          font-weight: 600;
          font-size: 13px;
          margin-bottom: 4px;
          color: #075e54;
        }

        .message-content {
          font-size: 14px;
          line-height: 1.4;
          margin-bottom: 4px;
        }

        .message-media img {
          max-width: 100%;
          border-radius: 4px;
          margin-bottom: 4px;
        }

        .message-footer {
          display: flex;
          justify-content: flex-end;
          align-items: center;
          gap: 4px;
        }

        .message-time {
          font-size: 11px;
          color: #667781;
        }

        .message-status {
          font-size: 12px;
          color: #53bdeb;
        }
      `}</style>
    </div>
  )
}
