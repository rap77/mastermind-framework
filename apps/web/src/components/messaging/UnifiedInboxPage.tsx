import React, { useState, useEffect, useCallback } from 'react'
import ChannelRail from './ChannelRail'
import ThreadList, { Thread } from './ThreadList'
import ThreadDetail from './ThreadDetail'
import { wsDispatcher } from '@/stores/wsStore'
import { MessageState } from '@/stores/messageStore'

export default function UnifiedInboxPage() {
  const [selectedChannel, setSelectedChannel] = useState('all')
  const [selectedThreadId, setSelectedThreadId] = useState<string | null>(null)
  const [threads, setThreads] = useState<Thread[]>([])

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
    const unsubscribe = wsDispatcher.subscribe('thread_updates', (event: any) => {
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

  const handleMerge = useCallback((threadId: string) => {
    // TODO: Implement manual thread merge UI
    console.log('Merge thread:', threadId)
  }, [])

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
      <div className="inbox-layout">
        <ChannelRail selectedChannel={selectedChannel} onChannelSelect={setSelectedChannel} />
        <ThreadList
          threads={threads}
          selectedThreadId={selectedThreadId}
          onThreadSelect={handleThreadSelect}
          filterChannel={selectedChannel}
        />
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
      `}</style>
    </div>
  )
}
