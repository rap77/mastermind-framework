import React, { useEffect, useState } from 'react'
import { Virtuoso } from 'react-virtuoso'
import { wsDispatcher } from '@/stores/wsStore'
import { MessageState } from '@/stores/messageStore'
import WhatsAppMessage from './messages/WhatsAppMessage'
import InstagramMessage from './messages/InstagramMessage'
import EmailMessage from './messages/EmailMessage'

interface ThreadDetailProps {
  thread: {
    id: string
    channel: 'whatsapp' | 'instagram' | 'email'
    subject: string
    participants: string[]
    messages: MessageState[]
  }
  onMerge: (threadId: string) => void
}

interface ThreadUpdateEvent {
  thread_id: string
  message: MessageState
}

export default function ThreadDetail({ thread, onMerge }: ThreadDetailProps) {
  const [messages, setMessages] = useState<MessageState[]>(thread.messages)
  const [messageText, setMessageText] = useState('')

  useEffect(() => {
    // Subscribe to WebSocket updates
    const unsubscribe = wsDispatcher.subscribe('thread_updates', (event: ThreadUpdateEvent) => {
      if (event.thread_id === thread.id) {
        setMessages((prev) => [...prev, event.message])
      }
    })

    return () => unsubscribe()
  }, [thread.id])

  return (
    <div className="thread-detail" data-testid="thread-detail" data-selected-thread={thread.id}>
      <div className="thread-header">
        <h2 className="thread-subject">{thread.subject}</h2>
        <button className="merge-button" onClick={() => onMerge(thread.id)}>
          Merge Thread
        </button>
      </div>

      <div className="thread-participants">
        {thread.participants.map((p) => (
          <span key={p} className="participant">
            {p}
          </span>
        ))}
      </div>

      <div className="messages-container">
        <Virtuoso
          style={{ height: 'calc(100% - 120px)' }}
          data={messages}
          itemContent={(index, message) => {
            // Render channel-specific message component
            switch (message.channel) {
              case 'whatsapp':
                return <WhatsAppMessage key={message.id} message={message} />
              case 'instagram':
                return <InstagramMessage key={message.id} message={message} />
              case 'email':
                return <EmailMessage key={message.id} message={message} outgoing={message.sender === 'me'} />
              default:
                return (
                  <div key={message.id} className={`message message-${message.status}`}>
                    <div className="message-sender">{message.sender}</div>
                    <div className="message-content">{message.content}</div>
                    <div className="message-time">{new Date(message.timestamp).toLocaleString()}</div>
                  </div>
                )
            }
          }}
        />
      </div>

      <div className="message-composer">
        <textarea
          value={messageText}
          onChange={(e) => setMessageText(e.target.value)}
          placeholder="Type a message..."
        />
        <button onClick={() => console.log('Send message:', messageText)}>Send</button>
      </div>

      <style jsx>{`
        .thread-detail {
          flex: 1;
          display: flex;
          flex-direction: column;
          height: 100%;
          background: white;
        }

        .thread-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px;
          border-bottom: 1px solid #e0e0e0;
        }

        .thread-subject {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
        }

        .merge-button {
          padding: 8px 16px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
        }

        .merge-button:hover {
          background: #0056b3;
        }

        .thread-participants {
          display: flex;
          gap: 8px;
          padding: 8px 16px;
          border-bottom: 1px solid #f0f0f0;
        }

        .participant {
          padding: 4px 8px;
          background: #f0f0f0;
          border-radius: 12px;
          font-size: 12px;
        }

        .messages-container {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
        }

        .message {
          margin-bottom: 12px;
          padding: 12px;
          border-radius: 8px;
          background: #f8f8f8;
        }

        .message-sent {
          background: #dcf8c6;
        }

        .message-sender {
          font-weight: 500;
          margin-bottom: 4px;
          font-size: 14px;
        }

        .message-content {
          font-size: 14px;
          margin-bottom: 4px;
        }

        .message-time {
          font-size: 11px;
          color: #666;
        }

        .message-composer {
          display: flex;
          gap: 8px;
          padding: 16px;
          border-top: 1px solid #e0e0e0;
        }

        .message-composer textarea {
          flex: 1;
          padding: 8px;
          border: 1px solid #e0e0e0;
          border-radius: 6px;
          resize: none;
          min-height: 40px;
        }

        .message-composer button {
          padding: 8px 16px;
          background: #007bff;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-weight: 500;
        }

        .message-composer button:hover {
          background: #0056b3;
        }
      `}</style>
    </div>
  )
}
