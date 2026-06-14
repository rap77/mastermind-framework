import fs from 'node:fs'
import path from 'node:path'
import vm from 'node:vm'

import { beforeEach, describe, expect, it, vi } from 'vitest'

type DashboardState = {
  exportTask(taskId: string, format: 'json' | 'yaml' | 'markdown'): Promise<void>
  _renderMarkdown(task: Record<string, unknown>): string
  addLog(level: string, message: string): void
  logs: Array<{ id: number; level: string; message: string }>
}

function loadDashboardFactory(): () => DashboardState {
  const dashboardPath = path.resolve(
    process.cwd(),
    '../api/mastermind_cli/web/static/js/dashboard.js',
  )
  const source = fs.readFileSync(dashboardPath, 'utf8')
  const context = vm.createContext(globalThis)
  vm.runInContext(`${source}\n;globalThis.__dashboardFactory = dashboard;`, context)
  return (globalThis as typeof globalThis & { __dashboardFactory: () => DashboardState })
    .__dashboardFactory
}

describe('legacy dashboard exportTask', () => {
  const dashboardFactory = loadDashboardFactory()

  const fetchMock = vi.fn()
  const dumpMock = vi.fn()
  const createObjectURLMock = vi.fn(() => 'blob:test-url')
  const revokeObjectURLMock = vi.fn()
  const appendChildMock = vi.fn()
  const removeChildMock = vi.fn()

  let capturedBlob: Blob | null = null
  let anchor: {
    href: string
    download: string
    click: ReturnType<typeof vi.fn>
  }

  beforeEach(() => {
    vi.clearAllMocks()

    capturedBlob = null
    anchor = {
      href: '',
      download: '',
      click: vi.fn(),
    }

    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({
        id: 'task-123',
        status: 'completed',
        created_at: '2026-06-13T12:00:00Z',
        brief: 'Export this task',
        flow_config: '{"mode":"deep"}',
        error: 'none',
      }),
    })

    dumpMock.mockReturnValue('status: completed\nbrief: Export this task\n')

    vi.stubGlobal('fetch', fetchMock)
    vi.stubGlobal('authStore', () => ({
      getAuthHeaders: () => ({ Authorization: 'Bearer test-token' }),
    }))
    vi.stubGlobal('jsyaml', {
      dump: dumpMock,
    })
    vi.stubGlobal('Blob', class MockBlob {
      parts: unknown[]
      type: string

      constructor(parts: unknown[], options?: { type?: string }) {
        this.parts = parts
        this.type = options?.type ?? ''
        capturedBlob = this as unknown as Blob
      }
    })
    vi.stubGlobal('URL', {
      createObjectURL: createObjectURLMock,
      revokeObjectURL: revokeObjectURLMock,
    })
    vi.stubGlobal('document', {
      body: {
        appendChild: appendChildMock,
        removeChild: removeChildMock,
      },
      createElement: vi.fn(() => anchor),
    })
    vi.stubGlobal('console', {
      error: vi.fn(),
    })
  })

  it('exports the fetched task as JSON in the browser', async () => {
    const dashboard = dashboardFactory()

    await dashboard.exportTask('task-123', 'json')

    expect(fetchMock).toHaveBeenCalledWith('/api/tasks/task-123', {
      headers: { Authorization: 'Bearer test-token' },
    })
    expect(createObjectURLMock).toHaveBeenCalledTimes(1)
    expect(anchor.download).toMatch(/^task-task-123-\d+\.json$/)
    expect(anchor.click).toHaveBeenCalledTimes(1)
    expect(revokeObjectURLMock).toHaveBeenCalledWith('blob:test-url')

    const blob = capturedBlob as unknown as { parts: string[]; type: string }
    expect(blob.type).toBe('application/json')
    expect(blob.parts[0]).toContain('"id": "task-123"')
    expect(blob.parts[0]).toContain('"brief": "Export this task"')
  })

  it('exports the fetched task as YAML in the browser', async () => {
    const dashboard = dashboardFactory()

    await dashboard.exportTask('task-123', 'yaml')

    expect(dumpMock).toHaveBeenCalledWith(
      expect.objectContaining({
        id: 'task-123',
        status: 'completed',
      }),
      {
        indent: 2,
        lineWidth: -1,
        sortKeys: false,
      },
    )
    expect(anchor.download).toMatch(/^task-task-123-\d+\.yaml$/)

    const blob = capturedBlob as unknown as { parts: string[]; type: string }
    expect(blob.type).toBe('text/yaml')
    expect(blob.parts[0]).toBe('status: completed\nbrief: Export this task\n')
  })

  it('exports the fetched task as Markdown in the browser', async () => {
    const dashboard = dashboardFactory()

    await dashboard.exportTask('task-123', 'markdown')

    expect(anchor.download).toMatch(/^task-task-123-\d+\.md$/)

    const blob = capturedBlob as unknown as { parts: string[]; type: string }
    expect(blob.type).toBe('text/markdown')
    expect(blob.parts[0]).toContain('# Task Result')
    expect(blob.parts[0]).toContain('**Task ID:** task-123')
    expect(blob.parts[0]).toContain('## Brief')
    expect(blob.parts[0]).toContain('Export this task')
    expect(blob.parts[0]).toContain('## Flow Config')
  })
})
