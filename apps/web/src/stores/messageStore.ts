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
        // Check localStorage quota before saving
        const quotaPercent = get().checkLocalStorageQuota()

        // Alert at 80%
        if (quotaPercent > 80 && quotaPercent <= 90) {
          console.warn(`localStorage quota at ${quotaPercent.toFixed(1)}% - approaching limit`)
          // Could show toast notification here
        }

        // Block at 90%
        if (quotaPercent > 90) {
          console.error(`localStorage quota at ${quotaPercent.toFixed(1)}% - cannot save draft`)
          alert('LocalStorage quota exceeded. Please clear old messages to continue.')
          return
        }

        set((state) => {
          state.drafts.set(channelId, draft)
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
    })),
    {
      name: 'mastermind-messages',
      partialize: (state) => ({
        drafts: Array.from(state.drafts.entries()), // Persist only drafts
        localStorage_quota_percent: state.localStorage_quota_percent,
      }),
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
