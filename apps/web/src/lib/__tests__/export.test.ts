/**
 * Tests for export utilities
 *
 * **Purpose:** Verify export functionality for JSON, YAML, and Markdown formats
 * **Context:** Reimplementation of HTMX/Alpine.js export functionality
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { exportTask, exportAndDownload, triggerDownload, type TaskData } from '../export'

// Mock DOM APIs
const mockCreateElement = vi.fn()
const mockCreateObjectURL = vi.fn()
const mockRevokeObjectURL = vi.fn()
const mockAppendChild = vi.fn()
const mockRemoveChild = vi.fn()
const mockClick = vi.fn()

describe('export utilities', () => {
  beforeEach(() => {
    // Setup DOM mocks
    global.document = {
      createElement: mockCreateElement,
      body: {
        appendChild: mockAppendChild,
        removeChild: mockRemoveChild,
      },
    } as unknown as Document

    global.URL = {
      createObjectURL: mockCreateObjectURL,
      revokeObjectURL: mockRevokeObjectURL,
    } as unknown as URL

    // Mock anchor element
    const mockAnchor = {
      href: '',
      download: '',
      click: mockClick,
    }
    mockCreateElement.mockReturnValue(mockAnchor)
    mockCreateObjectURL.mockReturnValue('blob:mock-url')
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  const mockTask: TaskData = {
    id: 'task-123',
    brief: 'Test task brief',
    status: 'complete',
    created_at: '2026-04-15T10:00:00Z',
    flow_config: '{"nodes": {}, "edges": {}}',
    error: undefined,
  }

  describe('exportTask', () => {
    it('should export task as JSON', () => {
      const result = exportTask(mockTask, 'json')

      expect(result.content).toContain('"id": "task-123"')
      expect(result.content).toContain('"brief": "Test task brief"')
      expect(result.filename).toMatch(/^task-task-123-\d+\.json$/)
      expect(result.mimeType).toBe('application/json')
    })

    it('should export task as YAML', () => {
      const result = exportTask(mockTask, 'yaml')

      expect(result.content).toContain('id: task-123')
      expect(result.content).toContain('brief: Test task brief')
      expect(result.filename).toMatch(/^task-task-123-\d+\.yaml$/)
      expect(result.mimeType).toBe('text/yaml')
    })

    it('should export task as Markdown', () => {
      const result = exportTask(mockTask, 'markdown')

      expect(result.content).toContain('# Task Result')
      expect(result.content).toContain('**Task ID:** task-123')
      expect(result.content).toContain('## Brief')
      expect(result.content).toContain('Test task brief')
      expect(result.filename).toMatch(/^task-task-123-\d+\.md$/)
      expect(result.mimeType).toBe('text/markdown')
    })

    it('should include error section in Markdown when task has error', () => {
      const taskWithError = { ...mockTask, error: 'Something went wrong' }
      const result = exportTask(taskWithError, 'markdown')

      expect(result.content).toContain('## Error')
      expect(result.content).toContain('Something went wrong')
    })

    it('should include flow_config section in Markdown when present', () => {
      const result = exportTask(mockTask, 'markdown')

      expect(result.content).toContain('## Flow Config')
      expect(result.content).toContain('```json')
    })

    it('should throw error for unsupported format', () => {
      expect(() => exportTask(mockTask, 'xml' as any)).toThrow(
        'Unsupported export format: xml'
      )
    })
  })

  describe('triggerDownload', () => {
    it('should create blob and trigger download', () => {
      triggerDownload('test content', 'test.txt', 'text/plain')

      expect(mockCreateObjectURL).toHaveBeenCalled()
      expect(mockCreateElement).toHaveBeenCalledWith('a')
      expect(mockAppendChild).toHaveBeenCalled()
      expect(mockClick).toHaveBeenCalled()
      expect(mockRemoveChild).toHaveBeenCalled()
      expect(mockRevokeObjectURL).toHaveBeenCalledWith('blob:mock-url')
    })

    it('should set correct anchor attributes', () => {
      const mockAnchor = {
        href: '',
        download: '',
        click: mockClick,
      }
      mockCreateElement.mockReturnValue(mockAnchor)

      triggerDownload('test content', 'test.txt', 'text/plain')

      expect(mockAnchor.href).toBe('blob:mock-url')
      expect(mockAnchor.download).toBe('test.txt')
    })
  })

  describe('exportAndDownload', () => {
    it('should export and download in one step for JSON', () => {
      exportAndDownload(mockTask, 'json')

      expect(mockCreateObjectURL).toHaveBeenCalled()
      expect(mockClick).toHaveBeenCalled()
    })

    it('should export and download in one step for YAML', () => {
      exportAndDownload(mockTask, 'yaml')

      expect(mockCreateObjectURL).toHaveBeenCalled()
      expect(mockClick).toHaveBeenCalled()
    })

    it('should export and download in one step for Markdown', () => {
      exportAndDownload(mockTask, 'markdown')

      expect(mockCreateObjectURL).toHaveBeenCalled()
      expect(mockClick).toHaveBeenCalled()
    })

    it('should throw error and log for invalid format', () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

      expect(() => exportAndDownload(mockTask, 'xml' as any)).toThrow()
      expect(consoleSpy).toHaveBeenCalled()

      consoleSpy.mockRestore()
    })
  })

  describe('Markdown rendering', () => {
    it('should format dates correctly in Markdown', () => {
      const result = exportTask(mockTask, 'markdown')

      expect(result.content).toContain('**Created:**')
      expect(result.content).toContain('6:00:00 AM')
    })

    it('should handle missing optional fields in Markdown', () => {
      const minimalTask: TaskData = {
        id: 'task-456',
        brief: 'Minimal task',
        status: 'pending',
        created_at: '',
      }

      const result = exportTask(minimalTask, 'markdown')

      expect(result.content).toContain('**Task ID:** task-456')
      expect(result.content).toContain('N/A') // For missing created_at
    })
  })
})
