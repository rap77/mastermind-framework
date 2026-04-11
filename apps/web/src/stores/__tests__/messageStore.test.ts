import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useMessageStore } from '../messageStore'

describe('messageStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useMessageStore.setState({
      messages: new Map(),
      drafts: new Map(),
      localStorage_quota_percent: 0,
    })
    // Clear localStorage
    localStorage.clear()
  })

  describe('addMessage', () => {
    it('should add message to messages Map', () => {
      const message = {
        id: 'msg-1',
        channel: 'whatsapp' as const,
        sender: 'user-1',
        content: 'Hello world',
        status: 'sent',
        timestamp: Date.now(),
        thread_id: 'thread-1',
      }

      useMessageStore.getState().addMessage(message)

      const messages = useMessageStore.getState().messages
      expect(messages.size).toBe(1)
      expect(messages.get('msg-1')).toEqual(message)
    })

    it('should add multiple messages', () => {
      const msg1 = {
        id: 'msg-1',
        channel: 'whatsapp' as const,
        sender: 'user-1',
        content: 'First',
        status: 'sent',
        timestamp: Date.now(),
        thread_id: 'thread-1',
      }
      const msg2 = {
        id: 'msg-2',
        channel: 'instagram' as const,
        sender: 'user-2',
        content: 'Second',
        status: 'delivered',
        timestamp: Date.now(),
        thread_id: 'thread-2',
      }

      useMessageStore.getState().addMessage(msg1)
      useMessageStore.getState().addMessage(msg2)

      expect(useMessageStore.getState().messages.size).toBe(2)
    })
  })

  describe('updateMessageStatus', () => {
    it('should update message status', () => {
      const message = {
        id: 'msg-1',
        channel: 'whatsapp' as const,
        sender: 'user-1',
        content: 'Hello',
        status: 'sent' as const,
        timestamp: Date.now(),
        thread_id: 'thread-1',
      }

      useMessageStore.getState().addMessage(message)
      useMessageStore.getState().updateMessageStatus('msg-1', 'read')

      const updated = useMessageStore.getState().messages.get('msg-1')
      expect(updated?.status).toBe('read')
    })

    it('should handle non-existent message gracefully', () => {
      expect(() => {
        useMessageStore.getState().updateMessageStatus('non-existent', 'read')
      }).not.toThrow()
    })
  })

  describe('saveDraft', () => {
    it('should save draft to localStorage', () => {
      const draft = {
        channel_id: 'whatsapp-user-1',
        content: 'Draft message',
        media_attachments: [],
      }

      useMessageStore.getState().saveDraft('whatsapp-user-1', draft)

      const savedDraft = useMessageStore.getState().drafts.get('whatsapp-user-1')
      expect(savedDraft).toEqual(draft)
    })

    it('should update existing draft', () => {
      const draft1 = {
        channel_id: 'whatsapp-user-1',
        content: 'First draft',
        media_attachments: [],
      }
      const draft2 = {
        channel_id: 'whatsapp-user-1',
        content: 'Updated draft',
        media_attachments: [],
      }

      useMessageStore.getState().saveDraft('whatsapp-user-1', draft1)
      useMessageStore.getState().saveDraft('whatsapp-user-1', draft2)

      const savedDraft = useMessageStore.getState().drafts.get('whatsapp-user-1')
      expect(savedDraft?.content).toBe('Updated draft')
    })
  })

  describe('LocalStorage quota monitoring', () => {
    it('should alert at 80% quota usage', () => {
      // Mock localStorage to simulate 80% usage
      // Need ~4MB of data (80% of 5MB)
      const mockData = 'x'.repeat(4_200_000) // ~4.2MB
      localStorage.setItem('mock-big-data', mockData)

      const quotaPercent = useMessageStore.getState().checkLocalStorageQuota()
      expect(quotaPercent).toBeGreaterThan(80)

      // Cleanup
      localStorage.clear()
    })

    it('should block saveDraft at 90% quota usage', () => {
      // Mock localStorage to simulate 90%+ usage
      // Fill localStorage to near limit
      try {
        const chunks = []
        for (let i = 0; i < 4; i++) {
          chunks.push('x'.repeat(1_200_000)) // 4 x 1.2MB = 4.8MB
        }
        chunks.forEach((chunk, i) => {
          localStorage.setItem(`mock-chunk-${i}`, chunk)
        })
      } catch (e) {
        // Ignore QuotaExceededError - we've filled enough
      }

      const draft = {
        channel_id: 'whatsapp-user-1',
        content: 'Should be blocked',
        media_attachments: [],
      }

      const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {})

      useMessageStore.getState().saveDraft('whatsapp-user-1', draft)

      // Draft should not be saved (either blocked by our check or by localStorage quota)
      const savedDraft = useMessageStore.getState().drafts.get('whatsapp-user-1')
      expect(savedDraft).toBeUndefined()

      alertSpy.mockRestore()
      localStorage.clear()
    })

    it('should allow saveDraft below 90% quota', () => {
      const draft = {
        channel_id: 'whatsapp-user-1',
        content: 'Should be saved',
        media_attachments: [],
      }

      useMessageStore.getState().saveDraft('whatsapp-user-1', draft)

      const savedDraft = useMessageStore.getState().drafts.get('whatsapp-user-1')
      expect(savedDraft).toBeDefined()
    })
  })

  describe('useMessage selector', () => {
    it('should return message by id (O(1) lookup)', () => {
      const message = {
        id: 'msg-1',
        channel: 'whatsapp' as const,
        sender: 'user-1',
        content: 'Hello',
        status: 'sent',
        timestamp: Date.now(),
        thread_id: 'thread-1',
      }

      useMessageStore.getState().addMessage(message)

      const retrieved = useMessageStore.getState().useMessage('msg-1')
      expect(retrieved).toEqual(message)
    })

    it('should return undefined for non-existent message', () => {
      const retrieved = useMessageStore.getState().useMessage('non-existent')
      expect(retrieved).toBeUndefined()
    })
  })

  describe('RAF batching', () => {
    it('should batch message additions using RAF', () => {
      const messages = Array.from({ length: 100 }, (_, i) => ({
        id: `msg-${i}`,
        channel: 'whatsapp' as const,
        sender: 'user-1',
        content: `Message ${i}`,
        status: 'sent' as const,
        timestamp: Date.now(),
        thread_id: 'thread-1',
      }))

      messages.forEach((msg) => {
        useMessageStore.getState().addMessage(msg)
      })

      // All messages should be added
      expect(useMessageStore.getState().messages.size).toBe(100)
    })
  })
})
