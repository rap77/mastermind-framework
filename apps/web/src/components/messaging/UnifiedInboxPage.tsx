import React, { useState, useEffect, useCallback } from 'react'
import ChannelRail from './ChannelRail'
import ThreadList, { Thread } from './ThreadList'
import ThreadDetail from './ThreadDetail'
import { wsDispatcher } from '@/stores/wsStore'
import { useMessageStore } from '@/stores/messageStore'
import { MessageState } from '@/stores/messageStore'
import { logger } from '@/lib/logger'

type MessagesResponse = Thread[]

interface ThreadUpdateEvent {
  thread_id: string
  thread: Thread
}

export default function UnifiedInboxPage() {
  const [selectedChannel, setSelectedChannel] = useState('all')
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null)
  const [threads, setThreads] = useState<Thread[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch threads from API
  useEffect(() => {
    const fetchThreads = async () => {
      try {
        setIsLoading(true)
        setError(null)
        const response = await fetch(`/api/messages?channel=${selectedChannel}&limit=1000`)
        if (!response.ok) {
          throw new Error(`Failed to fetch threads: ${response.statusText}`)
        }
        const data: MessagesResponse = await response.json()
        setThreads(data)
      } catch (err) {
        console.error('Error fetching threads:', err)
        setError(err instanceof Error ? err.message : 'Failed to load threads')
        // Fallback to mock data if API fails
        const mockThreads: Thread[] = Array.from({ length: 1000 }, (_, i) => ({
          id: `thread-${i}`,
          channel: ['whatsapp', 'instagram', 'email'][i % 3] as Thread['channel'],
          subject: `Test Thread ${i + 1}`,
          preview: `This is a preview message for thread ${i + 1}...`,
          timestamp: Date.now() - i * 60000,
          unread: i % 5 === 0,
          status: 'active',
        }))
        setThreads(mockThreads)
      } finally {
        setIsLoading(false)
      }
    }

    fetchThreads()
  }, [selectedChannel])

  // Thread merge state
  const selectedThreads = useMessageStore((state) => state.selectedThreads)
  const toggleThreadSelection = useMessageStore((state) => state.toggleThreadSelection)
  const clearThreadSelection = useMessageStore((state) => state.clearThreadSelection)
  const mergeThreads = useMessageStore((state) => state.mergeThreads)

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'j' || e.key === 'J') {
        // Navigate to next thread
        const currentIndex = threads.findIndex((t) => t.id === selectedThreadId)
        if (currentIndex < threads.length - 1) {
          setSelectedThreadId(threads[currentIndex + 1].id)
        }
      } else if (e.key === 'k' || e.key === 'K') {
        // Navigate to previous thread
        const currentIndex = threads.findIndex((t) => t.id === selectedThreadId)
        if (currentIndex > 0) {
          setSelectedThreadId(threads[currentIndex - 1].id)
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [threads, selectedThreadId])

  // WebSocket integration
  useEffect(() => {
    const unsubscribe = wsDispatcher.subscribe('thread_updates', (event: ThreadUpdateEvent) => {
      // Update threads in real-time
      setThreads((prev) => {
        const existing = prev.find((t) => t.id === event.thread_id)
        if (existing) {
          return prev.map((t) => (t.id === event.thread_id ? { ...t, ...event.thread } : t))
        } else {
          return [...prev, event.thread]
        }
      })
    })

    return () => unsubscribe()
  }, [])

  const handleThreadSelect = useCallback((threadId: string) => {
    setSelectedThreadId(threadId)
  }, [])

  const handleMerge = useCallback(async (threadIds: string[]) => {
    try {
      await mergeThreads(threadIds)
      // TODO: Refresh thread list after merge
      logger.info('Threads merged successfully:', threadIds)
    } catch (error) {
      logger.error('Failed to merge threads:', error)
    }
  }, [mergeThreads])

  // Mock thread data for selected thread
  const selectedThread = selectedThreadId
    ? {
        id: selectedThreadId,
        channel: threads.find((t) => t.id === selectedThreadId)?.channel || 'whatsapp',
        subject: threads.find((t) => t.id === selectedThreadId)?.subject || '',
        participants: ['User 1', 'User 2'],
        messages: [] as MessageState[],
      }
    : null

  return (
    <div className="unified-inbox-page" data-testid="unified-inbox-page">
      {error && (
        <div className="error-banner" data-testid="error-banner">
          <span>{error}</span>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      )}
      <div className="inbox-layout">
        <ChannelRail selectedChannel={selectedChannel} onChannelSelect={setSelectedChannel} />
        {isLoading ? (
          <div className="loading-state" data-testid="loading-state">
            <div className="spinner" />
            <p>Loading threads...</p>
          </div>
        ) : (
          <ThreadList
            threads={threads}
            selectedThreadId={selectedThreadId}
            onThreadSelect={handleThreadSelect}
            filterChannel={selectedChannel}
            selectedThreads={selectedThreads}
            onToggleThreadSelection={toggleThreadSelection}
            onMergeThreads={handleMerge}
          />
        )}
        {selectedThread ? (
          <ThreadDetail thread={selectedThread} onMerge={handleMerge} />
        ) : (
          <div className="empty-state" data-testid="thread-detail">
            <p>Select a thread to view messages</p>
          </div>
        )}
      </div>

      <style jsx>{`
        .unified-inbox-page {
          width: 100%;
          height: 100vh;
          display: flex;
          flex-direction: column;
        }

        .inbox-layout {
          display: grid;
          grid-template-columns: 60px 300px 1fr;
          height: 100%;
        }

        .empty-state {
          flex: 1;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #666;
          font-size: 14px;
        }

        .error-banner {
          padding: 12px 16px;
          background: #ffebee;
          border-bottom: 1px solid #ef5350;
          display: flex;
          justify-content: space-between;
          align-items: center;
          color: #c62828;
        }

        .error-banner button {
          padding: 6px 12px;
          background: #ef5350;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .loading-state {
          width: 300px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 40px;
          color: #666;
        }

        .spinner {
          width: 32px;
          height: 32px;
          border: 3px solid #f0f0f0;
          border-top-color: #2196f3;
          border-radius: 50%;
          animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </div>
  )
}
