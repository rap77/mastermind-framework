import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { persist } from 'zustand/middleware'
import { enableMapSet } from 'immer'

enableMapSet()

export type ChannelType = 'whatsapp' | 'instagram' | 'email'
export type MessageStatus = 'sent' | 'delivered' | 'read' | 'failed'

export interface MessageState {
  id: string
  channel: ChannelType
  sender: string
  content: string
  media_url?: string
  status: MessageStatus
  timestamp: number
  thread_id: string
}

export interface MessageDraft {
  channel_id: string
  content: string
  media_attachments: string[]
}

interface MessageStore {
  messages: Map<string, MessageState>
  drafts: Map<string, MessageDraft>
  inMemoryDrafts: Map<string, MessageDraft> // Fallback storage
  localStorageError: boolean // Track quota exceeded
  localStorage_quota_percent: number

  // O(1) targeted selector
  useMessage: (id: string) => MessageState | undefined

  // Actions
  addMessage: (message: MessageState) => void
  updateMessageStatus: (id: string, status: MessageStatus) => void
  saveDraft: (channelId: string, draft: MessageDraft) => void

  // Quota monitoring
  checkLocalStorageQuota: () => number
  calculateQuotaPercent: () => number
  clearOldDrafts: () => void
}

const LOCAL_STORAGE_QUOTA_LIMIT = 5 * 1024 * 1024 // 5MB default

// RAF batching for message updates
let rafId: number | null = null
const eventQueue: Array<{ type: string; message: MessageState }> = []

function processEventQueue() {
  eventQueue.splice(0, eventQueue.length)
  rafId = null
}

export const useMessageStore = create<MessageStore>()(
  persist(
    immer((set, get) => ({
      messages: new Map(),
      drafts: new Map(),
      inMemoryDrafts: new Map(),
      localStorageError: false,
      localStorage_quota_percent: 0,

      useMessage: (id: string) => {
        return get().messages.get(id)
      },

      addMessage: (message: MessageState) => {
        set((state) => {
          state.messages.set(message.id, message)
        })

        // RAF batching
        eventQueue.push({ type: 'MESSAGE_ADDED', message })
        if (rafId === null) {
          rafId = requestAnimationFrame(processEventQueue)
        }
      },

      updateMessageStatus: (id: string, status: MessageStatus) => {
        set((state) => {
          const message = state.messages.get(id)
          if (message) {
            message.status = status
          }
        })
      },

      saveDraft: (channelId: string, draft: MessageDraft) => {
        set((state) => {
          try {
            state.drafts.set(channelId, draft)
            state.localStorageError = false // Clear error on success
          } catch (e: any) {
            // Handle QuotaExceededError
            if (e.name === 'QuotaExceededError' || e.code === 22) {
              console.warn('[messageStore] LocalStorage quota exceeded, saving to in-memory fallback')
              state.inMemoryDrafts.set(channelId, draft) // Fallback
              state.localStorageError = true

              // Track metric
              if (typeof window !== 'undefined' && (window as any).gtag) {
                ;(window as any).gtag('event', 'draft_save_error', {
                  error_type: 'quota_exceeded',
                  fallback_used: 'in_memory',
                })
              }
            }
          }
        })
      },

      checkLocalStorageQuota: () => {
        return get().calculateQuotaPercent()
      },

      calculateQuotaPercent: () => {
        let totalSize = 0

        for (let key in localStorage) {
          if (localStorage.hasOwnProperty(key)) {
            totalSize += localStorage[key].length + key.length
          }
        }

        return (totalSize / LOCAL_STORAGE_QUOTA_LIMIT) * 100
      },

      clearOldDrafts: () => {
        set((state) => {
          const draftArray = Array.from(state.drafts.entries())
          // Keep only the 10 most recent drafts
          const recentDrafts = draftArray.slice(-10)
          state.drafts = new Map(recentDrafts)
          state.localStorageError = false
        })
      },
    })),
    {
      name: 'mastermind-messages',
      partialize: (state) => ({
        drafts: Array.from(state.drafts.entries()), // Persist only drafts
        localStorage_quota_percent: state.localStorage_quota_percent,
      }),
      onRehydrateStorage: () => (state) => {
        // Handle quota exceeded on rehydration
        if (!state) return

        try {
          const stored = localStorage.getItem('mastermind-messages')
          if (stored) {
            const parsed = JSON.parse(stored)
            if (parsed.drafts) {
              state.drafts = new Map(parsed.drafts)
            }
          }
        } catch (e: any) {
          if (e.name === 'QuotaExceededError' || e.code === 22) {
            console.warn('[messageStore] LocalStorage quota exceeded on rehydration, using in-memory fallback')
            state.localStorageError = true
            state.inMemoryDrafts = new Map() // Initialize fallback
          }
        }
      },
      merge: (persistedState: any, currentState: MessageStore) => {
        return {
          ...currentState,
          drafts: new Map(persistedState.drafts || []),
          localStorage_quota_percent: persistedState.localStorage_quota_percent || 0,
        }
      },
    }
  )
)
