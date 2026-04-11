import React from 'react'
import DOMPurify from 'dompurify'
import { MessageState } from '@/stores/messageStore'

interface EmailAttachment {
  filename: string
  url: string
}

interface EmailMessageProps {
  message: MessageState
  outgoing: boolean
  subject?: string
  inReplyTo?: string
  references?: string[]
  attachments?: EmailAttachment[]
}

export default function EmailMessage({
  message,
  outgoing,
  subject,
  inReplyTo,
  references,
  attachments = [],
}: EmailMessageProps) {
  return (
    <div
      className={`email-message ${outgoing ? 'email-outgoing' : 'email-incoming'}`}
      data-testid="email-message"
    >
      {subject && <div className="email-subject">{subject}</div>}
      <div className="email-header">
        <span className="email-sender">{message.sender}</span>
        <span className="email-time" data-testid="message-timestamp">
          {new Date(message.timestamp).toLocaleString()}
        </span>
      </div>
      {(inReplyTo || references) && (
        <div className="email-threading" data-testid="email-threading">
          {inReplyTo && <span className="threading-info">In reply to: {inReplyTo}</span>}
        </div>
      )}
      <div
        className="email-body"
        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(message.content) }}
      />
      {attachments.length > 0 && (
        <div className="email-attachments">
          {attachments.map((att, index) => (
            <a key={index} href={att.url} className="attachment-link">
              📎 {att.filename}
            </a>
          ))}
        </div>
      )}
      <style jsx>{`
        .email-message {
          max-width: 500px;
          padding: 12px 16px;
          border-radius: 8px;
          margin-bottom: 8px;
        }

        .email-outgoing {
          background: #e3f2fd;
          border-left: 4px solid #2196f3;
        }

        .email-incoming {
          background: #f5f5f5;
          border-left: 4px solid #9e9e9e;
        }

        .email-subject {
          font-weight: 600;
          font-size: 14px;
          margin-bottom: 8px;
          color: #262626;
        }

        .email-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          font-size: 12px;
        }

        .email-sender {
          font-weight: 500;
          color: #424242;
        }

        .email-time {
          color: #757575;
        }

        .email-threading {
          font-size: 11px;
          color: #9e9e9e;
          margin-bottom: 8px;
        }

        .email-body {
          font-size: 14px;
          line-height: 1.5;
          color: #424242;
          margin-bottom: 8px;
        }

        .email-attachments {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }

        .attachment-link {
          font-size: 13px;
          color: #2196f3;
          text-decoration: none;
        }

        .attachment-link:hover {
          text-decoration: underline;
        }
      `}</style>
    </div>
  )
}
