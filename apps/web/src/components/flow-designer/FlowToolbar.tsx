/**
 * FlowToolbar — Toolbar with zoom, export, import, clear actions
 *
 * **Features:**
 * - Zoom controls (zoom in, zoom out, fit view)
 * - Export flow to JSON file
 * - Import flow from JSON file
 * - Clear all nodes and edges from canvas
 * - Simulate button (links to Simulation page)
 * - Confirmation dialogs for destructive actions
 * - Loading states for async operations
 * - Error handling with toast notifications
 *
 * **Actions:**
 * - `zoomIn`: Zoom in the canvas (incremental)
 * - `zoomOut`: Zoom out the canvas (incremental)
 * - `fitView`: Fit all nodes in the viewport
 * - `exportFlow`: Export current flow to JSON file
 * - `importFlow`: Import flow from JSON file (with validation)
 * - `clearFlow`: Remove all nodes and edges (requires confirmation)
 * - `simulate`: Navigate to Simulation page (if flow has nodes)
 *
 * **File Size Limit:** 5MB for JSON import (prevents performance issues)
 *
 * @see flow-serializer - Export/import logic
 * @see toastError - Error notification system
 */

import { useCallback, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useReactFlow } from '@xyflow/react'
import { toastError } from '@/lib/toast'
import { exportFlowToFile, importFlow } from '@/lib/flow-serializer'
import { useFlowDesignerStore } from '@/stores/flowDesignerStore'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

// File size limit for JSON import (5MB)
const MAX_JSON_FILE_SIZE = 5 * 1024 * 1024

export function FlowToolbar() {
  const router = useRouter()
  const { zoomIn, zoomOut, fitView } = useReactFlow()
  const { nodes, edges, clearFlow } = useFlowDesignerStore()
  const [isClearDialogOpen, setIsClearDialogOpen] = useState(false)
  const [isNavigating, setIsNavigating] = useState(false)
  const [isImporting, setIsImporting] = useState(false)

  const handleExport = useCallback(() => {
    const flow = {
      id: 'flow-1',
      name: 'My Flow',
      nodes,
      edges,
    }
    exportFlowToFile(flow)
  }, [nodes, edges])

  const handleImport = useCallback(() => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = 'application/json'

    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (!file) return

      // Validate file size
      if (file.size > MAX_JSON_FILE_SIZE) {
        toastError(
          `File too large. Maximum size is ${MAX_JSON_FILE_SIZE / 1024 / 1024}MB`
        )
        return
      }

      // Validate file type
      if (!file.name.endsWith('.json') && file.type !== 'application/json') {
        toastError('Invalid file type. Please select a JSON file.')
        return
      }

      setIsImporting(true)
      const reader = new FileReader()
      reader.onload = (event) => {
        try {
          const json = event.target?.result as string
          const flow = importFlow(json)
          useFlowDesignerStore.getState().loadFlow(flow)
        } catch (error) {
          toastError('Failed to parse JSON file. Please check the file format.')
          console.error('Import failed:', error)
        } finally {
          setIsImporting(false)
        }
      }
      reader.readAsText(file)
    }

    input.click()
  }, [])

  const handleClear = useCallback(() => {
    setIsClearDialogOpen(true)
  }, [])

  const handleConfirmClear = useCallback(() => {
    clearFlow()
    setIsClearDialogOpen(false)
  }, [clearFlow])

  const handleCancelClear = useCallback(() => {
    setIsClearDialogOpen(false)
  }, [])

  const handleSimulate = useCallback(async () => {
    // Navigate to simulation page
    // The current flow state is automatically available in the store
    try {
      setIsNavigating(true)
      await router.push('/simulation')
    } catch (error) {
      // Router not available (e.g., in test environment)
      toastError('Failed to open simulation. Please try again.')
      console.warn('Router not available:', error)
    } finally {
      setIsNavigating(false)
    }
  }, [router])

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
        onClick={handleSimulate}
        disabled={isNavigating}
        className="px-3 py-1 rounded text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        style={{
          backgroundColor: 'var(--color-success)',
          color: 'var(--color-success-foreground)',
        }}
      >
        {isNavigating ? (
          <span className="flex items-center gap-2">
            <LoadingSpinner size="sm" />
            Loading...
          </span>
        ) : (
          'Simulate'
        )}
      </button>

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
        disabled={isImporting}
        className="px-3 py-1 rounded text-sm transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        style={{
          backgroundColor: 'var(--color-surface)',
          color: 'var(--color-text-primary)',
          border: '1px solid var(--color-border)',
        }}
      >
        {isImporting ? (
          <span className="flex items-center gap-2">
            <LoadingSpinner size="sm" />
            Importing...
          </span>
        ) : (
          'Import JSON'
        )}
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

      <Dialog open={isClearDialogOpen} onOpenChange={setIsClearDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clear Flow</DialogTitle>
            <DialogDescription>
              Are you sure you want to clear the flow? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={handleCancelClear}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleConfirmClear}>
              Clear
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
