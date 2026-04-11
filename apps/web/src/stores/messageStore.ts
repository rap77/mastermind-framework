import { create } from 'zustand'
import { immer } from 'zustand/middleware/immer'
import { persist } from 'zustand/middleware'
import { enableMapSet } from 'immer'
import { logger } from '@/lib/logger'
import type {
  ChannelMessage,
  MessageState,
  MessageDraft,
  WhatsAppMessage,
  InstagramMessage,
  EmailMessage,
  MessageStatus,
} from '@/types/messages'

enableMapSet()

// Re-export types for backward compatibility
export type { ChannelMessage, MessageState, MessageDraft, MessageStatus }
export type { WhatsAppMessage, InstagramMessage, EmailMessage }

// Google Analytics type declaration
declare global {
  interface Window {
    gtag?: (event: string, action: string, params: Record<string, unknown>) => void
  }
}

interface MessageStore {
  messages: Map<string, ChannelMessage> // Typed with ChannelMessage
  drafts: Map<string, MessageDraft>
  inMemoryDrafts: Map<string, MessageDraft> // Fallback storage
  localStorageError: boolean // Track quota exceeded
  localStorage_quota_percent: number

  // Thread merge state
  selectedThreads: Set<string>

  // O(1) targeted selector
  useMessage: (id: string) => ChannelMessage | undefined

  // Channel-specific getters
  getWhatsAppMessage: (id: string) => WhatsAppMessage | undefined
  getInstagramMessage: (id: string) => InstagramMessage | undefined
  getEmailMessage: (id: string) => EmailMessage | undefined

  // Actions
  addMessage: (message: ChannelMessage) => void
  updateMessageStatus: (id: string, status: MessageStatus) => void
  saveDraft: (channelId: string, draft: MessageDraft) => void

  // Thread merge actions
  toggleThreadSelection: (threadId: string) => void
  clearThreadSelection: () => void
  mergeThreads: (threadIds: string[]) => Promise<void>

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
      selectedThreads: new Set(),

      useMessage: (id: string) => {
        return get().messages.get(id)
      },

      getWhatsAppMessage: (id: string) => {
        const msg = get().messages.get(id)
        if (msg && msg.channel === 'whatsapp') {
          return msg as WhatsAppMessage
        }
        return undefined
      },

      getInstagramMessage: (id: string) => {
        const msg = get().messages.get(id)
        if (msg && msg.channel === 'instagram') {
          return msg as InstagramMessage
        }
        return undefined
      },

      getEmailMessage: (id: string) => {
        const msg = get().messages.get(id)
        if (msg && msg.channel === 'email') {
          return msg as EmailMessage
        }
        return undefined
      },

      addMessage: (message: ChannelMessage) => {
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
          } catch (e: unknown) {
            // Handle QuotaExceededError
            const errorCode = e instanceof Error && 'code' in e ? (e as { code: number }).code : undefined
            if (e instanceof Error && (e.name === 'QuotaExceededError' || errorCode === 22)) {
              logger.warn('[messageStore] LocalStorage quota exceeded, saving to in-memory fallback')
              state.inMemoryDrafts.set(channelId, draft) // Fallback
              state.localStorageError = true

              // Track metric
              if (typeof window !== 'undefined' && window.gtag) {
                window.gtag('event', 'draft_save_error', {
                  error_type: 'quota_exceeded',
                  fallback_used: 'in_memory',
                })
              }
            }
          }
        })
      },

      toggleThreadSelection: (threadId: string) => {
        set((state) => {
          if (state.selectedThreads.has(threadId)) {
            state.selectedThreads.delete(threadId)
          } else {
            state.selectedThreads.add(threadId)
          }
        })
      },

      clearThreadSelection: () => {
        set((state) => {
          state.selectedThreads.clear()
        })
      },

      mergeThreads: async (threadIds: string[]) => {
        if (threadIds.length < 2) {
          throw new Error('At least 2 threads required for merge')
        }

        // TODO: Implement merge API call
        // POST /api/threads/merge with threadIds
        logger.info('Merging threads:', threadIds)

        // Clear selection after merge
        set((state) => {
          state.selectedThreads.clear()
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
        } catch (e: unknown) {
          const errorCode = e instanceof Error && 'code' in e ? (e as { code: number }).code : undefined
          if (e instanceof Error && (e.name === 'QuotaExceededError' || errorCode === 22)) {
            logger.warn('[messageStore] LocalStorage quota exceeded on rehydration, using in-memory fallback')
            state.localStorageError = true
            state.inMemoryDrafts = new Map() // Initialize fallback
          }
        }
      },
      merge: (persistedState: unknown, currentState: MessageStore) => {
        const persisted = persistedState as {
          drafts?: Array<[string, MessageDraft]>
          localStorage_quota_percent?: number
        }
        return {
          ...currentState,
          drafts: new Map(persisted.drafts || []),
          localStorage_quota_percent: persisted.localStorage_quota_percent || 0,
        }
      },
    }
  )
)
