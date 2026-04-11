import React from 'react'
import { MessageState } from '@/stores/messageStore'

interface InstagramMessageProps {
  message: MessageState
}

export default function InstagramMessage({ message }: InstagramMessageProps) {
  return (
    <div
      className="instagram-message instagram-gradient"
      data-testid="instagram-message"
    >
      <div className="message-header">
        <span className="message-username">@{message.sender}</span>
      </div>
      <div className="message-content">{message.content}</div>
      {message.media_url && (
        <div className="message-media">
          <img src={message.media_url} alt="Instagram media" />
        </div>
      )}
      <div className="message-footer">
        <span className="message-time" data-testid="message-timestamp">
          {new Date(message.timestamp).toLocaleString()}
        </span>
      </div>
      <style jsx>{`
        .instagram-message {
          max-width: 350px;
          padding: 12px;
          border-radius: 12px;
          border: 2px solid transparent;
          background: white;
          margin-bottom: 8px;
        }

        .instagram-gradient {
          background: linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045);
          background-clip: padding-box;
          position: relative;
        }

        .instagram-gradient::before {
          content: '';
          position: absolute;
          inset: 0;
          border-radius: 12px;
          padding: 2px;
          background: linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045);
          -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
          -webkit-mask-composite: xor;
          mask-composite: exclude;
        }

        .message-header {
          margin-bottom: 8px;
        }

        .message-username {
          font-weight: 600;
          font-size: 13px;
          color: #262626;
        }

        .message-content {
          font-size: 14px;
          line-height: 1.4;
          margin-bottom: 8px;
          color: #262626;
        }

        .message-media img {
          width: 100%;
          border-radius: 8px;
          margin-bottom: 8px;
        }

        .message-footer {
          display: flex;
          justify-content: flex-end;
        }

        .message-time {
          font-size: 11px;
          color: #8e8e8e;
        }
      `}</style>
    </div>
  )
}
