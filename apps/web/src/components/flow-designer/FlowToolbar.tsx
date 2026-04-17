/**
 * FlowToolbar — Toolbar with zoom, export, import, clear actions
 *
 * Top toolbar for the Flow Designer with common actions.
 */

import { useCallback } from 'react'
import { useReactFlow } from '@xyflow/react'
import { exportFlow, importFlow } from '@/lib/flow-serializer'
import { useFlowDesignerStore } from '@/stores/flowDesignerStore'

export function FlowToolbar() {
  const { zoomIn, zoomOut, fitView } = useReactFlow()
  const { nodes, edges, clearFlow } = useFlowDesignerStore()

  const handleExport = useCallback(() => {
    const flow = {
      id: 'flow-1',
      name: 'My Flow',
      nodes,
      edges,
    }

    try {
      const json = exportFlow(flow)
      const blob = new Blob([json], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `flow-${Date.now()}.json`
      a.click()
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Export failed:', error)
    }
  }, [nodes, edges])

  const handleImport = useCallback(() => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'application/json'

    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (!file) return

      const reader = new FileReader()
      reader.onload = (event) => {
        try {
          const json = event.target?.result as string
          const flow = importFlow(json)
          useFlowDesignerStore.getState().loadFlow(flow)
        } catch (error) {
          console.error('Import failed:', error)
        }
      }
      reader.readAsText(file)
    }

    input.click()
  }, [])

  const handleClear = useCallback(() => {
    if (confirm('Are you sure you want to clear the flow?')) {
      clearFlow()
    }
  }, [clearFlow])

  return (
    <div
      className="flex items-center gap-2 px-4 py-2 border-b"
      style={{
        backgroundColor: 'var(--color-surface)',
        borderColor: 'var(--color-border)',
      }}
    >
      <button
        onClick={() => zoomIn({ duration: 300 })}
        className="px-3 py-1 rounded text-sm"
        style={{
          backgroundColor: 'var(--color-surface)',
          color: 'var(--color-text-primary)',
          border: '1px solid var(--color-border)',
        }}
      >
        Zoom In
      </button>

      <button
        onClick={() => zoomOut({ duration: 300 })}
        className="px-3 py-1 rounded text-sm"
        style={{
          backgroundColor: 'var(--color-surface)',
          color: 'var(--color-text-primary)',
          border: '1px solid var(--color-border)',
        }}
      >
        Zoom Out
      </button>

      <button
        onClick={() => fitView({ padding: 0.2, duration: 300 })}
        className="px-3 py-1 rounded text-sm"
        style={{
          backgroundColor: 'var(--color-surface)',
          color: 'var(--color-text-primary)',
          border: '1px solid var(--color-border)',
        }}
      >
        Fit View
      </button>

      <div className="flex-1" />

      <button
        onClick={handleExport}
        className="px-3 py-1 rounded text-sm"
        style={{
          backgroundColor: 'var(--color-primary)',
          color: 'var(--color-primary-foreground)',
        }}
      >
        Export JSON
      </button>

      <button
        onClick={handleImport}
        className="px-3 py-1 rounded text-sm"
        style={{
          backgroundColor: 'var(--color-surface)',
          color: 'var(--color-text-primary)',
          border: '1px solid var(--color-border)',
        }}
      >
        Import JSON
      </button>

      <button
        onClick={handleClear}
        className="px-3 py-1 rounded text-sm"
        style={{
          backgroundColor: 'var(--color-destructive)',
          color: 'var(--color-destructive-foreground)',
        }}
      >
        Clear
      </button>
    </div>
  )
}
