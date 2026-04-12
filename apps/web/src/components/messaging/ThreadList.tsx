'use client'

import React, { useMemo, memo } from 'react'
import { Virtuoso } from 'react-virtuoso'

export interface Thread {
  id: string
  channel: 'whatsapp' | 'instagram' | 'email'
  subject: string
  preview: string
  timestamp: number
  unread: boolean
  status: string
}

interface ThreadListProps {
  threads: Thread[]
  selectedThreadId: string | null
  onThreadSelect: (threadId: string) => void
  filterChannel?: string
  selectedThreads?: Set<string>
  onToggleThreadSelection?: (threadId: string) => void
  onMergeThreads?: (threadIds: string[]) => void
}

interface ThreadItemProps {
  thread: Thread
  isSelected: boolean
  isMergeSelected: boolean
  onThreadSelect: (threadId: string) => void
  onToggleThreadSelection?: (threadId: string) => void
}

const ThreadItem = memo(function ThreadItem({
  thread,
  isSelected,
  isMergeSelected,
  onThreadSelect,
  onToggleThreadSelection,
}: ThreadItemProps) {
  // Compute background style based on state
  const getBackgroundStyle = (): React.CSSProperties => {
    if (isMergeSelected) {
      return { backgroundColor: '#fff3e0', borderLeft: '3px solid #ff9800' }
    }
    if (isSelected) {
      return { backgroundColor: '#e3f2fd', borderLeft: '3px solid #2196f3' }
    }
    return {}
  }

  return (
    <div
      data-testid={`thread-item-${thread.id}`}
      className={`thread-item ${thread.unread ? 'unread' : ''}`}
      style={getBackgroundStyle()}
      onClick={() => onThreadSelect(thread.id)}
    >
      {onToggleThreadSelection && (
        <input
          type="checkbox"
          checked={isMergeSelected}
          onChange={() => onToggleThreadSelection(thread.id)}
          className="thread-checkbox"
          onClick={(e) => e.stopPropagation()}
        />
      )}
      <div className="thread-header">
        <span className="thread-channel">{thread.channel}</span>
        <span className="thread-time">{new Date(thread.timestamp).toLocaleTimeString()}</span>
      </div>
      <div className="thread-subject">{thread.subject}</div>
      <div className="thread-preview">{thread.preview}</div>
    </div>
  )
})

export default function ThreadList({
  threads,
  selectedThreadId,
  onThreadSelect,
  filterChannel = 'all',
  selectedThreads = new Set(),
  onToggleThreadSelection,
  onMergeThreads,
}: ThreadListProps) {
  // Filter and sort threads
  const filteredThreads = useMemo(() => {
    let filtered = filterChannel === 'all' ? threads : threads.filter((t) => t.channel === filterChannel)
    return filtered.sort((a, b) => b.timestamp - a.timestamp)
  }, [threads, filterChannel])

  const handleMergeClick = () => {
    if (onMergeThreads && selectedThreads.size >= 2) {
      onMergeThreads(Array.from(selectedThreads))
    }
  }

  return (
    <div className="thread-list" data-testid="thread-list" data-channel={filterChannel}>
      {onMergeThreads && selectedThreads.size >= 2 && (
        <div className="thread-merge-bar">
          <span className="selected-count">{selectedThreads.size} threads selected</span>
          <button onClick={handleMergeClick} className="merge-button">
            Merge
          </button>
        </div>
      )}
      <Virtuoso
        style={{ height: onMergeThreads && selectedThreads.size >= 2 ? 'calc(100% - 50px)' : '100%' }}
        data={filteredThreads}
        initialItemCount={100}
        overscan={200}
        itemContent={(index, thread) => (
          <ThreadItem
            key={thread.id}
            thread={thread}
            isSelected={selectedThreadId === thread.id}
            isMergeSelected={selectedThreads.has(thread.id)}
            onThreadSelect={onThreadSelect}
            onToggleThreadSelection={onToggleThreadSelection}
          />
        )}
      />
      <style jsx>{`
        .thread-list {
          width: 300px;
          height: 100%;
          border-right: 1px solid #e0e0e0;
          background: white;
        }

        .thread-merge-bar {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 12px 16px;
          background: #e3f2fd;
          border-bottom: 1px solid #2196f3;
        }

        .selected-count {
          font-size: 13px;
          font-weight: 500;
          color: #1976d2;
        }

        .merge-button {
          padding: 6px 12px;
          background: #2196f3;
          color: white;
          border: none;
          border-radius: 4px;
          font-size: 13px;
          cursor: pointer;
        }

        .merge-button:hover {
          background: #1976d2;
        }

        .thread-item {
          padding: 12px 16px;
          border-bottom: 1px solid #f0f0f0;
          cursor: pointer;
          transition: background 0.2s;
          display: flex;
          gap: 8px;
        }

        .thread-checkbox {
          margin-top: 2px;
        }

        .thread-item:hover {
          background: #f8f8f8;
        }

        .thread-item.selected {
          background: #e3f2fd;
        }

        .thread-item.merge-selected {
          background: #fff3e0;
        }

        .thread-item.unread {
          font-weight: 500;
        }

        .thread-header {
          display: flex;
          justify-content: space-between;
          font-size: 12px;
          color: #666;
          margin-bottom: 4px;
        }

        .thread-channel {
          text-transform: capitalize;
        }

        .thread-subject {
          font-weight: 500;
          margin-bottom: 4px;
        }

        .thread-preview {
          font-size: 14px;
          color: #666;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
      `}</style>
    </div>
  )
}
