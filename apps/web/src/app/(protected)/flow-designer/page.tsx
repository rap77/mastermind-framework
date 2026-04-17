/**
 * Flow Designer Route — n8n-style node-based flow editor
 *
 * Main page for the Flow Designer feature.
 * Layout: Palette (left) | Canvas (center) | Toolbar (top)
 *
 * Features:
 * - Drag-and-drop node creation
 * - Visual flow editing with React Flow v12
 * - Export/Import JSON
 * - Zoom/pan controls
 * - Minimap for navigation
 */

'use client'

import { FlowDesignerCanvas } from '@/components/flow-designer/FlowDesignerCanvas'
import { FlowPalette } from '@/components/flow-designer/FlowPalette'
import { FlowToolbar } from '@/components/flow-designer/FlowToolbar'

export default function FlowDesignerPage() {
  return (
    <div className="flex flex-col h-screen bg-[var(--color-background)]">
      {/* Top toolbar */}
      <FlowToolbar />

      {/* Main content area: palette + canvas */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left sidebar: Node palette */}
        <FlowPalette />

        {/* Center: Flow canvas */}
        <FlowDesignerCanvas />
      </div>
    </div>
  )
}
